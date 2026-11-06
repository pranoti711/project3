# ============================================================================
# 06_models_ABCD.R  -  predictive models A, B, C, D with leave-future-out CV
#   A own history | B A + mortality | C A + context | D everything
# Binomial INLA model: disease iid + county BYM2 + year RW2 (+ fixed effects).
# Mortality effects are group-specific (drug_linked, comparison, ...).
#
# Run (from project3 or its parent):  Rscript 04_scripts/06_models_ABCD.R
# Options: --n_test=6 (number of test years)  --boot=500  --year_effect=iid|rw2  --input=...  --tag=...
# AUC reported as 'auc' is stratified within year x disease (auc_pooled is kept for comparison).
# Outputs: 05_results/tables/oof_predictions_lfo.csv
#          05_results/tables/model_scores_lfo.csv (overall, by group, by year)
#          05_results/tables/model_delta_auc_lfo.csv (vs A, county-cluster bootstrap CI)
# ============================================================================
.here <- function() {
  a <- commandArgs(FALSE); f <- sub("^--file=", "", a[grepl("^--file=", a)])
  if (length(f)) return(dirname(normalizePath(f)))
  for (p in c("04_scripts", "project3/04_scripts")) if (dir.exists(p)) return(normalizePath(p))
  stop("cd to project3 first")
}
source(file.path(.here(), "p3_common.R"))
input_path <- get_arg("input", P$model_table)
P$model_table <- if (grepl("^([A-Za-z]:|/)", input_path)) input_path else file.path(ROOT, input_path)

n_test <- as.integer(get_arg("n_test", 6))
n_boot <- as.integer(get_arg("boot", 500))
output_tag <- get_arg("tag", "")
output_file <- function(name) {
  suffix <- if (nzchar(output_tag)) paste0("_", output_tag) else ""
  file.path(P$tables, sub("\\.csv$", paste0(suffix, ".csv"), name))
}
models <- c("A", "B", "C", "D")

tb <- prep_table(); dat <- tb$dt; g <- tb$graph
if (is.na(n_test) || n_test < 1L) stop("--n_test must be a positive integer.")
if (is.na(n_boot) || n_boot < 1L) stop("--boot must be a positive integer.")
test_years <- tail(sort(unique(dat$year)), n_test)
message("Leave-future-out test years: ", paste(test_years, collapse = ", "))

out <- list()
for (T in test_years) {
  # Forecast origin T: rows up to year T are visible, outcomes of year-T rows are hidden.
  # (Outcome of row year t is the move t -> t+1, so rows <= T-1 are fully known at T.)
  sub <- dat[year <= T]
  test_idx <- which(sub$year == T)
  if (sum(sub$up[test_idx]) == 0) { message("No events in ", T, ", skipped"); next }
  for (m in models) {
    t0 <- Sys.time()
    p <- fit_predict(sub, test_idx, m, g$file)
    out[[length(out) + 1]] <- data.table(
      county = sub$county[test_idx], fips = sub$fips[test_idx], year = T,
      disease = sub$disease[test_idx], group = sub$group[test_idx],
      y = sub$up[test_idx], model = m, p = p)
    message(sprintf("year %d model %s done (%.0fs)", T, m, as.numeric(difftime(Sys.time(), t0, units = "secs"))))
  }
}
if (!length(out)) stop("No test-year predictions were produced; check event counts and the selected test window.")
oof <- rbindlist(out)
calib <- oof[model == "A", .(events = sum(y), rate = mean(y), mean_p = mean(p)), by = year]
fwrite(calib, output_file("calibration_by_year.csv"))
cat("\n=== Observed vs predicted event rate by test year (model A) ===\n"); print(calib)
oof_save <- copy(oof); setnames(oof_save, "y", "up")   # scripts 09/10 read the column as 'up'
fwrite(oof_save, output_file("oof_predictions_lfo.csv"))

sc_all <- cbind(scope = "all", score_table(oof))
sc_grp <- rbindlist(lapply(unique(oof$group), function(gr) cbind(scope = gr, score_table(oof[group == gr]))))
sc_yr  <- rbindlist(lapply(sort(unique(oof$year)), function(yy) cbind(scope = paste0("year_", yy), score_table(oof[year == yy]))))
scores <- rbind(sc_all, sc_grp, sc_yr)
fwrite(scores, output_file("model_scores_lfo.csv"))

wide <- dcast(oof, county + fips + year + disease + group + y ~ model, value.var = "p")
dl <- rbind(
  cbind(scope = "all", boot_delta_auc(wide, "A", c("B", "C", "D"), B = n_boot)),
  rbindlist(lapply(unique(wide$group), function(gr) {
    w <- wide[group == gr]
    if (sum(w$y) < 5) return(NULL)
    cbind(scope = gr, boot_delta_auc(w, "A", c("B", "C", "D"), B = n_boot))
  })))
fwrite(dl, output_file("model_delta_auc_lfo.csv"))

cat("\n=== Overall scores (leave-future-out) ===\n"); print(sc_all)
cat("\n=== Delta AUC vs model A (95% county-cluster bootstrap) ===\n"); print(dl)
cat("\nInterpretation: an interval for B-A that excludes 0 in a group means mortality adds out-of-sample\n",
    "predictive value there. Run 11_placebos_surrogates.py before believing any positive result.\n")
