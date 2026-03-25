# Render Data Persistence - Important Information

## Why Your Data Disappeared

Your data disappeared because of one of these reasons:

### 1. Render Free Tier Database Limitations
- **Free PostgreSQL databases on Render expire after 90 days**
- After 90 days, the database is deleted and all data is lost
- You need to upgrade to a paid plan for permanent data storage

### 2. Database Connection Issues
- If DATABASE_URL environment variable is not set correctly
- The app might fall back to SQLite (which is temporary on Render)
- SQLite data is lost on every deployment/restart

### 3. Manual Database Reset
- If you manually deleted the database or reset it
- If you changed the DATABASE_URL to a new database

## How to Prevent Data Loss

### Solution 1: Verify DATABASE_URL is Set (CRITICAL)
1. Go to Render Dashboard
2. Click your web service
3. Go to "Environment" tab
4. Verify DATABASE_URL is set to your PostgreSQL Internal Database URL
5. It should look like: `postgresql://user:password@host/database`

### Solution 2: Use Paid PostgreSQL Plan
- Free tier: 90 days, then deleted
- Paid tier: Permanent storage, automatic backups
- Cost: Starting at $7/month for PostgreSQL

### Solution 3: Regular Backups
Create manual backups of your database regularly:

```bash
# From Render Shell (if available on paid tier)
pg_dump $DATABASE_URL > backup.sql

# Or use a backup service
```

### Solution 4: Check Database Status
1. Go to Render Dashboard
2. Click on your PostgreSQL database (not web service)
3. Check "Expires" date
4. If it says "Expires in X days", you're on free tier
5. Upgrade before expiration to keep data

## Current App Configuration

The app is configured to:
- ✓ Only create tables if they don't exist (safe)
- ✓ Only create admin user if no admin exists (safe)
- ✓ Never delete or drop existing data
- ✓ Use PostgreSQL on Render (if DATABASE_URL is set)
- ✓ Fall back to SQLite locally (for development)

## What Changed in Latest Update

I've improved the initialization code to:
1. Add better logging to track what's happening
2. Check if admin exists before creating
3. Check if Main Depot exists before creating
4. Add rollback on errors to prevent corruption
5. Never drop or delete existing data

## How to Check Your Database

### Check if DATABASE_URL is Set:
1. Render Dashboard → Your Service → Environment
2. Look for DATABASE_URL variable
3. Should be: `postgresql://...` (not empty!)

### Check Database Expiration:
1. Render Dashboard → Databases
2. Click your PostgreSQL database
3. Look for "Expires on" date
4. If you see an expiration date, upgrade before that date!

### Check Database Contents:
1. Render Dashboard → Your PostgreSQL Database
2. Click "Connect" → "External Connection"
3. Use a tool like pgAdmin or DBeaver to connect
4. View your tables and data

## Recommended Actions

### Immediate (Do Now):
1. ✓ Verify DATABASE_URL is set in Render environment variables
2. ✓ Check your PostgreSQL database expiration date
3. ✓ If expiring soon, upgrade to paid plan or export data

### Short Term (This Week):
1. Set up regular database backups
2. Consider upgrading to paid PostgreSQL plan ($7/month)
3. Document your database connection details

### Long Term (Best Practice):
1. Use paid PostgreSQL plan for production
2. Set up automated backups
3. Monitor database size and performance
4. Keep a local backup of critical data

## Database Pricing on Render

| Plan | Price | Storage | Retention |
|------|-------|---------|-----------|
| Free | $0 | 1 GB | 90 days (then deleted) |
| Starter | $7/month | 10 GB | Permanent + Backups |
| Standard | $20/month | 50 GB | Permanent + Backups |

## Support

If your data is still disappearing after verifying DATABASE_URL:
1. Check Render logs for database errors
2. Contact Render support
3. Consider migrating to a different database provider

## Summary

Your data disappeared because:
- Render free tier databases expire after 90 days
- OR DATABASE_URL was not set correctly
- OR the database was manually reset

To prevent this:
- ✓ Verify DATABASE_URL is set
- ✓ Check database expiration date
- ✓ Upgrade to paid plan before expiration
- ✓ Set up regular backups

The app code is safe and will NOT delete your data on its own!
