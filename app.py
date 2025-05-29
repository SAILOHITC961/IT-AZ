# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from extensions import db
from models import Asset, License
from sqlalchemy import func
import os
from flask import jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')

# ✅ Add your PostgreSQL database config here
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/flask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hardcoded user for now (can later move to DB)
        if username == 'admin' and password == 'password123':
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)

@app.route('/add_asset', methods=['POST'])
def add_asset():
    if 'user' not in session:
        return redirect(url_for('login'))

    emp_name = request.form.get('emp_name')
    commodity = request.form.get('commodity')
    brand_model = request.form.get('brand_model')
    qty = request.form.get('qty')
    given_date = request.form.get('given_date')
    return_update_date = request.form.get('return_update_date')
    status = request.form.get('status')
    emp_id = request.form.get('emp_id')

    new_asset = Asset(
        emp_name=emp_name,
        commodity=commodity,
        brand_model=brand_model,
        qty=int(qty),
        given_date=datetime.strptime(given_date, '%Y-%m-%d') if given_date else None,
        return_update_date=datetime.strptime(return_update_date, '%Y-%m-%d') if return_update_date else None,
        status=status,
        emp_id=emp_id
    )

    db.session.add(new_asset)
    db.session.commit()

    return redirect(url_for('dashboard'))
@app.route('/delete_asset/<int:asset_id>', methods=['POST'])
def delete_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    db.session.delete(asset)
    db.session.commit()
    return redirect(url_for('dashboard'))
    
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Fetch all assets
    assets = Asset.query.order_by(Asset.id.desc()).all()


    # Data for pie chart - count of each commodity
    commodity_counts = db.session.query(Asset.commodity, func.count().label('count'))\
                                 .group_by(Asset.commodity).all()

    # Data for pie chart - count of each status
    status_counts = db.session.query(Asset.status, func.count().label('count'))\
                              .group_by(Asset.status).all()

    # Convert query results to dicts
    commodity_data = {c[0]: c[1] for c in commodity_counts}
    status_data = {s[0]: s[1] for s in status_counts}

    return render_template('hardware.html',
                           assets=assets,
                           commodity_data=commodity_data,
                           status_data=status_data)

@app.route('/licenses')
def licenses():
    if 'user' not in session:
        return redirect(url_for('login'))

    licenses = License.query.order_by(License.id.desc()).all()

    # Pie chart data
    status_counts = db.session.query(License.status, func.count().label('count'))\
                              .group_by(License.status).all()
    brand_counts = db.session.query(License.license_brand, func.count().label('count'))\
                             .group_by(License.license_brand).all()

    status_data = {s[0]: s[1] for s in status_counts}
    brand_data = {b[0]: b[1] for b in brand_counts}

    return render_template('licenses.html',
                           licenses=licenses,
                           status_data=status_data,
                           brand_data=brand_data)
@app.route('/add_license', methods=['POST'])

def add_license():
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        emp_name = request.form['emp_name']
        license_brand = request.form['license_brand']
        qty = int(request.form['qty']) if request.form['qty'] else 1
        activated_date = request.form['activated_date']
        expiry_date = request.form['expiry_date']
        status = request.form['status']
        emp_id = request.form['emp_id']

        # Convert date strings to actual datetime.date objects
        activated_date = datetime.strptime(activated_date, '%Y-%m-%d').date() if activated_date else None
        expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date() if expiry_date else None

        new_license = License(
            emp_name=emp_name,
            license_brand=license_brand,
            qty=qty,
            activated_date=activated_date,
            expiry_date=expiry_date,
            status=status,
            emp_id=emp_id
        )

        db.session.add(new_license)
        db.session.commit()
        return redirect(url_for('licenses'))

    except Exception as e:
        print("Error while adding license:", e)
        return "Bad Request", 400

@app.route("/update_license/<int:id>", methods=["POST"])
def update_license(id):
    license = License.query.get_or_404(id)
    license.emp_name = request.form["emp_name"]
    license.license_brand = request.form["license_brand"]
    license.qty = request.form["qty"]
    license.activated_date = request.form["activated_date"]
    license.expiry_date = request.form["expiry_date"]
    license.status = request.form["status"]
    license.emp_id = request.form["emp_id"]

    db.session.commit()
    return redirect("/licenses")

@app.route('/delete_license/<int:license_id>', methods=['POST'])
def delete_license(license_id):
    license = License.query.get_or_404(license_id)
    db.session.delete(license)
    db.session.commit()
    return redirect(url_for('licenses'))
                           
@app.route("/update_asset/<int:id>", methods=["POST"])
def update_asset(id):
    asset = Asset.query.get_or_404(id)

    asset.emp_name = request.form["emp_name"]
    asset.commodity = request.form["commodity"]
    asset.brand_model = request.form["brand_model"]
    asset.qty = int(request.form["qty"]) if request.form["qty"] else 1

    given_date = request.form.get("given_date")
    return_update_date = request.form.get("return_update_date")
    asset.given_date = datetime.strptime(given_date, "%Y-%m-%d") if given_date else None
    asset.return_update_date = datetime.strptime(return_update_date, "%Y-%m-%d") if return_update_date else None

    asset.status = request.form["status"]
    asset.emp_id = request.form["emp_id"]

    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
