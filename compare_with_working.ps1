# Compare current files with working snapshot
# Run this if game doesn't load after push/pull

param(
    [string]$SnapshotDir
)

Write-Host "=== Comparing Files with Working Snapshot ===" -ForegroundColor Cyan

# Find the most recent working snapshot if not specified
if (-not $SnapshotDir) {
    $snapshot = Get-ChildItem "working_snapshot_*" | Sort-Object Name -Descending | Select-Object -First 1
    if (-not $snapshot) {
        Write-Host "❌ No working snapshot found!" -ForegroundColor Red
        exit 1
    }
    $SnapshotDir = $snapshot.FullName
}

Write-Host "`nUsing snapshot: $SnapshotDir" -ForegroundColor Yellow

# Compare main save files
Write-Host "`n=== CommonSslSave.cfg ===" -ForegroundColor Cyan
$workingCommon = [System.IO.File]::ReadAllText("$SnapshotDir\remote\CommonSslSave.cfg").TrimEnd([char]0)
$currentCommon = [System.IO.File]::ReadAllText("remote\CommonSslSave.cfg").TrimEnd([char]0)

$workingHash = (Get-FileHash "$SnapshotDir\remote\CommonSslSave.cfg").Hash
$currentHash = (Get-FileHash "remote\CommonSslSave.cfg").Hash

Write-Host "Files match: $($workingHash -eq $currentHash)" -ForegroundColor $(if($workingHash -eq $currentHash){'Green'}else{'Red'})
Write-Host "Working size: $($workingCommon.Length) bytes"
Write-Host "Current size: $($currentCommon.Length) bytes"
Write-Host "Difference: $($currentCommon.Length - $workingCommon.Length) bytes"

# Check structure
$workingSslValuePos = $workingCommon.IndexOf('"SslValue"')
$workingSslTypePos = $workingCommon.IndexOf('"SslType"')
$currentSslValuePos = $currentCommon.IndexOf('"SslValue"')
$currentSslTypePos = $currentCommon.IndexOf('"SslType"')

Write-Host "`nWorking file - SslValue before SslType: $($workingSslValuePos -lt $workingSslTypePos)" -ForegroundColor Green
Write-Host "Current file - SslValue before SslType: $($currentSslValuePos -lt $currentSslTypePos)" -ForegroundColor $(if($currentSslValuePos -lt $currentSslTypePos){'Green'}else{'Red'})

Write-Host "`nFirst 200 chars - Working:"
$workingCommon.Substring(0, 200)
Write-Host "`nFirst 200 chars - Current:"
$currentCommon.Substring(0, 200)

# Check field order
Write-Host "`n=== Field Order Check ===" -ForegroundColor Cyan
$fields = @('objVersion', 'finishedTrials', 'birthVersion', 'achievementStates', 
            'givenProsEntitlements', 'saveSlotsTransaction', 'lastGeneratedId', 
            'platformStatsInfo', 'freezedTrailers')

Write-Host "Working file positions:"
foreach ($field in $fields) {
    $pos = $workingCommon.IndexOf("`"$field`":")
    if ($pos -ge 0) { Write-Host "  $field : $pos" }
}

Write-Host "`nCurrent file positions:"
$currentFieldsCorrect = $true
$lastPos = -1
foreach ($field in $fields) {
    $pos = $currentCommon.IndexOf("`"$field`":")
    if ($pos -ge 0) { 
        $color = if ($pos -gt $lastPos) { 'Green' } else { 'Red'; $currentFieldsCorrect = $false }
        Write-Host "  $field : $pos" -ForegroundColor $color
        $lastPos = $pos
    }
}

Write-Host "`nField order correct: $currentFieldsCorrect" -ForegroundColor $(if($currentFieldsCorrect){'Green'}else{'Red'})

# CompleteSave check
Write-Host "`n=== CompleteSave.cfg ===" -ForegroundColor Cyan
$workingComplete = [System.IO.File]::ReadAllText("$SnapshotDir\remote\CompleteSave.cfg").TrimEnd([char]0)
$currentComplete = [System.IO.File]::ReadAllText("remote\CompleteSave.cfg").TrimEnd([char]0)

$workingHashC = (Get-FileHash "$SnapshotDir\remote\CompleteSave.cfg").Hash
$currentHashC = (Get-FileHash "remote\CompleteSave.cfg").Hash

Write-Host "Files match: $($workingHashC -eq $currentHashC)" -ForegroundColor $(if($workingHashC -eq $currentHashC){'Green'}else{'Red'})
Write-Host "Working size: $($workingComplete.Length) bytes"
Write-Host "Current size: $($currentComplete.Length) bytes"

$workingSslValuePosC = $workingComplete.IndexOf('"SslValue"')
$workingSslTypePosC = $workingComplete.IndexOf('"SslType"')
$currentSslValuePosC = $currentComplete.IndexOf('"SslValue"')
$currentSslTypePosC = $currentComplete.IndexOf('"SslType"')

Write-Host "Working - SslValue before SslType: $($workingSslValuePosC -lt $workingSslTypePosC)" -ForegroundColor Green
Write-Host "Current - SslValue before SslType: $($currentSslValuePosC -lt $currentSslTypePosC)" -ForegroundColor $(if($currentSslValuePosC -lt $currentSslTypePosC){'Green'}else{'Red'})

# Summary
Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
if ($workingHash -eq $currentHash -and $workingHashC -eq $currentHashC) {
    Write-Host "✓ Files are identical to working snapshot" -ForegroundColor Green
} elseif ($currentFieldsCorrect -and ($currentSslValuePos -lt $currentSslTypePos) -and ($currentSslValuePosC -lt $currentSslTypePosC)) {
    Write-Host "✓ Structure is correct but content changed (game progress)" -ForegroundColor Yellow
} else {
    Write-Host "❌ Files are corrupted - structure differs from working snapshot" -ForegroundColor Red
    Write-Host "`nTo restore working files, run:" -ForegroundColor Yellow
    Write-Host "  Copy-Item `"$SnapshotDir\remote\*.cfg`" -Destination `"remote\`" -Force" -ForegroundColor White
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
