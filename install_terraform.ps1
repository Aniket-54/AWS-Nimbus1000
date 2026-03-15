# Terraform Installation Script for Windows
# Run this script to automatically download and install Terraform

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Terraform Installation Script for Windows" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$TerraformVersion = "1.6.6"
$InstallPath = "C:\terraform"
$DownloadUrl = "https://releases.hashicorp.com/terraform/$TerraformVersion/terraform_${TerraformVersion}_windows_amd64.zip"
$ZipFile = "$env:TEMP\terraform.zip"

# Step 1: Create installation directory
Write-Host "Step 1: Creating installation directory..." -ForegroundColor Yellow
if (!(Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    Write-Host "  Created: $InstallPath" -ForegroundColor Green
} else {
    Write-Host "  Directory already exists: $InstallPath" -ForegroundColor Green
}

# Step 2: Download Terraform
Write-Host "`nStep 2: Downloading Terraform $TerraformVersion..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $ZipFile
    Write-Host "  Downloaded successfully!" -ForegroundColor Green
} catch {
    Write-Host "  Error downloading Terraform: $_" -ForegroundColor Red
    Write-Host "`nPlease download manually from: https://www.terraform.io/downloads" -ForegroundColor Yellow
    exit 1
}

# Step 3: Extract ZIP
Write-Host "`nStep 3: Extracting Terraform..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $ZipFile -DestinationPath $InstallPath -Force
    Write-Host "  Extracted to: $InstallPath" -ForegroundColor Green
} catch {
    Write-Host "  Error extracting: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Add to PATH
Write-Host "`nStep 4: Adding Terraform to PATH..." -ForegroundColor Yellow
$CurrentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if ($CurrentPath -notlike "*$InstallPath*") {
    try {
        [Environment]::SetEnvironmentVariable("Path", "$CurrentPath;$InstallPath", "Machine")
        Write-Host "  Added to PATH successfully!" -ForegroundColor Green
        Write-Host "  NOTE: You need to close and reopen your terminal!" -ForegroundColor Yellow
    } catch {
        Write-Host "  Error: Could not add to PATH automatically." -ForegroundColor Red
        Write-Host "  Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
        Write-Host "  Or add manually: $InstallPath" -ForegroundColor Yellow
    }
} else {
    Write-Host "  Already in PATH!" -ForegroundColor Green
}

# Step 5: Cleanup
Write-Host "`nStep 5: Cleaning up..." -ForegroundColor Yellow
Remove-Item $ZipFile -Force -ErrorAction SilentlyContinue
Write-Host "  Cleanup complete!" -ForegroundColor Green

# Step 6: Verify (in current session)
Write-Host "`nStep 6: Verifying installation..." -ForegroundColor Yellow
$TerraformExe = Join-Path $InstallPath "terraform.exe"
if (Test-Path $TerraformExe) {
    Write-Host "  Terraform installed successfully!" -ForegroundColor Green
    Write-Host "  Location: $TerraformExe" -ForegroundColor Cyan
    
    # Test in current session
    & $TerraformExe --version
} else {
    Write-Host "  Error: terraform.exe not found!" -ForegroundColor Red
}

Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "`nIMPORTANT: Close and reopen your terminal, then run:" -ForegroundColor Yellow
Write-Host "  terraform --version" -ForegroundColor Cyan
Write-Host ""
