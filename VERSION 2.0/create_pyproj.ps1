# PS1 script, that creates everything that developer needs in folder, where it is called.

param(
    [string]$VenvName = ".venv",
    [switch]$SkipVenv 
)

function Write-Ok($msg) { Write-Host "[OK]  $msg" -ForegroundColor Green }
function Write-Err($msg) { Write-Host "[ERR] $msg" -ForegroundColor Red }
function Write-Info($msg) { Write-Host "[..]  $msg" -ForegroundColor Cyan }

try {
    $cwd = Get-Location
    Write-Info "Folder: $cwd"

    # 1) Files
    $files = @{
        "README.md" = "# Project"
        "requirements.txt" = ""
        "main.py" = 'if __name__ == "__main__": print("Hello World!")'
        ".gitignore" = ".venv/`n__pycache__/`n*.pyc`n.env`n.envrc"
    }

    foreach ($f in $files.Keys) {
        if (-not (Test-Path -LiteralPath $f)) {
            $content = $files[$f]
            # ensure correct newlines for .py
            if ($f -eq "main.py") {
                $content = 'if __name__ == "__main__":`n    print("Hello World!")'
            }
            Set-Content -LiteralPath $f -Value $content -Encoding UTF8
            Write-Ok "Created $f."
        } else {
            Write-Info "File $f already exists - skipping."
        }
    }

    # 2) data/ folder 
    if (-not (Test-Path -LiteralPath "data")) {
        New-Item -Path "data" -ItemType Directory | Out-Null
        Write-Ok "Created data/ folder."
    } else {
        Write-Info "data/ folder already exists - skipping."
    }

    # 3) virtual-env
    if (-not $SkipVenv) {
        if (-not (Test-Path -LiteralPath $VenvName)) {
            Write-Info "Creating Python Venv in '$VenvName'..."
            $pyExe = "python"
            # перевірка чи python доступний
            try {
                & $pyExe --version > $null 2>&1
            } catch {
                Write-Err "Python was not found in PATH. Install Python and put it in PATH or usr -SkipVenv flag."
                exit 1
            }
            & $pyExe -m venv $VenvName
            if ($LASTEXITCODE -eq 0) {
                Write-Ok "Python Venv created: $VenvName"
                $readmeAdd = "`n## Activating Venv`nWindows: `n```$VenvName\Scripts\Activate.ps1```nLinux/macOS:`n```source $VenvName/bin/activate``` "
                Add-Content -LiteralPath "README.md" -Value $readmeAdd -Encoding UTF8
            } else {
                Write-Err "Failed to create venv (code $LASTEXITCODE)."
            }
        } else {
            Write-Info "Venv '$VenvName' already exists - skipping."
        }
    } else {
        Write-Info "Skipping creating Venv (used -SkipVenv parameter)."
    }

    # 4) git init
    if (-not (Test-Path -LiteralPath ".git")) {
        try {
            & git --version > $null 2>&1
            $gitAvail = $true
        } catch {
            $gitAvail = $false
        }

        if ($gitAvail) {
            git init | Out-Null
            git add . | Out-Null
            git commit -m "Initial commit. " --allow-empty > $null 2>&1
            Write-Ok "Git initialized."
        } else {
            Write-Info "Git was not found in PATH - skipping git init"
        }
    } else {
        Write-Info "Git-repository already exists - skipping."
    }

    # 5) Вивід підсумку
    Write-Host ""
    Write-Host "=====  SUMMARY  =====" -ForegroundColor Yellow
    Write-Host "README.md:   " (Test-Path "README.md")
    Write-Host "requirements: " (Test-Path "requirements.txt")
    Write-Host "main.py:     " (Test-Path "main.py")
    Write-Host ".gitignore:  " (Test-Path ".gitignore")
    Write-Host "data/:       " (Test-Path "data")
    Write-Host "venv:        " (Test-Path $VenvName)
    Write-Host "git repo:    " (Test-Path ".git")
    Write-Host "=====================" -ForegroundColor Yellow

} catch {
    Write-Err $_.Exception.Message
    exit 1
}
