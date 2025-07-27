# app/seeds.py
from app import create_app, db
from app.models import User, Room

app = create_app()

with app.app_context():
    db.create_all()

    # Create admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@hotel.com',
            role='admin'
        )
        admin.set_password('admin123')  # Password: admin123
        db.session.add(admin)

    # Add sample rooms
    # Add sample rooms
    if Room.query.count() == 0:
        room_names = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Juliet']
        price = 1500  # PHP - Philippine Peso

        for name in room_names:
            room = Room(
                room_number=name,
                room_type="Standard",
                price=price,
                status="Available"
            )
            db.session.add(room)

        db.session.commit()
        print("✅ Database seeded! Admin user created.")