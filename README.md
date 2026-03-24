# Gas Masters - LP Gas Refilling System

A comprehensive Flask-based system for managing LP gas refilling operations with role-based access control, account approval workflow, and enterprise-grade security. LP Gas is measured in kilograms (kg).

## 🔒 Security & Performance - March 2024 Update

### ✅ Security Enhancements
- **Auto-Logout Feature**: Session timeout with 5-minute warning popup
- **Updated Dependencies**: All packages updated to latest stable versions
- **SQL Injection Prevention**: Custom validators and input sanitization
- **Enhanced Password Security**: Minimum 8 characters with complexity requirements
- **Security Headers**: HSTS, XSS Protection, Content-Type Options
- **Session Security**: 1-hour timeout, secure cookies, HttpOnly, SameSite
- **CSRF Protection**: Enabled on all forms
- **Error Handling**: Custom handlers with database rollback
- **Logging System**: Production-ready rotating file logs

### ⚡ Performance Optimizations
- **Waste/Loss Tracking**: Real-time inventory discrepancy detection
- **Database Connection Pooling**: Efficient connection management
- **CDN-Hosted Assets**: Fast loading of Bootstrap and Font Awesome
- **Responsive Design**: Optimized for all screen sizes
- **Clean Architecture**: Modular blueprint-based structure
- **Consolidated Documentation**: Single comprehensive guide
- **No Unnecessary Files**: Streamlined codebase

## 🚀 Features

### Enhanced Authentication & Security
- **Modern Login/Register Screens** with Gas Masters branding
- **Account Approval Workflow** - All new registrations require manager approval
- **Status-Based Access Control** - Only active accounts can access the system
- **User Management Dashboard** for managers to approve/deactivate accounts
- **Strong Password Requirements** - Uppercase, lowercase, and numbers required

### User Account Statuses
- **Pending**: New registrations awaiting approval
- **Active**: Approved users with full system access
- **Inactive**: Deactivated users (can be reactivated by managers)

## 👥 User Roles & Permissions

### Operators (Fillers)
- Record gas dispensing transactions
- View transaction history
- View total sales by date
- Monitor waste/loss tracking with color-coded alerts
- Assigned to specific depot
- **Requires manager approval** to access system

### Managers  
- Full system access
- **User Management**: Approve, deactivate, and manage user accounts
- Depot management and inventory tracking
- Purchase recording and allocation
- Comprehensive reporting (Balance Sheet, Depot Reports)
- **Requires manager approval** (except default admin)

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL 5.7+ or MariaDB 10.3+
- pip (Python package manager)

### Step 1: Clone or Download
```bash
git clone <repository-url>
cd gas-masters
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
1. Copy `.env.example` to `.env` (if provided) or create `.env`:
```env
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True

DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=your-password
DB_NAME=gas_masters
```

2. **IMPORTANT**: Change the SECRET_KEY to a strong random value for production

### Step 5: Add Your Logo
- Place your `logo.png` file in the `static/` directory
- Recommended size: 200x200 pixels or larger
- PNG format with transparent background preferred

### Step 6: Initialize Database
```bash
python init_db.py
```

### Step 7: Run the Application
```bash
# Development
python start_app.py

# Production (with Gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

### Step 8: Access the System
- URL: http://localhost:5000 (development)
- Default Manager: `admin` / `admin123`
- Default Filler: `filler1` / `filler123`

## 📊 System Features

### Core Functionality
- **Transaction Management**: Record gas dispensing with automatic inventory updates
- **Multi-Depot Support**: Manage multiple depot locations
- **Purchase Tracking**: Record gas purchases from suppliers
- **Allocation Management**: Allocate gas from purchases to depots
- **Real-time Inventory**: Monitor stock levels with low-stock alerts
- **Daily Sales Reports**: View sales by date with filtering
- **Balance Sheet**: Track purchases (IN) and dispensing (OUT)
- **Depot Reports**: Monthly inventory and transaction reports

### Security Features
- Role-based access control (RBAC)
- Account status verification
- Session management with timeout
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection
- Secure password hashing (PBKDF2)

### User Experience
- Modern purple gradient theme
- Responsive design (desktop, tablet, mobile)
- Frosted glass sidebar navigation
- Collapsible mobile menu
- Live search and filtering
- Auto-submit date filters
- Flash messages for user feedback
- Floating logo animations

## 🗄️ Database Schema

### Tables
1. **users** - User accounts with roles and status
2. **depots** - Gas depot locations and inventory
3. **transactions** - Gas dispensing records
4. **purchases** - Gas purchase records
5. **depot_allocations** - Gas allocation to depots

### Relationships
- Users → Transactions (one-to-many)
- Depots → Transactions (one-to-many)
- Depots → Allocations (one-to-many)
- Users → Depots (assigned depot for operators)

