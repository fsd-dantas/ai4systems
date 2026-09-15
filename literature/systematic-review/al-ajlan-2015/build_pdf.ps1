# Render analise-critica.md to PDF: pandoc (Markdown -> HTML) then headless Chrome or Edge (HTML -> PDF).
# Usage: pwsh literature/systematic-review/al-ajlan-2015/build_pdf.ps1

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $here "analise-critica.md"
$css = Join-Path $here "print.css"
$pdf = Join-Path $here "analise-critica.pdf"
$html = Join-Path ([System.IO.Path]::GetTempPath()) "analise-critica.html"

pandoc $source --from markdown --to html5 --standalone --embed-resources `
    --css $css --metadata pagetitle="Analise critica - Al-Ajlan (2015)" --metadata lang=pt-BR `
    --output $html

$browser = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $browser) { throw "Chrome or Edge not found" }

$uri = ([System.Uri]$html).AbsoluteUri
& $browser --headless=new --disable-gpu --no-pdf-header-footer "--print-to-pdf=$pdf" $uri 2>$null | Out-Null
Start-Sleep -Milliseconds 500
if (-not (Test-Path $pdf)) { throw "PDF was not written" }
Write-Output "wrote $pdf"
