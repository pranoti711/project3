# ============================================================================
# 10_spatial_checks.R  -  spatial robustness
#   (a) spatial-block CV: counties are clustered into k geographic blocks (k-means
#       on centroids); each block is held out entirely and predicted from the rest.
#   (b) Moran's I of out-of-sample residuals (from 06) by test year and model:
#       leftover spatial structure means the spatial term is not capturing it all.
#
# Run: Rscript 04_scripts/10_spatial_checks.R     Options: --k=6 --models=A,B,C,D
# Needs: 06_models_ABCD.R already run (for part b).
# Outputs: 05_results/tables/spatial_block_cv.csv, spatial_block_delta.csv,
#          residual_moran.csv, county_blocks.csv
# ============================================================================
.here <- function() {
  a <- commandArgs(FALSE); f <- sub("^--file=", "", a[grepl("^--file=", a)])
  if (length(f)) return(dirname(normalizePath(f)))
  for (p in c("04_scripts", "project3/04_scripts")) if (dir.exists(p)) return(normalizePath(p))
  stop("cd to project3 first")
}
source(file.path(.here(), "p3_common.R"))

k <- as.integer(get_arg("k", 6))
models <- union("A", strsplit(get_arg("models", "A,B,C,D"), ",")[[1]])
tb <- prep_table(); dat <- tb$dt; g <- tb$graph

# ---------------------------------------------------------- (a) block CV
set.seed(11)
km <- kmeans(scale(g$centroid), centers = k, nstart = 25)
blocks <- km$cluster                      # indexed by county_id (graph order)
fwrite(data.table(fips = g$fips, county = g$name, block = blocks), file.path(P$tables, "county_blocks.csv"))
dat[, block := blocks[county_id]]

rows <- list()
for (b in sort(unique(dat$block))) {
  test_idx <- which(dat$block == b)
  if (sum(dat$up[test_idx]) < 5) { message("block ", b, " skipped (few events)"); next }
  for (m in models) {
    t0 <- Sys.time()
    p <- tryCatch(fit_predict(dat, test_idx, m, g$file, pooled = FALSE),
                  error = function(e) { message("fit failed block ", b, " ", m, ": ", conditionMessage(e)); NULL })
    if (is.null(p)) next
    y <- dat$up[test_idx]
    rows[[length(rows) + 1]] <- data.table(block = b, n_counties = uniqueN(dat$county[test_idx]), model = m,
                                           n = length(y), events = sum(y),
                                           auc = auc_strat(y, p, dat$year[test_idx], dat$disease[test_idx]),
                                           auc_pooled = auc(y, p), brier = brier(y, p), logloss = logloss(y, p))
    message(sprintf("block %d model %s (%.0fs)", b, m, as.numeric(difftime(Sys.time(), t0, units = "secs"))))
  }
}
bcv <- rbindlist(rows)
if (!nrow(bcv)) {
  stop("Spatial block validation produced no successful fits. See the fit diagnostics above.")
}
fwrite(bcv, file.path(P$tables, "spatial_block_cv.csv"))
w <- dcast(bcv, block + n_counties ~ model, value.var = "auc")
for (m in setdiff(models, "A")) if (m %in% names(w)) w[[paste0("d", m)]] <- w[[m]] - w$A
fwrite(w, file.path(P$tables, "spatial_block_delta.csv"))
cat("\n=== Spatial-block CV: AUC per held-out block ===\n"); print(w)
for (m in setdiff(models, "A")) {
  d <- w[[paste0("d", m)]]; d <- d[!is.na(d)]
  if (length(d)) cat(sprintf("model %s vs A: improved in %d of %d blocks, mean dAUC = %.4f\n", m, sum(d > 0), length(d), mean(d)))
}

# ----------------------------------------------- (b) residual Moran's I
oof_path <- file.path(P$tables, "oof_predictions_lfo.csv")
if (!file.exists(oof_path)) {
  message("oof_predictions_lfo.csv not found; run 06_models_ABCD.R for the Moran's I part.")
} else {
  oof <- fread(oof_path)
  oof[, fips := sprintf("%05d", as.integer(fips))]
  moran_one <- function(vals, fp) {
    ok <- !is.na(vals); vals <- vals[ok]; fp <- fp[ok]
    if (length(vals) < 10 || sd(vals) == 0) return(c(I = NA, p = NA))
    keep <- g$fips %in% fp
    nb <- if (all(keep)) g$nb else spdep::subset.nb(g$nb, keep)
    ord <- match(g$fips[keep], fp)
    lw <- spdep::nb2listw(nb, style = "W", zero.policy = TRUE)
    mt <- tryCatch(spdep::moran.test(vals[ord], lw, zero.policy = TRUE, alternative = "greater"), error = function(e) NULL)
    if (is.null(mt)) return(c(I = NA, p = NA))
    c(I = unname(mt$estimate[1]), p = mt$p.value)
  }
  by_year <- oof[, .(r = mean(up - p)), by = .(model, year, fips)]
  m1 <- by_year[, as.list(moran_one(r, fips)), by = .(model, year)][, scope := "residual_by_year"]
  by_all <- oof[, .(r = mean(up - p)), by = .(model, fips)]
  m2 <- by_all[, as.list(moran_one(r, fips)), by = .(model)][, `:=`(year = NA_integer_, scope = "residual_pooled")]
  raw <- oof[model == "A", .(r = mean(up)), by = .(year, fips)]
  m3 <- raw[, as.list(moran_one(r, fips)), by = .(year)][, `:=`(model = "outcome_rate", scope = "raw_outcome")]
  mor <- rbind(m1, m2, m3, fill = TRUE)
  fwrite(mor, file.path(P$tables, "residual_moran.csv"))
  cat("\n=== Moran's I of out-of-sample residuals (positive and small p = leftover spatial pattern) ===\n")
  print(mor[scope != "residual_by_year"])
  cat("\nIf model D residuals show clear spatial clustering while A does not, mortality may be adding noise\n",
      "with its own spatial structure; check that before interpreting B/D gains.\n")
}
