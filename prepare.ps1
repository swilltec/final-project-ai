$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host 'Installing Ollama using its official Windows installer...'
    $installer = Invoke-RestMethod -Uri 'https://ollama.com/install.ps1'
    Invoke-Expression $installer
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
        [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + $env:Path
    $ollamaDirectory = Join-Path $env:LOCALAPPDATA 'Programs\Ollama'
    $env:Path = "$ollamaDirectory;$env:Path"
    if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
        throw 'Ollama was installed but is not on PATH. Open a new terminal and rerun prepare.ps1.'
    }
}

# Reuse an existing server when available; otherwise start one for this user.
& ollama list 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    $logs = Join-Path $PSScriptRoot 'exercises\downloads'
    New-Item -ItemType Directory -Force -Path $logs | Out-Null
    $server = Start-Process -FilePath (Get-Command ollama).Source -ArgumentList 'serve' `
        -PassThru -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logs 'ollama.log') `
        -RedirectStandardError (Join-Path $logs 'ollama-error.log')
    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        Start-Sleep -Seconds 1
        & ollama list 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { $ready = $true; break }
        if ($server.HasExited) { break }
    }
    if (-not $ready) { throw 'Ollama did not start. Check exercises\downloads\ollama-error.log.' }
}

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 -m venv .venv
} else {
    & python -m venv .venv
}
if ($LASTEXITCODE -ne 0) { throw 'Could not create the virtual environment. Install Python 3 first.' }

$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
& $python -m pip install 'torch==2.6.0' --index-url 'https://download.pytorch.org/whl/cpu'
if ($LASTEXITCODE -ne 0) { throw 'Could not install CPU PyTorch.' }
& $python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Could not install the Python dependencies.' }
& $python -m exercises.utils
if ($LASTEXITCODE -ne 0) { throw 'Could not prepare the exercise resources.' }
Write-Host 'Ready. Run the exercises with .venv\Scripts\python.exe main.py'
