# 05_transitions.R - disease transitions (Phase 0 definition): negative binomial, RW2 trend, BYM2 space,
# county-specific RW2 deviations (space-time interaction). R-INLA.
# Transition = upward crossing of a threshold by Pr(underlying trend is rising), computed from posterior samples.
# Reads : 02_data/processed/analysis_long.csv, 05_results/tables/data_gate_disease_screen.csv
# Writes: 02_data/processed/transitions.csv, 05_results/transitions/model_summary.csv,
#         05_results/tables/transition_counts_by_disease.csv, transition_counts_by_group.csv,
#         02_data/interim/ca_county_adjacency.csv (neighbour pairs, reused later for spatial CV)
# STATUS: written without being able to run R here. Run SMOKE <- TRUE first.
# Install once:
#   install.packages(c("dplyr","readr","Matrix","sf","spdep","tigris","sn"))
#   install.packages("INLA", repos = c(getOption("repos"), INLA = "https://inla.r-inla-download.org/R/stable"), dep = TRUE)

SMOKE     <- !("--full" %in% commandArgs(TRUE)) # Default to smoke; pass --full for eligible diseases.
SMOKE_DIS <- "Campylobacteriosis"
NSAMP     <- 1000                 # posterior samples for the full run
TAUS      <- c(0.70, 0.80, 0.90)  # 0.80 = default; 0.70/0.90 = sensitivity. Freeze before cross-domain modelling.
MAIN_TAU  <- 0.80
THREADS   <- 2

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
dat_all <- read_csv(file.path(PROC, "analysis_long.csv"), col_types = cols(fips = col_character(), .default = col_guess()),
                    show_col_types = FALSE) %>%
  select(fips, year, disease, group, cases, pop = population_cdph)
screen <- read_csv(file.path(TAB, "data_gate_disease_screen.csv"), show_col_types = FALSE) %>%
  filter(window == "full_2001_2023", pass_2_3_4)
diseases <- sort(unique(screen$disease))
if (SMOKE) diseases <- intersect(SMOKE_DIS, diseases)
stopifnot(length(diseases) > 0)
cat("diseases to fit:", length(diseases), "\n")
fips_sorted <- sort(unique(dat_all$fips)); n_cty <- length(fips_sorted)

# ---------- 2. county graph (queen contiguity) ----------
adj_file <- file.path(INTERIM, "ca_county_adjacency.csv")
if (!file.exists(adj_file)) {
  suppressPackageStartupMessages({ library(sf); library(spdep); library(tigris) })
  options(tigris_use_cache = TRUE)
  ca <- tigris::counties(state = "CA", cb = TRUE, year = 2022)
  ca <- ca[order(ca$GEOID), ]
  nb <- spdep::poly2nb(ca, queen = TRUE)
  Wm <- spdep::nb2mat(nb, style = "B", zero.policy = TRUE); rownames(Wm) <- colnames(Wm) <- ca$GEOID
  pr <- which(Wm == 1 & upper.tri(Wm), arr.ind = TRUE)
  write_csv(data.frame(fips_a = rownames(Wm)[pr[, 1]], fips_b = colnames(Wm)[pr[, 2]]), adj_file)
}
adj <- read_csv(adj_file, col_types = cols(.default = col_character()), show_col_types = FALSE)
stopifnot(all(c(adj$fips_a, adj$fips_b) %in% fips_sorted))
Wm <- matrix(0, n_cty, n_cty, dimnames = list(fips_sorted, fips_sorted))
Wm[cbind(match(adj$fips_a, fips_sorted), match(adj$fips_b, fips_sorted))] <- 1
Wm <- pmax(Wm, t(Wm)); W <- Matrix(Wm, sparse = TRUE)
if (any(rowSums(Wm) == 0)) warning("counties with no neighbours: ", paste(fips_sorted[rowSums(Wm) == 0], collapse = ", "))

# ---------- 3. model ----------
hyper_rw2  <- list(prec = list(prior = "pc.prec", param = c(1, 0.01)))
hyper_bym2 <- list(prec = list(prior = "pc.prec", param = c(1, 0.01)), phi = list(prior = "pc", param = c(0.5, 2/3)))
formula <- cases ~ 1 +
  f(year_g, model = "rw2", scale.model = TRUE, constr = TRUE, hyper = hyper_rw2) +                      # statewide trend
  f(county_id, model = "bym2", graph = W, scale.model = TRUE, constr = TRUE, hyper = hyper_bym2) +      # county level + spatial
  f(year_c, model = "rw2", replicate = county_id, scale.model = TRUE, constr = TRUE, hyper = hyper_rw2) # county-specific change

