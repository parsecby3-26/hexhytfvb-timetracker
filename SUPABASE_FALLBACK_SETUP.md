# Supabase Fallback Setup Guide

## Overview
This setup allows the frontend to connect directly to Supabase when the backend is unavailable. It's useful for:
- Backend maintenance or downtime
- Development/testing without running the backend
- Emergency access to data
- Disaster recovery scenarios

## Setup Steps

### 1. Install Supabase Client
```bash
npm install @supabase/supabase-js
```

### 2. Get Supabase Credentials
Get these from your Supabase dashboard:
- **Project URL**: `https://<project-id>.supabase.co`
- **Anon Key**: Public API key (safe to expose in frontend)

### 3. Configure Environment Variables
Add to your `.env` file:
```
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key
REACT_APP_ENABLE_SUPABASE_FALLBACK=true
```

### 4. Update API Configuration
To use the fallback in your components, import from the new service:

**Before:**
```javascript
import { timeEntriesAPI } from '../services/api';
```

**After:**
```javascript
import { apiWithFallback } from '../lib/apiWithFallback';
// Then use: apiWithFallback.timeEntriesAPI or individual methods
```

## Important Security Considerations

⚠️ **Direct database access bypasses backend security:**

1. **Row-Level Security (RLS)**: You MUST set up Supabase RLS policies to restrict data access
2. **Data Exposure**: Database schema is visible to frontend users
3. **No Business Logic**: Backend validations and custom logic are skipped
4. **Limited Control**: Can't implement complex authorization rules

### Recommended RLS Policies

Enable RLS on all tables and add policies like:

```sql
-- Time Entries: Users can only see their own entries (or manager/admin can see team)
CREATE POLICY "Users can view own entries" ON time_entries
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Managers can view team entries" ON time_entries
  FOR SELECT USING (
    SELECT parent_id = auth.uid() FROM users WHERE id = user_id
  );

-- Projects: All authenticated users can read
CREATE POLICY "Authenticated users can read projects" ON projects
  FOR SELECT USING (TRUE);

-- Users: Users can only read their own profile
CREATE POLICY "Users can read own profile" ON users
  FOR SELECT USING (id = auth.uid());
```

## Features

### Automatic Fallback
When enabled, the system will:
1. Try to reach the backend API first
2. If timeout or error occurs (5 second timeout), attempt Supabase connection
3. Use direct Supabase queries if backend is down
4. Log all fallback attempts

### Timeout Configuration
Edit `API_TIMEOUT` in `apiWithFallback.js` to change the wait time before fallback.

### Logging
Check browser console for:
- `Backend timeout/error, trying Supabase:` - Indicates fallback is active
- `Supabase fallback failed:` - Both backend and Supabase failed
- `Supabase client not available` - Credentials not configured

## Supported Operations

### Currently Implemented
- ✅ Get time entries
- ✅ Create time entries
- ✅ Get projects
- ✅ Get users
- ✅ Get reports (approved entries)

### Not Implemented (would need backend logic)
- ❌ Approve/reject time entries (complex workflows)
- ❌ Complex reports with calculations
- ❌ User role management
- ❌ Project member assignments

## Testing

### Test Backend Failure
```javascript
// In DevTools Console
localStorage.setItem('DEBUG_BACKEND_DOWN', 'true');
```

### Test Without Backend
1. Don't start the backend server
2. Set `REACT_APP_ENABLE_SUPABASE_FALLBACK=true`
3. Refresh the page
4. Try creating/viewing time entries

## Limitations

1. **Real-time Updates**: Won't have real-time sync like a production backend
2. **Calculations**: Aggregate calculations need to be done on frontend
3. **Complex Logic**: No access to stored procedures or complex business rules
4. **Performance**: Direct database queries might be slower
5. **Concurrent Updates**: Limited conflict resolution for simultaneous edits

## When to Use

✅ **Good Use Cases:**
- Development/testing
- Emergency read-only access
- Staff working during backend maintenance
- Disaster recovery scenarios

❌ **Not Recommended:**
- Primary production access method
- Complex workflows requiring validation
- High-volume operations
- Applications requiring strict audit trails

## Rollback

To disable Supabase fallback:
```bash
# Set environment variable to false
REACT_APP_ENABLE_SUPABASE_FALLBACK=false
```

Or remove the Supabase credentials from `.env`.

## Troubleshooting

**"Supabase client not available"**
- Check `.env` file has credentials
- Verify `REACT_APP_ENABLE_SUPABASE_FALLBACK=true`
- Restart dev server after env changes

**"Not authenticated"**
- Login through the app first
- Token must be stored in localStorage

**"Connection failed"**
- Check Supabase URL and key are correct
- Verify RLS policies allow the operation
- Check browser console for detailed errors

**"Timeout errors"**
- Increase `API_TIMEOUT` in `apiWithFallback.js`
- Check network connectivity
- Verify Supabase is online
