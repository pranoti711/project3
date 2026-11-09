# ============================================================================
# p3_common.R  -  shared helpers for 06_models_ABCD.R, 07, 08, 10
# Project 3: mortality -> infectious-disease up-transitions, California counties
#
# INPUT CONTRACT (edit the lists below if your 05_transitions output differs):
#   02_data/processed/model_table.csv  - one row per county x year x disease
#     required: county, fips (or county name matching Census NAME), year,
#               disease, group, up
#       up = 1 if disease d in county i makes an UP-transition between t and t+1,
#            0 if not, NA if undefined. All features must be known at time t.
#     own-history (HIST): lag_rate, trend_slope, prev_up, pop_log
#     mortality   (MORT): allcause_dev, drug_od_dev, suicide_dev, homicide_dev
#     context     (CTX) : aqi_median, drought_dsci
#   Columns that are absent are skipped with a message.
#
# LEAKAGE WARNING: if trend_slope (or any HIST feature) came from a model fitted
# on ALL years (e.g. a smoother using future data), the leave-future-out scores
# are optimistic. The feature at year t must use data up to year t only.
# ============================================================================

suppressPackageStartupMessages({
  library(data.table)
  library(INLA)
  library(sf)
  library(spdep)
})

find_root <- function() {
  p <- normalizePath(getwd())
  for (i in 1:5) {
    if (dir.exists(file.path(p, "04_scripts"))) return(p)
    if (dir.exists(file.path(p, "project3", "04_scripts"))) return(file.path(p, "project3"))
    p <- dirname(p)
  }
  stop("Run from inside the project3 folder (or its parent).")
}
ROOT <- find_root()
P <- list(
  model_table = file.path(ROOT, "02_data", "processed", "model_table.csv"),
  tables  = file.path(ROOT, "05_results", "tables"),
  figs    = file.path(ROOT, "05_results", "figures"),
  interim = file.path(ROOT, "02_data", "interim"),
  geo_raw = file.path(ROOT, "02_data", "raw", "geography")
)
for (d in c(P$tables, P$figs, P$interim)) dir.create(d, showWarnings = FALSE, recursive = TRUE)

get_arg <- function(name, default) {
  a <- commandArgs(TRUE)
  hit <- a[startsWith(a, paste0("--", name, "="))]
  if (length(hit)) sub(paste0("--", name, "="), "", hit[1]) else default
}

# CHANGED (v2): population is now part of the baseline (HIST) so that B and C are judged against a
# model that already knows county size. Mortality enters as lagged within-county deviations
# (built by 05b_build_model_table.py), not as levels. physicians_per_100k is dropped from CTX
# because it is ~96% missing (it was a constant after zero-filling).
HIST <- c("lag_rate", "trend_slope", "prev_up", "pop_log")
MORT <- c("allcause_dev", "drug_od_dev", "suicide_dev", "homicide_dev")
CTX  <- c("aqi_median", "drought_dsci")

# STAGE 2 (exploratory, see 00_docs/13_stage2_plan.md). Set the environment variable P3_STAGE2=1 to add the
# neighbour-county and static socioeconomic features built by 05c_add_stage2_features.py. Neighbour-county
# mortality gets ONE pooled slope (names start with "nbr_"); own mortality keeps group-specific slopes.
# Optional columns that do not exist (poverty_l1, unemp_l1) are skipped with a message.
if (identical(Sys.getenv("P3_STAGE2"), "1")) {
  MORT <- c(MORT, "nbr_allcause_dev", "nbr_drug_od_dev", "nbr_suicide_dev", "nbr_homicide_dev")
  CTX  <- c(CTX, "nbr_lag_rate", "nbr_trend_slope", "nbr_prev_up",
            "urban_pct", "median_age", "log_density", "rural_urban", "poverty_l1", "unemp_l1")
  message("STAGE 2 features ON (exploratory)")
}

# STAGE 3 (exploratory, see 00_docs/17_stage3_plan.md). P3_STAGE3=1 replaces the mortality block with the
# cross-disease signature of the SAME county (model B) and puts the neighbour-county cross-disease signature in
# model C. Built by 05d_add_crossdisease_features.py. All these features get one pooled slope.
# Steps 07 (lead time) and 13 (confound check) still use mortality and are not meaningful in stage 3.
if (identical(Sys.getenv("P3_STAGE3"), "1")) {
  MORT <- c("xd_n_up", "xd_share_rising", "xd_share_rising_same", "xd_share_rising_other")
  CTX  <- c("nbr_xd_n_up", "nbr_xd_share_rising")
  message("STAGE 3 cross-disease features ON (exploratory)")
}

