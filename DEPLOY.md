# Gas Masters - Render Deployment Guide

## 🚀 Quick Deploy (3 Steps)

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Deploy Gas Masters to Render"
git push origin main
```

Or use GitHub Desktop.

---

### Step 2: Create PostgreSQL Database on Render

1. Go to: https://dashboard.render.com
2. Click: **New +** → **PostgreSQL**
3. Settings:
   - Name: `gas-masters-db`
   - Database: `gas_masters`
   - Plan: **Free**
4. Click: **Create Database**
5. Copy: **Internal Database URL** (from Info tab)

---

### Step 3: Create Web Service on Render

1. Click: **New +** → **Web Service**
2. Connect: `gas-masters-system` (from GitHub)
3. Settings:
   - Name: `gas-masters`
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn "app:create_app()"`
   - Plan: **Free**

4. **Environment Variables** (click Advanced):
   ```
   DATABASE_URL = <paste Internal Database URL>
   SECRET_KEY = c162b530d47d6bc2faaf5755f3110bb17d5bfce53397e5367cebd78ddab641d4
   FLASK_ENV = production
   ```

5. Click: **Create Web Service**
6. Wait: 5-10 minutes

---

## ✅ Done!

Your app will be live at: `https://gas-masters.onrender.com`

**Login:**
- Username: `admin`
- Password: `admin123`

**⚠️ Change password immediately after first login!**

---

## 🎯 What Happens Automatically

On first run, the app automatically:
- ✅ Creates all database tables
- ✅ Creates admin user (admin/admin123)
- ✅ Creates sample depot
- ✅ Ready to use!

---

## 🆓 Free Tier Notes

- App spins down after 15 min inactivity
- First request after spin-down: 30-60 seconds
- Database expires after 90 days (backup your data!)

---

## 📞 Need Help?

See: `FREE_TIER_QUICK_START.txt` or `RENDER_FREE_TIER_SETUP.md`

---

**That's it! 3 simple steps to deploy!** 🎉
