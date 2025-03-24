# models.py
from extensions import db

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(50), nullable=False)
    emp_name = db.Column(db.String(100), nullable=False)
    commodity = db.Column(db.String(100), nullable=False)
    brand_model = db.Column(db.String(100), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    given_date = db.Column(db.Date, nullable=False)
    return_update_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False)  # "Active", "Faulty", "Offline"

class License(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(50), nullable=False)
    emp_name = db.Column(db.String(100), nullable=False)
    license_count = db.Column(db.Integer, nullable=False)
    license_brand = db.Column(db.String(100), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    activated_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # "Active", "Near Expiry", "Expired"
