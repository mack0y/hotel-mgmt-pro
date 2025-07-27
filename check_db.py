# check_db.py
from app import create_app, db
from app.models import User, Room

app = create_app()

with app.app_context():
    print("\n🔍 Users:")
    for user in User.query.all():
        print(f"  ID={user.id} | {user.username} ({user.role})")

    print("\n🛏️ Rooms:")
    for room in Room.query.all():
        print(f"  Room {room.room_number} | {room.room_type} | ${room.price} | {room.status}")