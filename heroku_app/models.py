from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Create class User
class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(100), primary_key=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)

# Create class User
class Property(db.Model):
    __tablename__ = 'properties'
    pid = db.Column(db.String(10), primary_key=True, nullable=False)
    mlsnumber = db.Column(db.String(50), nullable=False)


# Create class Condo
class Condo(db.Model):
    __tablename__ = 'condos'
    mlsnum = db.Column(db.String(50), primary_key=True, nullable=False)
    display_x = db.Column(db.Float, nullable=False)
    display_y = db.Column(db.Float, nullable=False)
    beds = db.Column(db.Float, nullable=False)
    baths = db.Column(db.Float, nullable=False)
    sqft = db.Column(db.Float, nullable=False)
    ppsf = db.Column(db.Float, nullable=False)
    photo_url = db.Column(db.String(2500), nullable=False)
    list_price = db.Column(db.Float, nullable=True)
    predicted_price = db.Column(db.Float, nullable=True)
    remarks = db.Column(db.String(2000), nullable=False)