# ---------------------------------------------------------------- geography
get_graph <- function() {
  shp <- list.files(P$geo_raw, pattern = "\\.shp$", full.names = TRUE, recursive = TRUE)
  if (!length(shp)) {
    zp <- list.files(P$geo_raw, pattern = "\\.zip$", full.names = TRUE)
    if (!length(zp)) stop("No county shapefile or zip found in ", P$geo_raw)
    exdir <- file.path(P$interim, "geography")
    dir.create(exdir, showWarnings = FALSE, recursive = TRUE)
    unzip(zp[1], exdir = exdir)
    shp <- list.files(exdir, pattern = "\\.shp$", full.names = TRUE, recursive = TRUE)
  }
  g <- sf::st_read(shp[1], quiet = TRUE)
  g <- g[g$STATEFP == "06", ]
  g <- g[order(g$GEOID), ]
  g <- sf::st_transform(g, 4326)
  # snap = 0.01 degrees (~1 km) so coastal pairs such as SF / Marin are linked
  nb <- spdep::poly2nb(g, queen = TRUE, snap = 0.01)
  gfile <- file.path(P$interim, "ca_counties.graph")
  spdep::nb2INLA(gfile, nb)
  ctr <- suppressWarnings(sf::st_coordinates(sf::st_centroid(sf::st_geometry(g))))
  list(nb = nb, file = gfile, fips = g$GEOID, name = g$NAME, centroid = ctr)
}

# --------------------------------------------------------------------- data
prep_table <- function() {
  if (!file.exists(P$model_table)) {
    stop(
      "Required modeling input is missing: ", P$model_table,
      ". Build model_table.csv from the full transition output and leakage-safe ",
      "history, mortality, and context features before running model 06."
    )
  }
  dt <- fread(P$model_table)
  req <- c("county", "year", "disease", "group", "up")
  if (!all(req %in% names(dt))) stop("model_table.csv is missing: ", paste(setdiff(req, names(dt)), collapse = ", "))
  g <- get_graph()
  if ("fips" %in% names(dt)) {
    dt[, fips := sprintf("%05d", as.integer(fips))]
  } else {
    nm <- sub(" County$", "", dt$county)
    dt[, fips := g$fips[match(nm, g$name)]]
  }
  dt[, county_id := match(fips, g$fips)]
  if (anyNA(dt$county_id)) stop("Some rows have a county that is not a California county in the shapefile.")
  dt <- dt[!is.na(up)]
  dt[, group := make.names(group)]
  dt[, disease_id := as.integer(factor(disease))]
  dt[, year_id := as.integer(year - min(year) + 1L)]
  need_new <- setdiff(MORT, names(dt))
  if (length(need_new)) stop("model table lacks ", paste(need_new, collapse = ", "),
    ". Rebuild it: python 04_scripts/05b_build_model_table.py --outcome=upcross_local_0.80 --output=02_data/processed/model_table_local.csv (stage 2 columns: python 04_scripts/05c_add_stage2_features.py)")
  absent <- setdiff(c(HIST, MORT, CTX), names(dt))
  if (length(absent)) message("Skipping absent columns: ", paste(absent, collapse = ", "))
  message("Rows: ", nrow(dt), " | diseases: ", uniqueN(dt$disease), " | event rate: ", round(mean(dt$up), 4))
  message("REMINDER: HIST features at year t must use data up to t only (see header).")
  list(dt = dt, graph = g)
}

# ------------------------------------------------------------------ metrics
auc <- function(y, p) {
  ok <- !is.na(y) & !is.na(p); y <- y[ok]; p <- p[ok]
  n1 <- sum(y == 1); n0 <- sum(y == 0)
  if (n1 == 0 || n0 == 0) return(NA_real_)
  (sum(rank(p)[y == 1]) - n1 * (n1 + 1) / 2) / (n1 * n0)
}
# AUC computed inside each (year, disease) cell, then averaged with pair-count weights.
# Removes the year-level and disease-level base-rate drift that makes pooled AUC meaningless
# (pooled AUC of 0.355 in the first run was caused by this drift, not by model skill).
auc_strat <- function(y, p, year, disease) {
  d <- data.table(y = y, p = p, year = year, disease = disease)
  cells <- d[, .(a = auc(y, p), w = sum(y == 1) * sum(y == 0)), by = .(year, disease)]
  cells <- cells[!is.na(a) & w > 0]
  if (!nrow(cells)) return(NA_real_)
  sum(cells$a * cells$w) / sum(cells$w)
}
brier   <- function(y, p) mean((y - p)^2, na.rm = TRUE)
logloss <- function(y, p) { p <- pmin(pmax(p, 1e-6), 1 - 1e-6); -mean(y * log(p) + (1 - y) * log(1 - p), na.rm = TRUE) }

