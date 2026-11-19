# 05_transitions_rolling_origin.R
# Leakage-reduced transition labels for leave-future-out evaluation.
#
# For forecast origin T, the target transition is T -> T+1. Each disease model
# is refitted using observations no later than T+1. No observations after the
# target year enter the label. This replaces the all-years smoother used by
# 05_transitions.R for the rolling-origin sensitivity analysis.
#
# IMPORTANT:
# - This is an outcome-label reconstruction, not a change to the predictor models.
# - The label is still a retrospective estimate of the target-year transition:
#   target-year counts are necessarily used to establish whether a transition
#   occurred. The key restriction is that no post-target-year data are used.
# - For the crossing rule, the previous-year status is recomputed from the same
#   truncated fit. This keeps the two adjacent annual probabilities comparable.
#
# Run from project root:
#   Rscript 04_scripts/05_transitions_rolling_origin.R
#   Rscript 04_scripts/05_transitions_rolling_origin.R --origins=2017,2018,2019,2020 --nsamp=1000
#
# Output:
#   02_data/processed/transitions_rolling_lfo.csv
#   05_results/transitions/rolling_origin_label_summary.csv

suppressPackageStartupMessages({
  library(INLA)
  library(dplyr)
  library(readr)
  library(Matrix)
})

args <- commandArgs(TRUE)
get_arg <- function(name, default) {
  hit <- args[startsWith(args, paste0("--", name, "="))]
  if (length(hit)) sub(paste0("--", name, "="), "", hit[1]) else default
}

find_root <- function() {
  a <- commandArgs(FALSE)
  f <- sub("^--file=", "", a[grep("^--file=", a)])
  d <- if (length(f)) dirname(normalizePath(f)) else getwd()
  for (i in 1:6) {
    if (dir.exists(file.path(d, "02_data"))) return(d)
    if (dir.exists(file.path(d, "project3", "02_data"))) return(file.path(d, "project3"))
    d <- dirname(d)
  }
  stop("Cannot find project root (folder containing 02_data).")
}
ROOT <- find_root()
PROC <- file.path(ROOT, "02_data/processed")
TAB  <- file.path(ROOT, "05_results/tables")
RES  <- file.path(ROOT, "05_results/transitions")
dir.create(RES, recursive = TRUE, showWarnings = FALSE)

ORIGINS <- as.integer(strsplit(get_arg("origins", "2017,2018,2019,2020"), ",", fixed = TRUE)[[1]])
TAU <- as.numeric(get_arg("tau", "0.80"))
NSAMP <- as.integer(get_arg("nsamp", "1000"))
THREADS <- get_arg("threads", "2")
SEED <- as.integer(get_arg("seed", "20261120"))
if (!length(ORIGINS) || anyNA(ORIGINS) || any(ORIGINS < 2002)) stop("Invalid --origins.")
if (length(TAU) != 1 || is.na(TAU) || TAU <= 0 || TAU >= 1) stop("--tau must be between 0 and 1.")
if (is.na(NSAMP) || NSAMP < 100) stop("--nsamp must be at least 100.")

panel_path <- file.path(PROC, "analysis_long.csv")
screen_path <- file.path(TAB, "data_gate_disease_screen.csv")
stopifnot(file.exists(panel_path), file.exists(screen_path))

dat_all <- read_csv(
  panel_path,
  col_types = cols(fips = col_character(), .default = col_guess()),
  show_col_types = FALSE
) %>%
  transmute(
    fips = sprintf("%05s", fips),
    year = as.integer(year),
    disease, group,
    cases = as.numeric(cases),
    pop = as.numeric(population_cdph)
  )

screen <- read_csv(screen_path, show_col_types = FALSE) %>%
  filter(window == "full_2001_2023", pass_2_3_4)
diseases <- sort(unique(screen$disease))
fips_sorted <- sort(unique(dat_all$fips))
n_cty <- length(fips_sorted)

# Fixed graph for California counties. The adjacency is built once by the
# original transition pipeline and is independent of the annual outcome data.
adj_file <- file.path(ROOT, "02_data/interim/ca_county_adjacency.csv")
if (!file.exists(adj_file)) {
  stop("Missing county adjacency file. Run 05_transitions.R once to create: ", adj_file)
}
adj <- read_csv(adj_file, col_types = cols(.default = col_character()), show_col_types = FALSE)
Wm <- matrix(0, n_cty, n_cty, dimnames = list(fips_sorted, fips_sorted))
Wm[cbind(match(adj$fips_a, fips_sorted), match(adj$fips_b, fips_sorted))] <- 1
Wm <- pmax(Wm, t(Wm))
W <- Matrix(Wm, sparse = TRUE)

hyper_rw2 <- list(prec = list(prior = "pc.prec", param = c(1, 0.01)))
hyper_bym2 <- list(
  prec = list(prior = "pc.prec", param = c(1, 0.01)),
  phi = list(prior = "pc", param = c(0.5, 2/3))
)
formula <- cases ~ 1 +
  f(year_g, model = "rw2", scale.model = TRUE, constr = TRUE, hyper = hyper_rw2) +
  f(county_id, model = "bym2", graph = W, scale.model = TRUE, constr = TRUE, hyper = hyper_bym2) +
  f(year_c, model = "rw2", replicate = county_id, scale.model = TRUE, constr = TRUE, hyper = hyper_rw2)

