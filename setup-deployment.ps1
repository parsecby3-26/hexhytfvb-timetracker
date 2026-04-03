# TimeTracker Complete Deployment Setup Script
# Backend: https://timetracker-api-m8k7.onrender.com

# ============================================
# CONFIGURATION
# ============================================
$BACKEND_URL = "https://timetracker-api-m8k7.onrender.com"
$SUPABASE_DB_URL = "postgresql://postgres.vjjbjyllpedhgtrzivdd:ticksheetpass123@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
$JWT_SECRET = "timetracker-super-secret-jwt-key-2024-production-32chars"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TimeTracker Full Deployment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. UPDATE package.json
if (Test-Path "package.json") {
    $package = Get-Content "package.json" -Raw | ConvertFrom-Json
    $package.scripts.build = "CI=false bun run build"
    $package | ConvertTo-Json -Depth 10 | Set-Content "package.json"
    Write-Host "âœ… Updated package.json: Set CI=false and Bun build" -ForegroundColor Green
}

# 2. CREATE vercel.json
$vercelJsonContent = @"
{
  "buildCommand": "bun run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "regions": ["sin1"],
  "env": {
    "NEXT_PUBLIC_API_URL": "$BACKEND_URL"
  }
}
"@
Set-Content -Path "vercel.json" -Value $vercelJsonContent -Force
Write-Host "âœ… Created vercel.json" -ForegroundColor Green

# 3. UPDATE src/lib/api.ts (The full API logic)
# We use Single Quotes '@ to prevent PowerShell from crashing on ${vars}
$apiContent = @'
import { useAuthStore } from '@/stores/auth-store';

const API_BASE = "https://timetracker-api-m8k7.onrender.com/api";

export class ApiError extends Error {
  statusCode: number;
  constructor(message: string, statusCode: number) {
    super(message);
    this.statusCode = statusCode;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = useAuthStore.getState().token;
  const headers: HeadersInit = { 'Content-Type': 'application/json', ...options.headers };
  if (token) { (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`; }
  
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, { ...options, headers });
  const data = await response.json();

  if (!response.ok) {
    throw new ApiError(data.detail || data.message || 'An error occurred', response.status);
  }
  return data;
}

export const api = {
  get: <T>(endpoint: string) => request<T>(endpoint, { method: 'GET' }),
  post: <T>(endpoint: string, body?: unknown) => request<T>(endpoint, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
  put: <T>(endpoint: string, body?: unknown) => request<T>(endpoint, { method: 'PUT', body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(endpoint: string) => request<T>(endpoint, { method: 'DELETE' }),
};

export const authApi = {
  login: async (email: string, password: string) => {
    const result = await api.post<{ access_token: string; user: any }>('/auth/login', { email, password });
    return {
      profile: {
        id: result.user.id,
        name: `${result.user.first_name} ${result.user.last_name}`,
        email: result.user.email,
        roles: result.user.roles.map((r: any) => ({ id: r.id, value: r.name }))
      },
      token: result.access_token
    };
  },
  me: async () => {
    const user = await api.get<any>('/auth/me');
    return {
      id: user.id,
      name: `${user.first_name} ${user.last_name}`,
      email: user.email,
      roles: user.roles.map((r: any) => ({ id: r.id, value: r.name }))
    };
  }
};

export const projectsApi = {
  list: async () => {
    const projects = await api.get<any[]>('/projects');
    return { projects: projects.map(p => ({ id: p.id, name: p.name, code: p.code, status: p.is_active })) };
  },
  create: (data: { name: string; code: string }) => api.post<any>('/projects', data)
};

export const timeEntriesApi = {
  list: (params?: any) => api.get<any[]>('/time-entries'),
  create: (data: any) => api.post<any>('/time-entries', data)
};
'@

if (-not (Test-Path "src/lib")) { New-Item -ItemType Directory -Path "src/lib" -Force }
Set-Content -Path "src/lib/api.ts" -Value $apiContent -Force
Write-Host "âœ… Updated src/lib/api.ts (Full API Included)" -ForegroundColor Green

# 4. UPDATE backend .env
$envBackendContent = @"
DATABASE_URL=$SUPABASE_DB_URL
JWT_SECRET_KEY=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
"@

if (Test-Path "timetracker-backend") {
    Set-Content -Path "timetracker-backend/.env" -Value $envBackendContent -Force
    Write-Host "âœ… Updated backend .env" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ALL UPDATES APPLIED SUCCESSFULLY" -ForegroundColor Green
Write-Host "Run 'git add .', 'git commit', and 'git push' to deploy." -ForegroundColor White


