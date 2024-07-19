from api import app, db

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.app_context()