 git tag -f advanced-freeze 6b7f8d2                     
Updated tag 'advanced-freeze' (was 098aff0)
PS C:\Users\Pranoti munjankar\OneDrive\Desktop\iit tirupati\PROJECT\project3> git status
On branch master
nothing to commit, working tree clean
PS C:\Users\Pranoti munjankar\OneDrive\Desktop\iit tirupati\PROJECT\project3> git log --oneline -6 --decorate
6b7f8d2 (HEAD -> master, tag: advanced-freeze) Deviations log: note removed draft scripts
4da2c14 Remove stray file 'text'
50d7cd7 Remove unused superseded scripts (20_advanced_analysis, 22_make_maps_and_heatmap)
098aff0 Deviations log entry for advanced layer; remove duplicate TRIPOD file
db26fa0 Advanced layer results
ed4e0b0 Advanced layer plan and code
PS C:\Users\Pranoti munjankar\OneDrive\Desktop\iit tirupati\PROJECT\project3> 
 *  History restored 

PS C:\Users\Pranoti munjankar\OneDrive\Desktop\iit tirupati\PROJECT\project3> Expand-Archive -Path "$HOME\Downloads\advanced2.zip" -DestinationPath "$env:TEMP\advanced2" -Force              
PS C:\Users\Pranoti munjankar\OneDrive\Desktop\iit tirupati\PROJECT\project3> Copy-Item "$env:TEMP\advanced2\advanced2\04_scripts\*" 04_scripts\ -Force
PS C:\Users\Pranoti munjankar\OneDrive\Desktop\iit tirupati\PROJECT\project3> Copy-Item "$env:TEMP\advanced2\advanced2\tools\run_advanced.ps1" tools\ -Force
Copy-Item: Cannot find path 'C:\Users\PRANOT~1\AppData\Local\Temp\advanced2\advanced2\tools\run_advanced.ps1' because it does not exist.
PS C:\Users\Pranoti munjankar\OneDrive\Desktop\iit tirupati\PROJECT\project3> git status --short 05_results
PS C:\Users\Pranoti munjankar\OneDrive\Desktop\iit tirupati\PROJECT\project3> python -m pytest 04_scripts -q                         
.........                                                                                                                     [100%]
9 passed in 41.19s
PS C:\Users\Pranoti munjankar\OneDrive\Desktop\iit tirupati\PROJECT\project3> python 04_scripts/27_proper_scoring_and_influence.py --boot 1000
  score contrast   delta  ci95_lo  ci95_hi     se  share_boot_worse
logloss      B-A  0.0007  -0.0007   0.0018 0.0007             0.814
  brier      B-A  0.0001  -0.0000   0.0002 0.0001             0.921
logloss      C-A -0.0002  -0.0004   0.0001 0.0001             0.107
  brier      C-A -0.0000  -0.0000   0.0000 0.0000             0.506
logloss      D-A  0.0005  -0.0009   0.0017 0.0007             0.758
  brier      D-A  0.0001  -0.0000   0.0002 0.0001             0.917
model  slope  slope_lo  slope_hi  intercept_in_the_large  int_lo  int_hi
    A  1.030     0.783     1.299                  -0.098   -0.33   0.095
    B  0.881     0.637     1.144                  -0.108   -0.35   0.087
contrast  delta  p_inside_pm0_02  p_inside_pm0_03  p_inside_pm0_05  p_gain_above_0_02  p_gain_above_0_05  p_loss_below_minus_0_02
     B-A  0.001            0.805            0.938            0.994              0.130              0.005                    0.065
     C-A  0.003            1.000            1.000            1.000              0.000              0.000                    0.000
     D-A  0.003            0.786            0.926            0.993              0.156              0.006                    0.058
leave-one-disease-out B-A range: -0.0043 to +0.0058
Wrote 00_docs/23_proper_scoring_results.md and 05_results/tables/adv2_*.csv
PS C:\Users\Pranoti munjankar\OneDrive\Desktop\iit tirupati\PROJECT\project3> @"
>> 
>> ## Deviation 2026-11-12: second advanced layer (exploratory, after advanced-freeze)
>> 
>> **What changed.** Script 27 added proper scoring rules, calibration intervals, bootstrap probability statements and a leave-one-disease-out check. It uses only the saved stage 1 out-of-sample predictions. It does not change the primary outcome, models A to D or the validation design, and it was not in the pre-registered plan.
>> 
>> **Results.**
>> - Log-loss B-A +0.0007 (95% CI -0.0007 to +0.0018); C-A -0.0002 (-0.0004 to +0.0001); no interval excludes zero.
>> - Calibration slope A 1.030 and B 0.881 (95% CI 0.637 to 1.144); intercept in the large -0.098 (A) and -0.108 (B). Over-confidence of B is not demonstrated.
>> - Share of bootstrap draws with B-A inside +/-0.03 AUC: 0.94; probability of a gain above 0.05: 0.005 (bootstrap shares, not posterior probabilities).
>> - Leave-one-disease-out B-A ranges from -0.0043 to +0.0058; no interval excludes zero.
>> 
>> **Correction.** The earlier supplementary table reported a B calibration intercept of -0.524 (free-slope fit). That figure is not comparable to the fixed-slope intercept above and should not be described as miscalibration.
>> 
>> **Impact on conclusions.** None. The finding remains no evidence of gain within the detectable range.
>> "@ | Add-Content -Path 00_docs/07_deviations_log.md -Encoding UTF8
PS C:\Users\Pranoti munjankar\OneDrive\Desktop\iit tirupati\PROJECT\project3> powershell -ExecutionPolicy Bypass -File tools/run_advanced.ps1 