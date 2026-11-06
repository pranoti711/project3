# cleanup.ps1 - moves stray files into archive/ (nothing is deleted). Run from the project3 folder:
#   powershell -ExecutionPolicy Bypass -File tools/cleanup.ps1
$ErrorActionPreference = "Continue"
$dest = "archive/cleanup_2026-11-05"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
$items = @(
  "text",
  ".tmp_raw_check.txt",
  "04_scripts/01c_build_analysis_panel.py",
  "04_scripts/00_check_raw_data.py"
)
foreach ($i in $items) {
  if (Test-Path -LiteralPath $i) {
    Move-Item -LiteralPath $i -Destination $dest -Force
    Write-Host "moved $i"
  }
  else { Write-Host "not found (skipped): $i" }
}
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Done. Check that python run_from_07.py --dry-run still works, then delete $dest if you like."