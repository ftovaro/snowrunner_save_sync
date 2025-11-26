# Fix null terminators and commit properly to Git
# This ensures the files are stored correctly in the repository

Write-Host "=== Fixing null terminators in SnowRunner saves ===" -ForegroundColor Green

# 1. Restore files with nulls from backup
Write-Host "`n1. Restoring files from backup..."
Copy-Item "backup\remote\CompleteSave.cfg" -Destination "remote\" -Force
Copy-Item "backup\remote\CommonSslSave.cfg" -Destination "remote\" -Force

# 2. Verify nulls are present
Write-Host "`n2. Verifying null terminators..."
$files = @("CompleteSave.cfg", "CommonSslSave.cfg")
$allGood = $true
foreach ($file in $files) {
    $bytes = [System.IO.File]::ReadAllBytes("remote\$file")
    $hasNull = $bytes[-1] -eq 0
    if ($hasNull) {
        Write-Host "   $file : OK (has null terminator)" -ForegroundColor Green
    } else {
        Write-Host "   $file : MISSING null terminator!" -ForegroundColor Red
        $allGood = $false
    }
}

if (-not $allGood) {
    Write-Host "`nERROR: Files don't have null terminators! Fix backup files first." -ForegroundColor Red
    exit 1
}

# 3. Remove files from Git index and re-add them as binary
Write-Host "`n3. Re-adding files to Git as binary..."
git rm --cached -r remote/*.cfg
git add remote/*.cfg remotecache.vdf

# 4. Add the Python script fix
Write-Host "`n4. Adding merge script fix..."
git add scripts/merge_saves.py

# 5. Commit everything
Write-Host "`n5. Committing changes..."
git commit -m "Fix: Preserve null terminators in save files

- Added .gitattributes to mark .cfg files as binary
- Fixed merge script to add null terminators when saving
- Re-committed save files with proper null bytes
- Required for SnowRunner to load saves correctly"

Write-Host "`n=== Done! Now run: git push ===" -ForegroundColor Green
Write-Host "After pushing, GitHub Actions will preserve nulls correctly." -ForegroundColor Yellow
