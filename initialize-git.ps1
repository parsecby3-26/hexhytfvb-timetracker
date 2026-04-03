# initialize-git.ps1
# Script to initialize and push separate GitHub repositories for Frontend and Backend

$root = Get-Location
$frontendDir = Join-Path $root "frontend"
$backendDir = Join-Path $root "backend"

Write-Host "--- hexhytfvb Git Initializer ---" -ForegroundColor Cyan

# 1. Initialize Frontend Repo
Write-Host "`nSetting up Frontend repository..." -ForegroundColor Yellow
if (Test-Path (Join-Path $frontendDir ".git")) {
    Write-Host "Frontend already has a git repo. Skipping init." -ForegroundColor Gray
} else {
    Set-Location $frontendDir
    git init
    git add .
    git commit -m "initial commit (frontend)"
    Write-Host "Frontend git repo initialized." -ForegroundColor Green
}

# 2. Initialize Backend Repo
Write-Host "`nSetting up Backend repository..." -ForegroundColor Yellow
if (Test-Path (Join-Path $backendDir ".git")) {
    Write-Host "Backend already has a git repo. Skipping init." -ForegroundColor Gray
} else {
    Set-Location $backendDir
    git init
    git add .
    git commit -m "initial commit (backend)"
    Write-Host "Backend git repo initialized." -ForegroundColor Green
}

Set-Location $root

Write-Host "`nGit Repositories Initialized Locally." -ForegroundColor Cyan
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Create two NEW PRIVATE repositories on GitHub (e.g., 'hexhytfvb-frontend' and 'hexhytfvb-backend')."
Write-Host "2. Run these commands manually to push:"
Write-Host "   Frontend:" -ForegroundColor Green
Write-Host "     cd frontend; git remote add origin [YOUR_FRONTEND_URL]; git push -u origin main"
Write-Host "   Backend:" -ForegroundColor Green
Write-Host "     cd backend; git remote add origin [YOUR_BACKEND_URL]; git push -u origin main"
