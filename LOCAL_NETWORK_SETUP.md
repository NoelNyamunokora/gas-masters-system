# Running Gas Masters on Local Network

## Overview
You can run the Gas Masters system on your PC and allow other computers on the same network (WiFi/LAN) to access it.

## Prerequisites
- Python installed on your PC
- All project files on your PC
- MySQL or PostgreSQL database (or use SQLite for testing)
- All computers on the same WiFi/LAN network

## Setup Instructions

### Step 1: Install Dependencies
Open Command Prompt or PowerShell in your project folder:
```bash
pip install -r requirements.txt
```

### Step 2: Configure Database

#### Option A: Use SQLite (Easiest - No Database Server Needed)
1. Open `config.py`
2. The fallback is already set to SQLite
3. No additional setup needed!

#### Option B: Use MySQL (If you have MySQL installed)
1. Create a `.env` file in your project folder
2. Add these lines:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=gas_masters
SECRET_KEY=your-secret-key-here
```

3. Create the database:
```sql
CREATE DATABASE gas_masters;
```

### Step 3: Find Your PC's IP Address

#### On Windows:
1. Open Command Prompt
2. Type: `ipconfig`
3. Look for "IPv4 Address" under your active network adapter
4. Example: `192.168.1.100`

#### On Mac/Linux:
1. Open Terminal
2. Type: `ifconfig` or `ip addr`
3. Look for your local IP address
4. Example: `192.168.1.100`

### Step 4: Run the Application

#### Method 1: Using Flask Development Server
Open Command Prompt in your project folder:
```bash
python app.py
```

The app will start on `http://127.0.0.1:5000`

#### Method 2: Make it Accessible on Network
Modify the last line in `app.py`:

Change from:
```python
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

To:
```python
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
```

This makes the app accessible from other computers on your network.

### Step 5: Access from Other Computers

#### On Your PC:
- Visit: `http://localhost:5000`
- Or: `http://127.0.0.1:5000`

#### On Other Computers (Same Network):
- Visit: `http://YOUR_PC_IP:5000`
- Example: `http://192.168.1.100:5000`

Replace `YOUR_PC_IP` with the IP address you found in Step 3.

### Step 6: Initialize Database (First Time Only)
1. Visit the app in your browser
2. Go to: `http://YOUR_PC_IP:5000/init-database-emergency`
3. This will create all tables and the admin user
4. Login with: `admin` / `admin123`

## Firewall Configuration

If other computers can't access the app, you may need to allow it through your firewall:

### Windows Firewall:
1. Open "Windows Defender Firewall"
2. Click "Advanced settings"
3. Click "Inbound Rules" → "New Rule"
4. Select "Port" → Next
5. Select "TCP" and enter port `5000`
6. Allow the connection
7. Apply to all profiles (Domain, Private, Public)
8. Name it "Gas Masters App"

### Alternative: Temporarily Disable Firewall (Not Recommended)
Only for testing - remember to re-enable it!

## Using Production Server (Recommended for Multiple Users)

For better performance with multiple users, use Gunicorn:

### Install Gunicorn:
```bash
pip install gunicorn
```

### Run with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

This runs 4 worker processes for better performance.

## Network Access Summary

| Location | URL to Use |
|----------|------------|
| Your PC | `http://localhost:5000` |
| Same WiFi/LAN | `http://192.168.1.100:5000` (use your actual IP) |
| Internet (Render) | `https://your-app.onrender.com` |

## Troubleshooting

### Problem: Other computers can't connect
**Solutions:**
1. Check firewall settings (see above)
2. Verify you're using `host='0.0.0.0'` in app.run()
3. Confirm all computers are on the same network
4. Try pinging your PC from other computers: `ping 192.168.1.100`

### Problem: App is slow with multiple users
**Solutions:**
1. Use Gunicorn instead of Flask development server
2. Increase worker processes: `gunicorn -w 8 -b 0.0.0.0:5000 wsgi:app`
3. Use a proper database (MySQL/PostgreSQL) instead of SQLite

### Problem: Database locked (SQLite)
**Solution:**
SQLite doesn't handle concurrent writes well. Switch to MySQL or PostgreSQL for multiple users.

### Problem: IP address keeps changing
**Solution:**
Set a static IP for your PC in your router settings.

## Best Practices

### For Testing (Few Users):
- Use SQLite database
- Run with Flask development server
- Access via local network only

### For Production (Many Users):
- Use MySQL or PostgreSQL database
- Run with Gunicorn (4-8 workers)
- Consider deploying to Render for internet access
- Set up proper backups

### Security Notes:
- Change default admin password immediately
- Don't expose to the internet without proper security
- Use HTTPS if accessing over internet
- Keep your PC running while others need access
- Consider using Render for 24/7 availability

## Quick Start Commands

### Start the app (accessible on network):
```bash
# Development mode
python app.py

# Production mode (better for multiple users)
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

### Stop the app:
Press `Ctrl+C` in the terminal

### Access URLs:
- Your PC: `http://localhost:5000`
- Other computers: `http://YOUR_PC_IP:5000`
- Initialize DB: `http://YOUR_PC_IP:5000/init-database-emergency`

## Comparison: Local vs Render

| Feature | Local Network | Render (Cloud) |
|---------|---------------|----------------|
| Cost | Free | Free tier available |
| Access | Same network only | Internet (anywhere) |
| Uptime | Only when PC is on | 24/7 |
| Performance | Depends on PC | Consistent |
| Setup | Quick | Requires deployment |
| Database | Local (SQLite/MySQL) | PostgreSQL |
| Best For | Testing, small office | Production, remote access |

## Recommendation

- **For testing/development**: Run locally on your network
- **For production use**: Deploy to Render for 24/7 access
- **For office use**: Run locally during work hours, or use Render for always-on access
