from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from functools import wraps
from bson.objectid import ObjectId
import bcrypt

auth_bp = Blueprint('auth', __name__)

# Initialize MongoDB
mongo = PyMongo()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = mongo.db.users.find_one({'email': email})
    
    if user:
        # Make sure password is stored as bytes in the database
        stored_password = user['password']
        if isinstance(stored_password, str):
            # If it's stored as a string, convert it to bytes
            stored_password = stored_password.encode('utf-8')
            
        if bcrypt.checkpw(password.encode('utf-8'), stored_password):
            session['user_id'] = str(user['_id'])
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect(url_for('admin.admin_panel'))
            elif user['role'] == 'client':
                return redirect(url_for('auth.client_dashboard'))
            return redirect(url_for('home'))
    
    flash('Invalid email or password')
    return redirect(url_for('home'))

@auth_bp.route('/admin')
@admin_required
def admin_panel():
    projects = mongo.db.projects.find()
    users = mongo.db.users.find({'role': {'$ne': 'admin'}})
    return render_template('admin/dashboard.html', projects=projects, users=users)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Add new route for client dashboard
@auth_bp.route('/client/dashboard')
@login_required
def client_dashboard():
    # Get client's projects
    client_id = ObjectId(session['user_id'])
    client = mongo.db.users.find_one({'_id': client_id})
    projects = list(mongo.db.projects.find({'client_email': client['email']}))
    return render_template('client/dashboard.html', projects=projects, client=client)

# Initialize the MongoDB instance
def init_auth(app):
    mongo.init_app(app)

# Helper function to create admin user
def create_admin_user():
    admin = {
        'email': 'admin@gmail.com',
        'password': bcrypt.hashpw('your_admin_password'.encode('utf-8'), bcrypt.gensalt()),
        'role': 'admin',
        'name': 'Admin'
    }
    try:
        # Check if admin already exists
        existing_admin = mongo.db.users.find_one({'email': admin['email']})
        if not existing_admin:
            mongo.db.users.insert_one(admin)
            print("Admin user created successfully")
        else:
            print("Admin user already exists")
    except Exception as e:
        print(f"Error creating admin user: {e}")