fit_disease <- function(dis) {
  dd <- dat_all %>% filter(disease == dis)
  yrs <- seq(min(dd$year), max(dd$year))
  grid <- expand.grid(fips = fips_sorted, year = yrs, stringsAsFactors = FALSE) %>%
    left_join(dd %>% select(fips, year, cases, pop, group), by = c("fips", "year")) %>% arrange(fips, year)
  grid$pop <- ave(grid$pop, grid$fips, FUN = function(x) ifelse(is.na(x), median(x, na.rm = TRUE), x))
  grid$group <- dd$group[1]; grid$disease <- dis
  grid$county_id <- match(grid$fips, fips_sorted); grid$t <- match(grid$year, yrs)
  grid$year_g <- grid$t; grid$year_c <- grid$t
  # suppressed counts are NA in 'cases' and are treated as missing here (they are ranges in the cross-domain step)
  t0 <- Sys.time()
  res <- inla(formula, family = "nbinomial", data = grid, E = grid$pop,
              control.family = list(hyper = list(theta = list(prior = "pc.mgamma", param = 7))),
              control.predictor = list(compute = TRUE), control.compute = list(config = TRUE, waic = TRUE),
              num.threads = THREADS)
  n_obs <- nrow(grid)
  ns <- if (SMOKE) 200 else NSAMP
  samp <- inla.posterior.sample(n = ns, result = res, selection = list(Predictor = 1:n_obs), num.threads = THREADS)
  eta <- sapply(samp, function(s) s$latent[, 1])                   # n_obs x ns ; log rate (offset excluded)
  now <- which(grid$t >= 2); prv <- now - 1                        # grid is sorted by county, then year
  Dm  <- eta[now, , drop = FALSE] - eta[prv, , drop = FALSE]
  out <- grid[now, c("disease", "group", "fips", "year", "t", "cases", "pop")]
  out$p_rising   <- rowMeans(Dm > 0)
  out$slope_mean <- rowMeans(Dm)
  out$slope_sd   <- apply(Dm, 1, sd)
  # LOCAL signal: remove the statewide change in each year (per posterior sample), so an event means
  # "this county is rising faster than the state", not "the whole state rose this year".
  Dm_loc <- Dm
  for (yy in unique(out$year)) {
    ii <- which(out$year == yy)
    Dm_loc[ii, ] <- sweep(Dm[ii, , drop = FALSE], 2, colMeans(Dm[ii, , drop = FALSE]), "-")
  }
  out$p_rising_local <- rowMeans(Dm_loc > 0)
  for (tau in TAUS) {
    ab <- out$p_rising >= tau
    prev <- c(NA, head(ab, -1)); prev[out$t == 2] <- NA            # first usable year has no previous state
    out[[sprintf("above_%.2f", tau)]]   <- as.integer(ab)
    out[[sprintf("upcross_%.2f", tau)]] <- as.integer(ab & !prev)
    abl <- out$p_rising_local >= tau
    prevl <- c(NA, head(abl, -1)); prevl[out$t == 2] <- NA
    out[[sprintf("above_local_%.2f", tau)]]   <- as.integer(abl)
    out[[sprintf("upcross_local_%.2f", tau)]] <- as.integer(abl & !prevl)
  }
  list(out = out %>% select(-t),
       summ = data.frame(disease = dis, group = grid$group[1], n_rows = n_obs, n_missing_cases = sum(is.na(grid$cases)),
                         waic = res$waic$waic, nb_size_mean = res$summary.hyperpar[1, "mean"],
                         minutes = as.numeric(difftime(Sys.time(), t0, units = "mins"))))
}

results <- list(); summ <- list(); failed <- character()
for (dis in diseases) {
  cat("fitting:", dis, "\n")
  r <- tryCatch(fit_disease(dis), error = function(e) {
    message("FAILED ", dis, ": ", conditionMessage(e))
    failed <<- c(failed, dis)
    NULL
  })
  if (!is.null(r)) { results[[dis]] <- r$out; summ[[dis]] <- r$summ }
}
stopifnot(length(results) > 0)
if (!SMOKE && length(failed)) {
  stop("Full transition run incomplete; failed diseases: ", paste(failed, collapse = ", "))
}
trans <- bind_rows(results)
write_csv(trans, file.path(PROC, if (SMOKE) "transitions_smoke.csv" else "transitions.csv"))
write_csv(bind_rows(summ), file.path(RES, if (SMOKE) "model_summary_smoke.csv" else "model_summary.csv"))

# ---------- 4. event counts (the real Gate 5 evidence) ----------
col <- sprintf("upcross_%.2f", MAIN_TAU)
by_dis <- trans %>% group_by(group, disease) %>%
  summarise(county_years = sum(!is.na(.data[[col]])), events = sum(.data[[col]], na.rm = TRUE),
            event_share = events / county_years, .groups = "drop")
by_grp <- by_dis %>% group_by(group) %>% summarise(diseases = n(), events = sum(events), .groups = "drop")
write_csv(by_dis, file.path(TAB, if (SMOKE) "transition_counts_by_disease_smoke.csv" else "transition_counts_by_disease.csv"))
write_csv(by_grp, file.path(TAB, if (SMOKE) "transition_counts_by_group_smoke.csv" else "transition_counts_by_group.csv"))
print(as.data.frame(by_dis))
cat("\nINLA version:", as.character(packageVersion("INLA")), "| done.\n")
