from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Donation
from sqlalchemy import func
from typing import Any
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///donations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager: Any = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize the database (create tables if they don't exist)
with app.app_context():
    db.create_all()
    # Dev-only: seed minimal data so the UI is not empty on first run
    if User.query.count() == 0:
        donor = User()
        donor.username = 'donor1'
        donor.email = 'donor1@example.com'
        donor.role = 'donor'
        donor.set_password('password')

        ngo = User()
        ngo.username = 'ngo1'
        ngo.email = 'ngo1@example.com'
        ngo.role = 'ngo'
        ngo.set_password('password')

        db.session.add_all([donor, ngo])
        db.session.commit()

        sample = Donation()
        sample.product_type = 'Clothes'
        sample.quantity = 10
        sample.donor_id = donor.id
        sample.ngo_id = ngo.id
        db.session.add(sample)
        db.session.commit()

@app.route('/')
def index():
    # Basic dashboard stats for the homepage
    total_donations = Donation.query.count()
    total_quantity = db.session.query(func.sum(Donation.quantity)).scalar() or 0
    ngo_count = User.query.filter_by(role='ngo').count()
    donor_count = User.query.filter_by(role='donor').count()
    recent = Donation.query.order_by(Donation.id.desc()).limit(5).all()
    return render_template('index.html', total_donations=total_donations,
                           total_quantity=total_quantity,
                           ngo_count=ngo_count,
                           donor_count=donor_count,
                           recent=recent)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Support both JSON (AJAX) and form-encoded submissions
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            role = data.get('role')
        else:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role')

        if not username or not email or not password or not role:
            if request.is_json:
                return jsonify({'error': 'Missing fields'}), 400
            else:
                return render_template('register.html', message='Please fill all fields')

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({'error': 'User already exists'}), 400
            return render_template('register.html', message='User already exists')

        user = User()
        user.username = username
        user.email = email
        user.role = role
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        if request.is_json:
            return jsonify({'message': 'Registration successful'}), 201
        # For regular form POST, redirect to login page
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Support both JSON (AJAX) and form-encoded submissions
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            # If AJAX, return JSON with role
            if request.is_json:
                return jsonify({'message': 'Login successful', 'role': user.role}), 200
            # Otherwise redirect based on role
            if user.role == 'donor':
                return redirect(url_for('donate'))
            return redirect(url_for('ngo_view'))

        if request.is_json:
            return jsonify({'error': 'Invalid credentials'}), 401
        return render_template('login.html', message='Invalid credentials')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/donate', methods=['GET', 'POST'])
@login_required
def donate():
    if current_user.role != 'donor':
        return jsonify({'error': 'Only donors can donate'}), 403
    if request.method == 'POST':
        # Accept JSON or form POST
        if request.is_json:
            data = request.get_json()
            product_type = data.get('product_type')
            quantity = data.get('quantity')
            ngo_id = data.get('ngo_id')
        else:
            product_type = request.form.get('product_type')
            quantity = request.form.get('quantity')
            ngo_id = request.form.get('ngo_id')

        if quantity is None or ngo_id is None:
            if request.is_json:
                return jsonify({'error': 'Missing quantity or ngo_id'}), 400
            return render_template('donate.html', ngos=User.query.filter_by(role='ngo').all(), message='Missing input')

        try:
            quantity = int(quantity)
            ngo_id = int(ngo_id)
        except (ValueError, TypeError):
            if request.is_json:
                return jsonify({'error': 'Invalid input'}), 400
            return render_template('donate.html', ngos=User.query.filter_by(role='ngo').all(), message='Invalid input')

        donation = Donation()
        donation.product_type = product_type
        donation.quantity = quantity
        donation.donor_id = current_user.id
        donation.ngo_id = ngo_id
        db.session.add(donation)
        db.session.commit()
        if request.is_json:
            return jsonify({'message': 'Donation submitted'}), 201
        return redirect(url_for('donor_view'))
    ngos = User.query.filter_by(role='ngo').all()
    return render_template('donate.html', ngos=ngos)

@app.route('/ngo_view')
@login_required
def ngo_view():
    if current_user.role != 'ngo':
        return jsonify({'error': 'Only NGOs can view donations'}), 403
    donations = Donation.query.filter_by(ngo_id=current_user.id).all()
    return render_template('ngo_view.html', donations=donations)


@app.route('/donor_view')
@login_required
def donor_view():
    if current_user.role != 'donor':
        return jsonify({'error': 'Only donors can view their donations'}), 403
    donations = Donation.query.filter_by(donor_id=current_user.id).all()
    return render_template('donor_view.html', donations=donations)

@app.route('/update_status/<int:donation_id>', methods=['POST'])
@login_required
def update_status(donation_id):
    if current_user.role != 'ngo':
        return jsonify({'error': 'Unauthorized'}), 403
    donation = Donation.query.get(donation_id)
    if donation and donation.ngo_id == current_user.id:
        donation.status = 'Received'
        db.session.commit()
        return jsonify({'message': 'Status updated'}), 200
    return jsonify({'error': 'Donation not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)