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


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
