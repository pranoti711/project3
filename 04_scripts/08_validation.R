# ============================================================================
# 08_validation.R  -  leave-one-disease-out (LODO) and leave-one-group-out (LOGO)
#
# Does a mortality signal learned on OTHER diseases/groups transfer to a disease
# or group the model has never seen?  Pooled (not group-specific) mortality
# coefficients are used, otherwise a held-out group would have no coefficient.
#
# Caveat: all years are used (this tests transfer across diseases, not forecasting;
# 06 does the forecasting test). Year effects are shared across diseases, so a
# common year shock can help every model; compare B/C/D to A, not to 0.5.
#
# Run: Rscript 04_scripts/08_validation.R        Option: --models=A,B,D (faster)
# Outputs: 05_results/tables/validation_lodo.csv, validation_logo.csv,
#          validation_summary.csv
# ============================================================================
.here <- function() {
  a <- commandArgs(FALSE); f <- sub("^--file=", "", a[grepl("^--file=", a)])
  if (length(f)) return(dirname(normalizePath(f)))
  for (p in c("04_scripts", "project3/04_scripts")) if (dir.exists(p)) return(normalizePath(p))
  stop("cd to project3 first")
}
source(file.path(.here(), "p3_common.R"))

models <- union("A", strsplit(get_arg("models", "A,B,C,D"), ",")[[1]])
tb <- prep_table(); dat <- tb$dt; g <- tb$graph

run_holdout <- function(unit_col) {
  units <- sort(unique(dat[[unit_col]]))
  rows <- list()
  for (u in units) {
    test_idx <- which(dat[[unit_col]] == u)
    if (sum(dat$up[test_idx]) < 5 || sum(1 - dat$up[test_idx]) < 5) {
      message("skip ", u, " (too few events/non-events)"); next
    }
    for (m in models) {
      t0 <- Sys.time()
      p <- tryCatch(fit_predict(dat, test_idx, m, g$file, pooled = TRUE), error = function(e) { message("fit failed: ", u, " ", m, ": ", conditionMessage(e)); NULL })
      if (is.null(p)) next
      y <- dat$up[test_idx]
      rows[[length(rows) + 1]] <- data.table(
        unit_type = unit_col, unit = u,
        group = dat$group[test_idx][1], model = m, n = length(y), events = sum(y),
        auc = auc_strat(y, p, dat$year[test_idx], dat$disease[test_idx]), auc_pooled = auc(y, p),
        brier = brier(y, p), logloss = logloss(y, p))
      message(sprintf("%s=%s model %s (%.0fs)", unit_col, u, m, as.numeric(difftime(Sys.time(), t0, units = "secs"))))
    }
  }
  rbindlist(rows)
}

lodo <- run_holdout("disease")
logo <- run_holdout("group")
if (!nrow(lodo) || !nrow(logo)) {
  stop("Validation produced no successful holdout fits. See the fit diagnostics above.")
}
fwrite(lodo, file.path(P$tables, "validation_lodo.csv"))
fwrite(logo, file.path(P$tables, "validation_logo.csv"))

delta <- function(x) {
  w <- dcast(x, unit_type + unit + group ~ model, value.var = "auc")
  for (m in setdiff(models, "A")) if (m %in% names(w)) w[[paste0("d", m)]] <- w[[m]] - w$A
  w
}
dl <- delta(lodo); dg <- delta(logo)

summ <- function(w, label) {
  rbindlist(lapply(setdiff(models, "A"), function(m) {
    d <- w[[paste0("d", m)]]; d <- d[!is.na(d)]
    if (!length(d)) return(NULL)
    data.table(scheme = label, model = m, n_units = length(d), mean_delta_auc = mean(d),
               median_delta_auc = median(d), n_improved = sum(d > 0),
               sign_test_p = if (length(d) >= 4) binom.test(sum(d > 0), length(d), 0.5, alternative = "greater")$p.value else NA_real_)
  }))
}
sm <- rbind(summ(dl, "leave-one-disease-out"), summ(dg, "leave-one-group-out"))
fwrite(sm, file.path(P$tables, "validation_summary.csv"))
fwrite(dl, file.path(P$tables, "validation_lodo_delta.csv")); fwrite(dg, file.path(P$tables, "validation_logo_delta.csv"))

cat("\n=== Held-out transfer: AUC gain over model A ===\n"); print(sm)
cat("\nPer-disease gains for B (mortality):\n"); if ("dB" %in% names(dl)) print(dl[order(-dB), .(unit, group, A, B, dB)])
cat("\nIf mortality helps only inside one group and fails on held-out groups, say so: that is a group-specific\n",
    "association, not a general cross-domain signal.\n")
