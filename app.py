from flask import Flask, render_template, request
from config import Config
from extensions import db, login_manager
import logging
from logging.handlers import RotatingFileHandler
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.session_protection = 'strong'
    
    from models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            app.logger.error(f'Error loading user {user_id}: {str(e)}')
            return None
    
    # Auto-initialize database on first run (for Render free tier)
    # This only creates tables and initial data if they don't exist
    with app.app_context():
        try:
            # Create tables only if they don't exist (safe operation)
            db.create_all()
            app.logger.info('Database tables verified/created')
            
            # Check if we need to create initial admin user (only if no admin exists)
            from models import User, Depot
            admin_exists = User.query.filter_by(username='admin').first()
            
            if not admin_exists:
                app.logger.info('No admin user found - creating initial admin user')
                # Create initial admin user
                from datetime import datetime
                admin = User(
                    username='admin',
                    first_name='Admin',
                    surname='User',
                    phone_number='1234567890',
                    role='manager',
                    status='active',
                    approved_at=datetime.utcnow()
                )
                admin.set_password('admin123')
                db.session.add(admin)
                
                # Check if Main Depot exists before creating
                main_depot_exists = Depot.query.filter_by(name='Main Depot').first()
                if not main_depot_exists:
                    depot = Depot(
                        name='Main Depot',
                        location='Main Location',
                        current_inventory=100.0
                    )
                    db.session.add(depot)
                
                db.session.commit()
                app.logger.info('Database initialized with admin user and sample depot')
            else:
                app.logger.info('Admin user exists - skipping initialization')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Database initialization error: {str(e)}')
            # Continue anyway - don't crash the app
    
    # Enhanced security headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval'; img-src 'self' data: https:;"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Prevent caching for authenticated pages to stop back button access after logout
        if request.endpoint and request.endpoint not in ['auth.login', 'auth.register', 'static']:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, post-check=0, pre-check=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response
    
    # Comprehensive error handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        app.logger.warning(f'Bad request: {request.url}')
        return render_template('error.html', 
                             error_code=400,
                             error_title='Bad Request',
                             error_message='The request could not be understood by the server.'), 400
    
    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f'Forbidden access attempt: {request.url}')
        return render_template('error.html',
                             error_code=403,
                             error_title='Access Denied',
                             error_message='You do not have permission to access this resource.'), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.info(f'Page not found: {request.url}')
        return render_template('error.html',
                             error_code=404,
                             error_title='Page Not Found',
                             error_message='The page you are looking for does not exist.'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Internal server error: {str(error)}')
        return render_template('error.html',
                             error_code=500,
                             error_title='Internal Server Error',
                             error_message='An unexpected error occurred. Please try again later.'), 500
    
    @app.errorhandler(503)
    def service_unavailable_error(error):
        app.logger.error(f'Service unavailable: {str(error)}')
        return render_template('error.html',
                             error_code=503,
                             error_title='Service Unavailable',
                             error_message='The service is temporarily unavailable. Please try again later.'), 503
    
    # Logging configuration (use /tmp for Render compatibility)
    if not app.debug:
        try:
            log_dir = '/tmp/logs' if os.environ.get('RENDER') else 'logs'
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            file_handler = RotatingFileHandler(f'{log_dir}/gas_masters.log', maxBytes=10240000, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Gas Masters startup')
        except Exception as e:
            # If file logging fails, just use console logging
            app.logger.setLevel(logging.INFO)
            app.logger.info(f'File logging disabled: {str(e)}')
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.filler import filler_bp
    from routes.manager import manager_bp
    from routes.reports import reports_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(filler_bp, url_prefix='/filler')
    app.register_blueprint(manager_bp, url_prefix='/manager')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    # Emergency database initialization endpoint
    @app.route('/init-database-emergency')
    def init_database_emergency():
        """Emergency endpoint to force database initialization"""
        try:
            from models import User, Depot, Purchase, DepotAllocation, Transaction
            from datetime import datetime
            
            # Force create all tables
            db.create_all()
            
            # Check if admin exists
            admin_exists = User.query.filter_by(username='admin').first()
            
            if not admin_exists:
                # Create admin user
                admin = User(
                    username='admin',
                    first_name='Admin',
                    surname='User',
                    phone_number='1234567890',
                    role='manager',
                    status='active',
                    approved_at=datetime.utcnow()
                )
                admin.set_password('admin123')
                db.session.add(admin)
                
                # Create Main Depot
                main_depot_exists = Depot.query.filter_by(name='Main Depot').first()
                if not main_depot_exists:
                    depot = Depot(
                        name='Main Depot',
                        location='Main Location',
                        current_inventory=100.0
                    )
                    db.session.add(depot)
                
                db.session.commit()
                return '<h1>✓ Database Initialized Successfully!</h1><p>Admin user created: admin/admin123</p><p>Main Depot created</p><p><a href="/">Go to Login</a></p>', 200
            else:
                return '<h1>✓ Database Already Initialized</h1><p>Admin user already exists</p><p><a href="/">Go to Login</a></p>', 200
                
        except Exception as e:
            db.session.rollback()
            return f'<h1>✗ Database Initialization Failed</h1><p>Error: {str(e)}</p><p>Check Render logs for details</p>', 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    # Run on all network interfaces (0.0.0.0) to allow access from other computers on the network
    # Access from your PC: http://localhost:5000
    # Access from other computers: http://YOUR_PC_IP:5000 (e.g., http://192.168.1.100:5000)
    app.run(host='0.0.0.0', port=5000, debug=True)