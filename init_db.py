from app import create_app
from extensions import db
from models import User, Depot, Purchase, DepotAllocation, Transaction
from datetime import datetime

def init_database():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                first_name='Admin',
                surname='User',
                phone_number='+1234567890',
                role='manager',
                status='active'  # Admin starts as active
            )
            admin.set_password('admin123')
            admin.approved_at = datetime.utcnow()
            db.session.add(admin)
        
        # Create default filler user
        filler = User.query.filter_by(username='filler1').first()
        if not filler:
            filler = User(
                username='filler1',
                first_name='John',
                surname='Doe',
                phone_number='+1234567891',
                role='filler',
                status='active'  # For demo purposes, make filler active too
            )
            filler.set_password('filler123')
            filler.approved_at = datetime.utcnow()
            db.session.add(filler)
        
        # Create sample depot
        depot = Depot.query.filter_by(name='Main Depot').first()
        if not depot:
            depot = Depot(name='Main Depot', location='Downtown Location', current_inventory=0)
            db.session.add(depot)
        
        db.session.commit()
        print("Database initialized successfully!")
        print("Default users created:")
        print("  Manager: admin / admin123")
        print("  Filler: filler1 / filler123")

if __name__ == '__main__':
    init_database()