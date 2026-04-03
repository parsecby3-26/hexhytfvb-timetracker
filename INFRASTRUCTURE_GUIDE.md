# 🛠️ hexhytfvb Infrastructure Setup Guide

Welcome to your new TimeTracker instance! To get your application live, you need to set up several cloud services and connect them using environment variables.

> [!IMPORTANT]
> Use the [setup.html](file:///c:/Users/TICKMARKS/Downloads/timetracker-complete/hexhytfvb-timetracker/setup.html) tool in your project folder to generate your `.env` file easily after following these steps.

---

## 1. 🗄️ Database (Supabase)

1.  **Create Project**: Go to [Supabase](https://supabase.com/) and create a new project named `hexhytfvb-timetracker`.
2.  **Get Connection String**:
    - Go to **Settings → Database**.
    - Find the **Connection string** section.
    - Choose **Node.js** or **Direct** and copy the URI. 
    - It should look like: `postgresql://postgres.[PROJ_ID]:[PASSWORD]@[REGION].pooler.supabase.com:6543/postgres`
    - **Pro Tip**: Use a strong password and keep it handy!
3.  **Run SQL Initializer**: 
    - Go to **SQL Editor** in Supabase.
    - Paste the contents of `backend/alembic/versions/xxxx_initial_migration.py` or use the provided migration scripts.

---

## 2. 📧 Email (Gmail SMTP)

To allow the system to send verification emails and reports:

1.  **Enable 2FA**: Ensure 2-Factor Authentication is ON for your Google Account.
2.  **App Password**: 
    - Go to [App Passwords](https://myaccount.google.com/apppasswords).
    - Give it a name (e.g., "hexhytfvb-timetracker").
    - Copy the **16-character code**.
3.  **Setup Assistant**: Paste this code into the "SMTP Password" field in `setup.html`.

---

## 3. 🚀 Frontend Deployment (Vercel)

1.  **Push to GitHub**: Create a new private repo `hexhytfvb-timetracker` and push your code.
2.  **Connect to Vercel**:
    - Create a new project in [Vercel](https://vercel.com/).
    - Import your GitHub repo.
    - **Build Command**: `CI=false npm run build`
    - **Output Directory**: `build`
3.  **Domain**: Once deployed, copy your `.vercel.app` URL.

---

## 4. ⚙️ Backend Deployment (Render)

1.  **Create Web Service**: In [Render](https://render.com/), create a new **Web Service**.
2.  **Runtime**: Python.
3.  **Build Command**: `pip install -r requirements.txt`
4.  **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
5.  **Environment Variables**: Add all the variables generated for **backend/.env** by `setup.html`.
6.  **Copy URL**: Once deployed, copy the **URL** (e.g., `https://hexhytfvb-api.onrender.com`).

---

## 5. 🔗 Connecting Frontend & Backend

1.  **Vercel Settings**: Go to your Vercel Project → **Settings → Environment Variables**.
2.  **Add Variable**: 
    - **Key**: `REACT_APP_API_URL`
    - **Value**: `[YOUR_RENDER_URL]/api` (e.g., `https://hexhytfvb-api.onrender.com/api`)
3.  **Redeploy**: Trigger a new deployment in Vercel to apply the changes.

---

## ✅ Final Steps

1.  Open [setup.html](file:///c:/Users/TICKMARKS/Downloads/timetracker-complete/hexhytfvb-timetracker/setup.html).
2.  Paste your keys and generate the configuration.
3.  Apply the **Backend .env** to Render/Local Backend.
4.  Apply the **Frontend Variable** to Vercel.
5.  Restart your servers and enjoy your new purple-themed **hexhytfvb TimeTracker**!
