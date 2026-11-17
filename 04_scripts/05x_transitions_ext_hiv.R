# 05x_transitions_ext_hiv.R - EXPLORATORY extension: transitions for HIV diagnoses (Office of AIDS series, 2012-2023).
# Same method as 05_transitions.R (negative binomial, RW2 trend, BYM2 space, county-specific RW2 deviations,
# Pr(trend rising) from 1000 posterior samples, TAUS 0.70/0.80/0.90, global and local signals).
# Differences (all deliberate, log them in the deviations log):
#   * reads 02_data/processed/analysis_long_ext_hiv.csv and fits ONLY "HIV diagnoses (Office of AIDS)"
#   * skips the data-gate screen (HIV has 12 years, not the 2001-2023 window that gate tests)
#   * writes NEW files only; transitions.csv and the frozen results are not touched
# Reads : 02_data/processed/analysis_long_ext_hiv.csv  (from build_ext_hiv_rows.py)
# Writes: 02_data/processed/transitions_ext_hiv.csv
#         05_results/transitions/model_summary_ext_hiv.csv
#         05_results/tables/transition_counts_ext_hiv.csv
# Run   : Rscript 04_scripts/05x_transitions_ext_hiv.R            (add --smoke for 200 samples)

SMOKE    <- "--smoke" %in% commandArgs(TRUE)
EXT_DIS  <- "HIV diagnoses (Office of AIDS)"
NSAMP    <- if (SMOKE) 200 else 1000
TAUS     <- c(0.70, 0.80, 0.90)
MAIN_TAU <- 0.80
THREADS  <- 2

suppressPackageStartupMessages({ library(INLA); library(dplyr); library(readr); library(Matrix) })

find_root <- function() {
  a <- commandArgs(FALSE); f <- sub("^--file=", "", a[grep("^--file=", a)])
  d <- if (length(f)) dirname(normalizePath(f)) else getwd()
  for (i in 1:6) {
    if (dir.exists(file.path(d, "02_data"))) return(d)
    if (dir.exists(file.path(d, "project3", "02_data"))) return(file.path(d, "project3"))
    d <- dirname(d)
  }
  stop("Cannot find the project root (folder containing 02_data). Set ROOT <- '...' by hand.")
}
ROOT <- find_root()
PROC <- file.path(ROOT, "02_data/processed"); INTERIM <- file.path(ROOT, "02_data/interim")
RES  <- file.path(ROOT, "05_results/transitions"); TAB <- file.path(ROOT, "05_results/tables")
for (p in c(RES, TAB, INTERIM)) dir.create(p, recursive = TRUE, showWarnings = FALSE)

# ---------- 1. data ----------
dat_all <- read_csv(file.path(PROC, "analysis_long_ext_hiv.csv"),
                    col_types = cols(fips = col_character(), .default = col_guess()), show_col_types = FALSE) %>%
  select(fips, year, disease, group, cases, pop = population_cdph) %>%
  filter(disease == EXT_DIS)
stopifnot(nrow(dat_all) > 0)
dat_all$fips <- sprintf("%05d", as.integer(dat_all$fips))
fips_sorted <- sort(unique(dat_all$fips)); n_cty <- length(fips_sorted)
cat("rows:", nrow(dat_all), "| counties:", n_cty, "| years:", min(dat_all$year), "-", max(dat_all$year), "\n")

# ---------- 2. county graph (reuse the adjacency written by 05_transitions.R) ----------
adj_file <- file.path(INTERIM, "ca_county_adjacency.csv")
if (!file.exists(adj_file)) stop("Missing ", adj_file, " - run 05_transitions.R once (it creates it).")
adj <- read_csv(adj_file, col_types = cols(.default = col_character()), show_col_types = FALSE)
stopifnot(all(c(adj$fips_a, adj$fips_b) %in% fips_sorted))
Wm <- matrix(0, n_cty, n_cty, dimnames = list(fips_sorted, fips_sorted))
Wm[cbind(match(adj$fips_a, fips_sorted), match(adj$fips_b, fips_sorted))] <- 1
Wm <- pmax(Wm, t(Wm)); W <- Matrix(Wm, sparse = TRUE)