# Return local posterior probabilities for a given annual change. The statewide
# mean change is subtracted separately within each posterior draw.
local_probability <- function(Dm) {
  Dlocal <- Dm
  Dlocal <- sweep(Dlocal, 2, colMeans(Dm), "-")
  rowMeans(Dlocal > 0)
}

fit_one_disease_origin <- function(dis, origin) {
  target_year <- origin + 1L
  dd <- dat_all %>% filter(disease == dis, year <= target_year)
  if (!nrow(dd) || target_year > max(dat_all$year)) return(NULL)

  first_year <- min(dd$year)
  if (target_year - first_year < 2L) return(NULL)
  years <- seq(first_year, target_year)

  grid <- expand.grid(fips = fips_sorted, year = years, stringsAsFactors = FALSE) %>%
    left_join(dd %>% select(fips, year, cases, pop, group),
              by = c("fips", "year")) %>%
    arrange(fips, year)

  # Impute missing population only from information available by target_year.
  grid$pop <- ave(grid$pop, grid$fips, FUN = function(x) {
    med <- suppressWarnings(median(x, na.rm = TRUE))
    if (!is.finite(med)) med <- 1
    ifelse(is.na(x), med, x)
  })
  grid$group <- dd$group[1]
  grid$disease <- dis
  grid$county_id <- match(grid$fips, fips_sorted)
  grid$t <- match(grid$year, years)
  grid$year_g <- grid$t
  grid$year_c <- grid$t

  set.seed(SEED + as.integer(target_year) + as.integer(match(dis, diseases)))
  fit <- INLA::inla(
    formula,
    family = "nbinomial",
    data = grid,
    E = grid$pop,
    control.family = list(hyper = list(theta = list(prior = "pc.mgamma", param = 7))),
    control.predictor = list(compute = TRUE),
    control.compute = list(config = TRUE),
    num.threads = THREADS,
    verbose = FALSE
  )

  n_obs <- nrow(grid)
  samp <- INLA::inla.posterior.sample(
    n = NSAMP, result = fit,
    selection = list(Predictor = seq_len(n_obs)),
    num.threads = THREADS
  )
  eta <- vapply(samp, function(s) s$latent[seq_len(n_obs)], numeric(n_obs))

  # The grid is ordered by county, then year. Extract the same annual contrast
  # for every county so statewide centring is performed draw-by-draw.
  idx_for_year <- function(yy) which(grid$year == yy)
  idx_target <- idx_for_year(target_year)
  idx_prev <- idx_for_year(target_year - 1L)
  idx_prev2 <- idx_for_year(target_year - 2L)
  stopifnot(length(idx_target) == n_cty, length(idx_prev) == n_cty,
            length(idx_prev2) == n_cty)

  D_target <- eta[idx_target, , drop = FALSE] - eta[idx_prev, , drop = FALSE]
  D_previous <- eta[idx_prev, , drop = FALSE] - eta[idx_prev2, , drop = FALSE]
  p_target <- local_probability(D_target)
  p_previous <- local_probability(D_previous)

  out <- data.frame(
    fips = grid$fips[idx_target],
    year = target_year,
    forecast_origin = origin,
    disease = dis,
    group = grid$group[idx_target],
    p_rising_local = p_target,
    p_rising_local_previous = p_previous,
    above_local = as.integer(p_target >= TAU),
    above_local_previous = as.integer(p_previous >= TAU),
    stringsAsFactors = FALSE
  )
  event_name <- sprintf("upcross_local_%.2f", TAU)
  out[[event_name]] <- as.integer(p_target >= TAU & p_previous < TAU)
  out
}

all_results <- list()
failures <- character()
for (origin in ORIGINS) {
  target_year <- origin + 1L
  if (target_year > max(dat_all$year)) {
    warning("Skipping origin ", origin, ": target year exceeds available data.")
    next
  }
  message("\n=== Forecast origin ", origin, " -> target year ", target_year, " ===")
  for (dis in diseases) {
    message("Fitting ", dis, " through ", target_year)
    ans <- tryCatch(
      fit_one_disease_origin(dis, origin),
      error = function(e) {
        failures <<- c(failures, paste(dis, target_year, conditionMessage(e), sep = " | "))
        message("FAILED: ", dis, " / ", target_year, " : ", conditionMessage(e))
        NULL
      }
    )
    if (!is.null(ans)) all_results[[length(all_results) + 1L]] <- ans
  }
}

if (!length(all_results)) stop("No rolling-origin transition labels were generated.")
if (length(failures)) {
  write_lines(failures, file.path(RES, "rolling_origin_failures.txt"))
  stop("Rolling-origin run incomplete: ", length(failures),
       " disease-origin fits failed. See rolling_origin_failures.txt; do not score partial labels.")
}

rolling <- bind_rows(all_results) %>%
  arrange(forecast_origin, disease, fips)
event_name <- sprintf("upcross_local_%.2f", TAU)
summary <- rolling %>%
  group_by(forecast_origin, year, disease, group) %>%
  summarise(
    county_rows = n(),
    events = sum(.data[[event_name]], na.rm = TRUE),
    event_share = events / county_rows,
    .groups = "drop"
  )

out_path <- file.path(PROC, "transitions_rolling_lfo.csv")
write_csv(rolling, out_path)
write_csv(summary, file.path(RES, "rolling_origin_label_summary.csv"))
message("\nWrote: ", out_path)
message("Total rows: ", nrow(rolling), " | total events: ", sum(rolling[[event_name]], na.rm = TRUE))
print(summary)
message("\nLabels are restricted to data through each target year. They are not a real-time prediction model.")
