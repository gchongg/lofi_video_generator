# Simple PowerShell virtualenv setup
# Creates .venv and installs requirements.txt

[CmdletBinding()]
param(
  [string]$VenvDir = ".venv",
  [string]$Requirements = "requirements.txt"
)

function Fail($msg) {
  Write-Error $msg
  exit 1
}

if (-not (Test-Path $Requirements)) {
  Fail "Requirements file not found: $Requirements"
}

# Choose a Python interpreter
$pyCandidates = @('py -3', 'py', 'python3', 'python')
$py = $null
foreach ($c in $pyCandidates) {
  try {
    $version = & $ExecutionContext.InvokeCommand.ExpandString($c) -V 2>$null
    if ($LASTEXITCODE -eq 0 -or $version) { $py = $c; break }
  } catch { }
}
if (-not $py) { Fail "Python not found. Please install Python 3.x." }

Write-Host "Creating virtual environment in $VenvDir ..."
& $ExecutionContext.InvokeCommand.ExpandString($py) -m venv $VenvDir
if ($LASTEXITCODE -ne 0) { Fail "Failed to create virtual environment." }

# Locate venv python
$venvPythonCandidates = @(
  Join-Path $VenvDir "Scripts/python.exe"),
  (Join-Path $VenvDir "Scripts/python"),
  (Join-Path $VenvDir "bin/python")

$venvPy = $null
foreach ($p in $venvPythonCandidates) { if (Test-Path $p) { $venvPy = $p; break } }
if (-not $venvPy) { Fail "Could not locate python inside venv at $VenvDir" }

Write-Host "Upgrading pip/setuptools/wheel ..."
& $venvPy -m pip install --upgrade pip setuptools wheel
if ($LASTEXITCODE -ne 0) { Fail "Failed to upgrade pip in venv." }

Write-Host "Installing dependencies from $Requirements ..."
& $venvPy -m pip install -r $Requirements
if ($LASTEXITCODE -ne 0) { Fail "Failed to install dependencies." }

Write-Host ""
Write-Host "✅ Virtual environment ready: $VenvDir"
Write-Host "Activate with: .\\$VenvDir\\Scripts\\Activate.ps1"
Write-Host "Deactivate with: deactivate"

