# ============================================================================
# 07_leadtime.R  -  does a mortality alarm precede disease up-transitions?
#
# Alarm: a county's mortality rate in year t is >= z_thr SDs above its own
#        trailing 5-year mean (needs >= 3 prior years).
# For each county-disease-year row (outcome = up-transition t -> t+1) we ask
#   was there an alarm in years t-4..t ?   lead = (t+1) - first alarm year
# Statistic: P(alarm | event) - P(alarm | no event), per group and mortality series.
# Null: county-swap permutation (each county's whole alarm history is assigned
#       to a random other county): breaks the county link, keeps time structure.
#
# Run: Rscript 04_scripts/07_leadtime.R   Options: --perms=1000 --zthr=1.0,1.5
# Outputs: 05_results/tables/leadtime_summary.csv, 05_results/figures/leadtime_hist.png
# ============================================================================
suppressPackageStartupMessages(library(data.table))
.here <- function() {
  a <- commandArgs(FALSE); f <- sub("^--file=", "", a[grepl("^--file=", a)])
  if (length(f)) return(dirname(normalizePath(f)))
  for (p in c("04_scripts", "project3/04_scripts")) if (dir.exists(p)) return(normalizePath(p))
  stop("cd to project3 first")
}
# lightweight: only paths and arg parser, no INLA needed here
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
TAB <- file.path(ROOT, "05_results", "tables"); FIG <- file.path(ROOT, "05_results", "figures")
dir.create(TAB, FALSE, TRUE); dir.create(FIG, FALSE, TRUE)
get_arg <- function(name, default) {
  a <- commandArgs(TRUE); hit <- a[startsWith(a, paste0("--", name, "="))]
  if (length(hit)) sub(paste0("--", name, "="), "", hit[1]) else default
}
n_perm <- as.integer(get_arg("perms", 1000))
z_thr  <- as.numeric(strsplit(get_arg("zthr", "1.0,1.5"), ",")[[1]])
MORT   <- c("allcause_rate", "drug_od_rate", "suicide_rate", "homicide_rate")
LMAX   <- 5L

tb <- fread(file.path(ROOT, "02_data", "processed", "model_table.csv"))
tb <- tb[!is.na(up)]
mv <- intersect(MORT, names(tb))
if (!length(mv)) stop("No mortality columns in model_table.csv")
mort <- unique(tb[, c("county", "year", mv), with = FALSE])
counties <- sort(unique(tb$county)); years <- sort(unique(mort$year))
ci <- match(tb$county, counties); yi <- match(tb$year, years)

alarm_fun <- function(x, zthr) {
  L <- sapply(1:5, function(k) shift(x, k))
  mu <- rowMeans(L, na.rm = TRUE); n <- rowSums(!is.na(L))
  sdv <- apply(L, 1, sd, na.rm = TRUE)
  z <- (x - mu) / pmax(sdv, 0.1 * abs(mu), 1e-8)
  as.integer(n >= 3 & !is.na(z) & z >= zthr)
}

# lead matrix [county, year]: years of warning given by the earliest alarm in t-4..t
lead_matrix <- function(v, zthr) {
  M <- matrix(NA_integer_, length(counties), length(years))
  for (c in seq_along(counties)) {
    s <- mort[county == counties[c]][order(year)]
    s <- s[match(years, s$year)]
    a <- alarm_fun(s[[v]], zthr)
    lead <- rep(NA_integer_, length(a))
    for (k in (LMAX - 1):0) {
      ak <- shift(a, k)
      lead <- fifelse(ak %in% 1L & is.na(lead), as.integer(k + 1L), lead)
    }
    M[c, ] <- lead
  }
  M
}

grp_idx <- split(seq_len(nrow(tb)), tb$group)
stat_fun <- function(a) vapply(grp_idx, function(ii) {
  mean(a[ii][tb$up[ii] == 1], na.rm = TRUE) - mean(a[ii][tb$up[ii] == 0], na.rm = TRUE)
}, numeric(1))

set.seed(42)
res <- list(); leads_all <- list()
for (zt in z_thr) for (v in mv) {
  M <- lead_matrix(v, zt)
  lead_row <- M[cbind(ci, yi)]
  any_row <- as.numeric(!is.na(lead_row))
  any_row[is.na(tb[[v]])] <- NA            # mortality unknown -> not scored
  obs <- stat_fun(any_row)
  nullm <- replicate(n_perm, {
    perm <- sample(seq_along(counties))
    a <- as.numeric(!is.na(M[cbind(perm[ci], yi)]))
    a[is.na(tb[[v]])] <- NA
    stat_fun(a)
  })
  nullm <- matrix(nullm, nrow = length(grp_idx))
  for (k in seq_along(grp_idx)) {
    ii <- grp_idx[[k]]; ev <- ii[tb$up[ii] == 1]
    res[[length(res) + 1]] <- data.table(
      zthr = zt, mortality = v, group = names(grp_idx)[k],
      n_events = length(ev), n_nonevents = length(ii) - length(ev),
      p_alarm_event = mean(any_row[ev], na.rm = TRUE),
      p_alarm_nonevent = mean(any_row[setdiff(ii, ev)], na.rm = TRUE),
      diff = obs[k], null_mean = mean(nullm[k, ], na.rm = TRUE),
      perm_p_one_sided = (1 + sum(nullm[k, ] >= obs[k], na.rm = TRUE)) / (n_perm + 1),
      median_lead_years = suppressWarnings(median(lead_row[ev], na.rm = TRUE)))
    leads_all[[length(leads_all) + 1]] <- data.table(zthr = zt, mortality = v, group = names(grp_idx)[k],
                                                      lead = lead_row[ev])
  }
}
summ <- rbindlist(res)
summ[, perm_p_holm := p.adjust(perm_p_one_sided, "holm")]
fwrite(summ, file.path(TAB, "leadtime_summary.csv"))
print(summ[order(perm_p_one_sided)][1:min(20, .N)])

# figure of observed leads (primary threshold = first one)
try({
  library(ggplot2)
  ld <- rbindlist(leads_all)[zthr == z_thr[1] & !is.na(lead)]
  p <- ggplot(ld, aes(lead)) + geom_bar() + facet_grid(group ~ mortality, scales = "free_y") +
    labs(x = "years of warning before up-transition", y = "events with an alarm",
         title = paste0("Lead time of mortality alarms (z >= ", z_thr[1], ")")) + theme_bw()
  ggsave(file.path(FIG, "leadtime_hist.png"), p, width = 10, height = 8, dpi = 150)
}, silent = TRUE)

cat("\nRead this table with the Holm-adjusted p-values: with 4 mortality series x several groups x",
    length(z_thr), "thresholds you are testing many hypotheses.\n")