# Cluster bootstrap (resample counties) of AUC difference vs a reference column
boot_delta_auc <- function(wide, ref = "A", others, B = 500, seed = 1) {
  set.seed(seed)
  wide <- as.data.frame(wide)
  idx_by <- split(seq_len(nrow(wide)), wide$county)
  cs <- names(idx_by)
  sa <- function(ii, m) auc_strat(wide$y[ii], wide[[m]][ii], wide$year[ii], wide$disease[ii])
  d_one <- function(ii) vapply(others, function(m) sa(ii, m) - sa(ii, ref), numeric(1))
  obs <- d_one(seq_len(nrow(wide)))
  bs <- replicate(B, d_one(unlist(idx_by[sample(cs, length(cs), TRUE)], use.names = FALSE)))
  bs <- matrix(bs, nrow = length(others))
  data.table(model = others, delta_auc = obs,
             lo = apply(bs, 1, quantile, 0.025, na.rm = TRUE),
             hi = apply(bs, 1, quantile, 0.975, na.rm = TRUE))
}

# ------------------------------------------------------------------- models
# A = own history | B = A + mortality | C = A + context | D = all
build_design <- function(dat, train_mask, model, pooled = FALSE) {
  use_m <- model %in% c("B", "D"); use_c <- model %in% c("C", "D")
  zs <- function(v) {
    x <- dat[[v]]
    m <- mean(x[train_mask], na.rm = TRUE); s <- sd(x[train_mask], na.rm = TRUE)
    if (is.na(s) || s == 0) s <- 1
    (x - m) / s
  }
  X <- list()
  hv <- intersect(HIST, names(dat))
  if (!length(hv)) stop("No own-history columns found; model A cannot be built.")
  for (v in hv) { z <- zs(v); z[is.na(z)] <- 0; X[[v]] <- z }
  if (use_c) for (v in intersect(CTX, names(dat))) { z <- zs(v); z[is.na(z)] <- 0; X[[v]] <- z }
  if (use_m) for (v in intersect(MORT, names(dat))) {
    z <- zs(v); z[is.na(z)] <- 0   # no missing-indicator: suppression flags act as a county-size proxy
    if (pooled || startsWith(v, "nbr_") || startsWith(v, "xd_")) {
      X[[v]] <- z
    } else {
      for (g in sort(unique(dat$group))) X[[paste0(v, "__", g)]] <- z * (dat$group == g)
    }
  }
  X <- as.data.frame(X)
  keep <- vapply(X, function(x) isTRUE(sd(x[train_mask]) > 0), logical(1))
  X <- X[, keep, drop = FALSE]
  list(X = X, terms = names(X))
}

# Fit once with test responses set to NA; INLA returns predictions for them.
# year_effect: "iid" (default) gives the unseen test year a neutral level; "rw2" extrapolates the
# trend into the hidden year, which produced wildly wrong year levels in the first run.
fit_predict <- function(dat, test_idx, model, graph_file, pooled = FALSE, threads = "2:1",
                        year_effect = get_arg("year_effect", "iid")) {
  train_mask <- rep(TRUE, nrow(dat)); train_mask[test_idx] <- FALSE
  des <- build_design(dat, train_mask, model, pooled)
  d <- data.frame(up = dat$up, county_id = dat$county_id,
                  disease_id = dat$disease_id, year_id = dat$year_id, des$X)
  d$up[test_idx] <- NA
  yr_vals <- seq(min(d$year_id), max(d$year_id))
  disease_effect <- if (uniqueN(dat$disease_id) > 1L) {
    paste0(
      "f(disease_id, model = 'iid', n = ", max(dat$disease_id),
      ", hyper = list(prec = list(prior = 'pc.prec', param = c(1, 0.01))))"
    )
  } else {
    character()
  }
  year_term <- if (year_effect == "rw2") {
    paste0("f(year_id, model = 'rw2', values = yr_vals, n = ", max(yr_vals),
           ", scale.model = TRUE, constr = TRUE, hyper = list(prec = list(prior = 'pc.prec', param = c(1, 0.01))))")
  } else {
    paste0("f(year_id, model = 'iid', n = ", max(yr_vals),
           ", hyper = list(prec = list(prior = 'pc.prec', param = c(1, 0.01))))")
  }
  rhs <- c("1", des$terms, disease_effect,
           paste0("f(county_id, model = 'bym2', graph = graph_file, n = ", max(dat$county_id), ",
              scale.model = TRUE, constr = TRUE,
              hyper = list(phi = list(prior = 'pc', param = c(0.5, 2/3)),
                           prec = list(prior = 'pc.prec', param = c(1, 0.01))))"),
           year_term)
  form <- as.formula(paste("up ~", paste(rhs, collapse = " + ")))
  res <- INLA::inla(form, family = "binomial", data = d,
                    control.predictor = list(compute = TRUE, link = rep(1, nrow(d))),
                    control.inla = list(strategy = "gaussian"),
                    num.threads = threads, verbose = FALSE)
  res$summary.fitted.values$mean[test_idx]
}

score_table <- function(dt_pred) {
  dt_pred[, .(n = .N, events = sum(y),
              auc = auc_strat(y, p, year, disease),   # headline metric (within year x disease)
              auc_pooled = auc(y, p),                 # kept only for comparison
              brier = brier(y, p), logloss = logloss(y, p)),
          by = model]
}