# ---------- 3. model (identical to 05_transitions.R) ----------
hyper_rw2  <- list(prec = list(prior = "pc.prec", param = c(1, 0.01)))
hyper_bym2 <- list(prec = list(prior = "pc.prec", param = c(1, 0.01)), phi = list(prior = "pc", param = c(0.5, 2/3)))
formula <- cases ~ 1 +
  f(year_g, model = "rw2", scale.model = TRUE, constr = TRUE, hyper = hyper_rw2) +
  f(county_id, model = "bym2", graph = W, scale.model = TRUE, constr = TRUE, hyper = hyper_bym2) +
  f(year_c, model = "rw2", replicate = county_id, scale.model = TRUE, constr = TRUE, hyper = hyper_rw2)

dis <- EXT_DIS
dd <- dat_all
yrs <- seq(min(dd$year), max(dd$year))
grid <- expand.grid(fips = fips_sorted, year = yrs, stringsAsFactors = FALSE) %>%
  left_join(dd %>% select(fips, year, cases, pop, group), by = c("fips", "year")) %>% arrange(fips, year)
grid$pop <- ave(grid$pop, grid$fips, FUN = function(x) ifelse(is.na(x), median(x, na.rm = TRUE), x))
grid$group <- dd$group[1]; grid$disease <- dis
grid$county_id <- match(grid$fips, fips_sorted); grid$t <- match(grid$year, yrs)
grid$year_g <- grid$t; grid$year_c <- grid$t
cat("missing cases in grid:", sum(is.na(grid$cases)), "of", nrow(grid), "\n")

t0 <- Sys.time()
res <- inla(formula, family = "nbinomial", data = grid, E = grid$pop,
            control.family = list(hyper = list(theta = list(prior = "pc.mgamma", param = 7))),
            control.predictor = list(compute = TRUE), control.compute = list(config = TRUE, waic = TRUE),
            num.threads = THREADS)
n_obs <- nrow(grid)
samp <- inla.posterior.sample(n = NSAMP, result = res, selection = list(Predictor = 1:n_obs), num.threads = THREADS)
eta <- sapply(samp, function(s) s$latent[, 1])
now <- which(grid$t >= 2); prv <- now - 1
Dm  <- eta[now, , drop = FALSE] - eta[prv, , drop = FALSE]
out <- grid[now, c("disease", "group", "fips", "year", "t", "cases", "pop")]
out$p_rising   <- rowMeans(Dm > 0)
out$slope_mean <- rowMeans(Dm)
out$slope_sd   <- apply(Dm, 1, sd)
Dm_loc <- Dm
for (yy in unique(out$year)) {
  ii <- which(out$year == yy)
  Dm_loc[ii, ] <- sweep(Dm[ii, , drop = FALSE], 2, colMeans(Dm[ii, , drop = FALSE]), "-")
}
out$p_rising_local <- rowMeans(Dm_loc > 0)
for (tau in TAUS) {
  ab <- out$p_rising >= tau
  prev <- c(NA, head(ab, -1)); prev[out$t == 2] <- NA
  out[[sprintf("above_%.2f", tau)]]   <- as.integer(ab)
  out[[sprintf("upcross_%.2f", tau)]] <- as.integer(ab & !prev)
  abl <- out$p_rising_local >= tau
  prevl <- c(NA, head(abl, -1)); prevl[out$t == 2] <- NA
  out[[sprintf("above_local_%.2f", tau)]]   <- as.integer(abl)
  out[[sprintf("upcross_local_%.2f", tau)]] <- as.integer(abl & !prevl)
}
out <- out %>% select(-t)

summ <- data.frame(disease = dis, group = grid$group[1], n_rows = n_obs, n_missing_cases = sum(is.na(grid$cases)),
                   waic = res$waic$waic, nb_size_mean = res$summary.hyperpar[1, "mean"],
                   nsamp = NSAMP, minutes = as.numeric(difftime(Sys.time(), t0, units = "mins")))
sfx <- if (SMOKE) "_smoke" else ""
write_csv(out,  file.path(PROC, paste0("transitions_ext_hiv", sfx, ".csv")))
write_csv(summ, file.path(RES,  paste0("model_summary_ext_hiv", sfx, ".csv")))

col <- sprintf("upcross_%.2f", MAIN_TAU)
cnt <- out %>% group_by(group, disease) %>%
  summarise(county_years = sum(!is.na(.data[[col]])), events = sum(.data[[col]], na.rm = TRUE),
            event_share = events / county_years, .groups = "drop")
write_csv(cnt, file.path(TAB, paste0("transition_counts_ext_hiv", sfx, ".csv")))
print(as.data.frame(cnt))
cat("\nINLA", as.character(packageVersion("INLA")), "| minutes:", round(summ$minutes, 1), "| done.\n")