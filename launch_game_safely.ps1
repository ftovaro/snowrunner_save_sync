# Safe SnowRunner Launch Script
# This ensures save files are correct before launching

Write-Host "=== SnowRunner Safe Launch ===" -ForegroundColor Cyan

# 1. Check if Steam is running
$steam = Get-Process -Name "steam" -ErrorAction SilentlyContinue
if ($steam) {
    Write-Host "`n⚠️  Steam is running. Please close Steam first!" -ForegroundColor Red
    Write-Host "This prevents Steam Cloud from overwriting the fixed saves." -ForegroundColor Yellow
    Write-Host "`nPress any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# 2. Restore known good backup
Write-Host "`n1. Restoring working backup files..." -ForegroundColor Green
Copy-Item "backup\remote\CommonSslSave.cfg" -Destination "remote\" -Force
Copy-Item "backup\remote\CompleteSave.cfg" -Destination "remote\" -Force

# 3. Verify restoration
Write-Host "`n2. Verifying files..." -ForegroundColor Green
$hash1 = (Get-FileHash "backup\remote\CommonSslSave.cfg").Hash
$hash2 = (Get-FileHash "remote\CommonSslSave.cfg").Hash
$hash3 = (Get-FileHash "backup\remote\CompleteSave.cfg").Hash
$hash4 = (Get-FileHash "remote\CompleteSave.cfg").Hash

if ($hash1 -ne $hash2 -or $hash3 -ne $hash4) {
    Write-Host "   ❌ File restoration failed!" -ForegroundColor Red
    exit 1
}

Write-Host "   ✓ Files restored successfully" -ForegroundColor Green

# 4. Instructions
Write-Host "`n3. Ready to launch!" -ForegroundColor Green
Write-Host "`nIMPORTANT STEPS:" -ForegroundColor Yellow
Write-Host "  1. Launch Steam" -ForegroundColor White
Write-Host "  2. Right-click SnowRunner in your library" -ForegroundColor White
Write-Host "  3. Go to Properties > General" -ForegroundColor White
Write-Host "  4. UNCHECK 'Enable Steam Cloud synchronization'" -ForegroundColor White
Write-Host "  5. Click OK" -ForegroundColor White
Write-Host "  6. Launch SnowRunner" -ForegroundColor White

Write-Host "`nThis prevents Steam Cloud from corrupting your saves." -ForegroundColor Cyan
Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
