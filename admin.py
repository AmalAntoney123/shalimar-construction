from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from auth import admin_required
from bson import ObjectId
from werkzeug.security import generate_password_hash
import random
import string
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Initialize MongoDB
mongo = PyMongo()

def init_admin(app):
    mongo.init_app(app)

@admin_bp.route('/')
@admin_required
def admin_panel():
    # Get counts using count_documents()
    users_count = mongo.db.users.count_documents({'role': {'$ne': 'admin'}})
    projects_count = mongo.db.projects.count_documents({})
    
    # Get the actual documents
    projects = list(mongo.db.projects.find())
    users = list(mongo.db.users.find({'role': {'$ne': 'admin'}}))
    
    return render_template('admin/dashboard.html', 
                         projects=projects, 
                         users=users,
                         users_count=users_count,
                         projects_count=projects_count)

# Project Management Routes
@admin_bp.route('/projects')
@admin_required
def manage_projects():
    projects = list(mongo.db.projects.find())
    return render_template('admin/manage_projects.html', projects=projects)

@admin_bp.route('/projects/add', methods=['POST'])
@admin_required
def add_project():
    if request.method == 'POST':
        # Generate a random password for the client
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # Create client account
        client_data = {
            'email': request.form.get('client_email'),
            'name': request.form.get('client_name'),
            'password': generate_password_hash(temp_password),
            'role': 'client',
            'phone': request.form.get('client_phone'),
            'address': request.form.get('client_address')
        }
        
        # Check if client already exists
        existing_client = mongo.db.users.find_one({'email': client_data['email']})
        if not existing_client:
            client_id = mongo.db.users.insert_one(client_data).inserted_id
        else:
            client_id = existing_client['_id']

        # Create project with default status
        project = {
            'name': request.form.get('name'),
            'status': 'Not Started',  # Default status
            'location': request.form.get('location'),
            'description': request.form.get('description'),
            'created_date': datetime.now(),
            'client_id': client_id,
            'client_name': request.form.get('client_name'),
            'client_email': request.form.get('client_email'),
            'client_phone': request.form.get('client_phone'),
            'client_address': request.form.get('client_address')
        }
        
        project_id = mongo.db.projects.insert_one(project).inserted_id
        
        if not existing_client:
            flash(f'Project created successfully. New client account created with temporary password: {temp_password}')
        else:
            flash('Project created successfully. Client account already exists.')
            
        return redirect(url_for('admin.project_details', project_id=project_id))
    
    return redirect(url_for('admin.manage_projects'))

@admin_bp.route('/projects/<project_id>')
@admin_required
def project_details(project_id):
    project = mongo.db.projects.find_one({'_id': ObjectId(project_id)})
    if not project:
        flash('Project not found')
        return redirect(url_for('admin.manage_projects'))
    return render_template('admin/project_details.html', project=project)

@admin_bp.route('/projects/<project_id>/status', methods=['POST'])
@admin_required
def update_project_status(project_id):
    status = request.form.get('status')
    if status:
        mongo.db.projects.update_one(
            {'_id': ObjectId(project_id)},
            {'$set': {'status': status}}
        )
        flash('Project status updated successfully')
    return redirect(url_for('admin.project_details', project_id=project_id))

@admin_bp.route('/projects/edit/<project_id>', methods=['GET', 'POST'])
@admin_required
def edit_project(project_id):
    project = mongo.db.projects.find_one({'_id': ObjectId(project_id)})
    if request.method == 'POST':
        updated_project = {
            'name': request.form.get('name'),
            'client': request.form.get('client'),
            'status': request.form.get('status'),
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'description': request.form.get('description')
        }
        mongo.db.projects.update_one({'_id': ObjectId(project_id)}, {'$set': updated_project})
        flash('Project updated successfully')
        return redirect(url_for('admin.manage_projects'))
    return render_template('admin/edit_project.html', project=project)

# User Management Routes
@admin_bp.route('/users')
@admin_required
def manage_users():
    users = list(mongo.db.users.find({'role': {'$ne': 'admin'}}))
    return render_template('admin/manage_users.html', users=users)

@admin_bp.route('/users/add', methods=['POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        user = {
            'email': request.form.get('email'),
            'name': request.form.get('name'),
            'password': request.form.get('password'),  # Remember to hash this!
            'role': request.form.get('role', 'user')
        }
        mongo.db.users.insert_one(user)
        flash('User added successfully')
    return redirect(url_for('admin.manage_users'))

# Add other admin routes as needed 