## 🔐 Security Best Practices

### For Production Deployment
1. **Change SECRET_KEY** to a strong random value
2. **Set FLASK_ENV=production** and **FLASK_DEBUG=False**
3. **Use HTTPS/TLS** with valid SSL certificates
4. **Strong database password** and restrict access
5. **Configure firewall** rules
6. **Enable logging** and monitoring
7. **Regular backups** of database
8. **Keep dependencies updated**

See `SECURITY.md` for detailed security documentation.

## 📈 Performance Tips

### Database
- Connection pooling enabled (10 connections, 20 max overflow)
- Connection pre-ping for stale connection handling
- Indexed foreign keys for faster queries

### Frontend
- CDN-hosted libraries (Bootstrap, Font Awesome)
- Minimal inline CSS
- Optimized images
- Responsive design

See `OPTIMIZATION.md` for detailed optimization guide.

## 📱 User Interface

### Desktop
- Full sidebar navigation
- Multi-column layouts
- Hover effects and animations
- Comprehensive dashboards

### Tablet
- Collapsible sidebar
- Responsive grid layouts
- Touch-friendly buttons
- Optimized spacing

### Mobile
- Hamburger menu
- Single-column layouts
- Full-height sidebar
- Touch-optimized controls

## 🚦 Getting Started Guide

### First Time Setup
1. Run initialization script to create database
2. Login as admin (admin/admin123)
3. Create depot locations
4. Record initial gas purchases
5. Allocate gas to depots
6. Create operator accounts
7. Approve operator accounts
8. Assign operators to depots

### Daily Operations
1. **Operators**: Record gas dispensing transactions
2. **Managers**: Monitor inventory levels
3. **Managers**: Approve new user accounts
4. **Managers**: Record new purchases
5. **Managers**: Allocate gas to depots
6. **Managers**: Generate reports

## 🔧 System Requirements

### Minimum
- Python 3.8+
- MySQL 5.7+ or MariaDB 10.3+
- 512MB RAM
- 100MB disk space
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Recommended
- Python 3.10+
- MySQL 8.0+
- 2GB RAM
- 1GB disk space
- SSD storage
- Dedicated server or VPS

## 🚀 Deployment

### Deploy to Render

This application is ready for deployment on Render.com:

1. **Export your database:**
```bash
python export_db.py
```

2. **Push to GitHub:**
```bash
# Windows
deploy_to_github.bat

# Or manually:
git add .
git commit -m "Deploy Gas Masters System"
git remote add origin https://github.com/NoelNyamunokora/gas-masters-system.git
git branch -M main
git push -u origin main
```

3. **Deploy on Render:**
   - See complete guide: `RENDER_DEPLOYMENT_GUIDE.md`
   - Create MySQL database
   - Import your database export
   - Create web service
   - Set environment variables
   - Deploy!

**Live URL:** Your app will be at `https://gas-masters.onrender.com`

---

## 📚 Documentation

- `README.md` - This file (getting started guide)
- `SYSTEM_DOCUMENTATION.md` - Complete system documentation (architecture, database, API, troubleshooting)
- `OPTIMIZATION_SUMMARY.md` - Optimization details and performance metrics

## 🐛 Troubleshooting

### Database Connection Issues
- Verify MySQL is running
- Check database credentials in `.env`
- Ensure database exists: `CREATE DATABASE gas_masters;`
- Check port number (default: 3307)

### Login Issues
- Verify user account is active (not pending/inactive)
- Check password meets requirements (8+ chars, uppercase, lowercase, number)
- Clear browser cookies and try again

### Permission Issues
- Verify user role (manager vs operator)
- Check if operator is assigned to a depot
- Ensure account status is "active"

## 📞 Support

For technical support, security concerns, or feature requests:
- Email: support@gasmasters.com
- Security: security@gasmasters.com
- Developer: Noel Nyamunokora

## 📄 License

© 2026 Gas Masters. All rights reserved.  
Developed By Noel Nyamunokora.

## 🔄 Version History

### Version 1.0.0 (2026-03-24)
- ✅ Auto-logout feature with 5-minute warning popup
- ✅ Waste/loss tracking system with color-coded alerts
- ✅ Consolidated documentation (SYSTEM_DOCUMENTATION.md)
- ✅ Security updates and vulnerability patches
- ✅ Performance optimizations
- ✅ Enhanced input validation
- ✅ Updated dependencies to latest versions
- ✅ Improved error handling and logging
- ✅ Database connection pooling
- ✅ Security headers implementation
- ✅ Removed 8 redundant documentation files

### Previous Versions
- Initial release with core functionality
- User management and approval workflow
- Multi-depot support
- Transaction and inventory management
- Reporting features

---

**Status**: Production Ready ✅  
**Last Updated**: 2026-03-24  
**Maintained By**: Noel Nyamunokora
