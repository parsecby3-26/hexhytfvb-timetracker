# setup-vercel.ps1
# Script to automate environment setup in Vercel for the frontend

$root = Get-Location
$frontendDir = Join-Path $root "frontend"

Write-Host "--- hexhytfvb Vercel Setup ---" -ForegroundColor Cyan

# 1. Initialize Frontend Repo
Write-Host "`nAdding Vercel Environment Variables..." -ForegroundColor Yellow
Set-Location $frontendDir

# Add REACT_APP_API_URL
vercel env add REACT_APP_API_URL production https://hexhytfvb.render.com/api
vercel env add REACT_APP_API_URL preview https://hexhytfvb.render.com/api
vercel env add REACT_APP_API_URL development https://hexhytfvb.render.com/api

Set-Location $root

Write-Host "`nVercel Environment Variables Added." -ForegroundColor Cyan
Write-Host "Next Step: Run 'vercel --prod' in the 'frontend' directory to deploy." -ForegroundColor Yellow
