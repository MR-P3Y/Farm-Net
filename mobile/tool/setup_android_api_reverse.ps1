[CmdletBinding()]
param(
    [ValidateRange(1, 65535)]
    [int]$Port = 8000
)

$ErrorActionPreference = 'Stop'

$adbCandidates = @()

if ($env:ANDROID_SDK_ROOT) {
    $adbCandidates += Join-Path $env:ANDROID_SDK_ROOT 'platform-tools\adb.exe'
}

if ($env:ANDROID_HOME) {
    $adbCandidates += Join-Path $env:ANDROID_HOME 'platform-tools\adb.exe'
}

$adbCandidates += Join-Path $env:LOCALAPPDATA 'Android\Sdk\platform-tools\adb.exe'

$adbPath = $adbCandidates |
    Where-Object { Test-Path -LiteralPath $_ } |
    Select-Object -First 1

if (-not $adbPath) {
    throw 'adb.exe was not found. Install Android SDK Platform-Tools or set ANDROID_SDK_ROOT.'
}

$deviceIds = & $adbPath devices |
    Select-String -Pattern '^(\S+)\s+device(?:\s|$)' |
    ForEach-Object { $_.Matches[0].Groups[1].Value }

if (-not $deviceIds) {
    Write-Host 'No authorized Android device or emulator is connected.'
    exit 0
}

foreach ($deviceId in $deviceIds) {
    & $adbPath -s $deviceId reverse "tcp:$Port" "tcp:$Port" | Out-Null

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to reverse TCP port $Port for Android device $deviceId."
    }

    Write-Host "Android device ${deviceId}: localhost:$Port -> Windows localhost:$Port"
}
