# git_freeze.ps1 - make a dated, tamper-evident freeze of stage 1. Run from the project3 folder:
#   powershell -ExecutionPolicy Bypass -File tools/git_freeze.ps1
# Requires git (https://git-scm.com). Raw data and result backups are kept out of the repository.
$ErrorActionPreference = "Stop"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Write-Host "git not found. Install git first."; exit 1 }
$ignore = @"
02_data/raw/
02_data/interim/geography/
05_results_*/
*.bak
__pycache__/
archive/
"@
Set-Content -Path .gitignore -Value $ignore -Encoding utf8
if (-not (Test-Path .git)) { git init | Out-Null }
git add -A
git commit -m "Stage 1 freeze: corrected pipeline, null result, docs" | Out-Null
git tag -f stage1-freeze
Write-Host "Frozen. Commit hash:"
git rev-parse HEAD
Write-Host "Date:"
git log -1 --format=%cd
Write-Host "Write the hash and date into 00_docs/13_stage2_plan.md and 00_docs/04_prereg.md."
