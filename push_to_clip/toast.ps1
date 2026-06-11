<#
.SYNOPSIS
  Windows toast notification helper for push-to-clip.

.DESCRIPTION
  Shows a native Windows toast (banner, bottom right). Called by push-to-clip
  after a successful copy, but works standalone too:

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File toast.ps1 `
      -Title "Copied" -Message "1,234 characters" [-Source "..."] [-Target "..."] [-Urgent]

  MUST run under Windows PowerShell 5.1 (powershell.exe) — the WinRT projection
  used here is not available in PowerShell 7 (pwsh).

  Self-registration: Windows only shows toast banners for a registered
  AppUserModelId. This script registers its own AppId under HKCU (no admin
  rights, idempotent) on every run, so installation needs zero manual steps.

  -Urgent: marks the toast as a Windows 11 "important notification"
  (scenario="urgent"), which can break through Do Not Disturb / Focus Assist.
  The very first urgent toast makes Windows ask once ("Allow important
  notifications from push-to-clip?"); after allowing, urgent toasts stay
  visible even while Do Not Disturb is on. Regular toasts are silently routed
  to the Notification Center while Do Not Disturb is active.

  File encoding: UTF-8 WITH BOM (PowerShell 5.1 garbles non-ASCII otherwise).
#>
param(
    [Parameter(Mandatory = $true)][string]$Title,
    [Parameter(Mandatory = $true)][string]$Message,
    [Parameter(Mandatory = $false)][string]$Source = '',
    [Parameter(Mandatory = $false)][string]$Target = '',
    [switch]$Urgent,
    [Parameter(Mandatory = $false)][string]$AppId = 'MoritzV42.PushToClip',
    [Parameter(Mandatory = $false)][string]$DisplayName = 'push-to-clip'
)

function Escape-Xml($s) {
    $s -replace '&', '&amp;' -replace '<', '&lt;' -replace '>', '&gt;'
}

try {
    # 1) Register the AppUserModelId (HKCU, no admin, idempotent). Without this,
    #    Windows accepts the toast but never renders a banner.
    $regPath = "HKCU:\SOFTWARE\Classes\AppUserModelId\$AppId"
    if (-not (Test-Path $regPath)) { New-Item -Path $regPath -Force | Out-Null }
    $current = (Get-ItemProperty -Path $regPath -ErrorAction SilentlyContinue).DisplayName
    if ($current -ne $DisplayName) {
        New-ItemProperty -Path $regPath -Name DisplayName -Value $DisplayName -PropertyType String -Force | Out-Null
    }

    # 2) Build and show the toast.
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

    $routeLine = ''
    if ($Source -or $Target) {
        $parts = @()
        if ($Source) { $parts += "From: $Source" }
        if ($Target) { $parts += ('→ For: ' + $Target) }
        $routeLine = "<text>$(Escape-Xml ($parts -join ' '))</text>"
    }

    $scenario = ''
    if ($Urgent) { $scenario = ' scenario="urgent"' }

    $xml = "<toast$scenario duration=""short""><visual><binding template=""ToastGeneric""><text>$(Escape-Xml $Title)</text><text>$(Escape-Xml $Message)</text>$routeLine</binding></visual></toast>"
    $doc = New-Object Windows.Data.Xml.Dom.XmlDocument
    $doc.LoadXml($xml)

    $toast = New-Object Windows.UI.Notifications.ToastNotification($doc)
    # Drop out of the Notification Center after 5 minutes (banner itself ~5 s).
    $toast.ExpirationTime = [DateTimeOffset]::Now.AddMinutes(5)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($AppId).Show($toast)
    exit 0
} catch {
    Write-Error "toast failed: $_"
    exit 1
}
