from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from auth import admin_required
from bson import ObjectId
import random
import string
from datetime import datetime
import bcrypt
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Initialize MongoDB
mongo = PyMongo()

# Add these configurations at the top after the Blueprint creation
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit

def init_admin(app):
    mongo.init_app(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            'password': bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt()),
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

        # Create project with additional fields for images and logs
        project = {
            'name': request.form.get('name'),
            'status': 'Not Started',  # Default status
            'location': request.form.get('location'),
            'description': request.form.get('description'),
            'progress_images': [],  # Initialize empty list for images
            'construction_logs': [],  # Initialize empty list for logs
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
    
    # Sort construction logs by date (newest first)
    if 'construction_logs' in project:
        project['construction_logs'].sort(key=lambda x: x['date'], reverse=True)
    
    # Sort progress images by upload date (newest first)
    if 'progress_images' in project:
        project['progress_images'].sort(key=lambda x: x['upload_date'], reverse=True)
    
    return render_template('admin/project_details.html', project=project)

@admin_bp.route('/projects/<project_id>/status', methods=['POST'])
@admin_required
def update_project_status(project_id):
    try:
        # Get form data
        status = request.form.get('status', 'Not Started')
        status_notes = request.form.get('status_notes', '')
        completion_percentage = int(request.form.get('completion_percentage', '0'))
        next_steps = request.form.get('next_steps', '')
        phase = request.form.get('phase', '')
        
        # Get cost information
        try:
            phase_cost = float(request.form.get('phase_cost', 0))
        except ValueError:
            phase_cost = 0
        
        cost_breakdown = request.form.get('cost_breakdown', '')

        # Handle image uploads
        uploaded_images = []
        if 'status_images[]' in request.files:
            files = request.files.getlist('status_images[]')
            
            for file in files:
                if file and allowed_file(file.filename):
                    # Create unique filename with timestamp
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_filename = f"{timestamp}_{secure_filename(file.filename)}"
                    
                    # Ensure upload directory exists
                    if not os.path.exists(UPLOAD_FOLDER):
                        os.makedirs(UPLOAD_FOLDER)
                    
                    # Save file
                    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                    file.save(file_path)
                    
                    # Add image info to uploaded_images list
                    uploaded_images.append({
                        'filename': unique_filename,
                        'original_name': file.filename,
                        'upload_date': datetime.now()
                    })

        # Create status update entry
        status_update = {
            'status': status,
            'phase': phase,
            'notes': status_notes,
            'completion_percentage': completion_percentage,
            'next_steps': next_steps,
            'images': uploaded_images,
            'update_date': datetime.now(),
            'phase_cost': phase_cost,
            'cost_breakdown': cost_breakdown
        }

        # Update project and total cost
        result = mongo.db.projects.update_one(
            {'_id': ObjectId(project_id)},
            {
                '$set': {'status': status},
                '$push': {'status_updates': status_update},
                '$inc': {'total_cost': phase_cost}  # Increment total cost
            }
        )

        if result.modified_count > 0:
            flash('Project status, images, and costs updated successfully', 'success')
        else:
            flash('No changes were made to the project', 'info')

    except Exception as e:
        flash(f'Error updating project: {str(e)}', 'error')
        return redirect(url_for('admin.project_details', project_id=project_id))

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

# Add these new route handlers
@admin_bp.route('/projects/<project_id>/upload-images', methods=['POST'])
@admin_required
def upload_progress_images(project_id):
    if 'images[]' not in request.files:
        flash('No files selected')
        return redirect(url_for('admin.project_details', project_id=project_id))
    
    files = request.files.getlist('images[]')
    description = request.form.get('description', '')
    
    uploaded_images = []
    for file in files:
        if file and allowed_file(file.filename):
            # Create unique filename
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
            
            # Ensure upload directory exists
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            # Save file
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # Create image entry
            image_entry = {
                'filename': filename,
                'description': description,
                'upload_date': datetime.now()
            }
            uploaded_images.append(image_entry)
    
    if uploaded_images:
        # Update project with new images
        mongo.db.projects.update_one(
            {'_id': ObjectId(project_id)},
            {'$push': {'progress_images': {'$each': uploaded_images}}}
        )
        flash('Images uploaded successfully')
    
    return redirect(url_for('admin.project_details', project_id=project_id))

@admin_bp.route('/projects/<project_id>/add-log', methods=['POST'])
@admin_required
def add_construction_log(project_id):
    log_entry = {
        'phase': request.form.get('phase'),
        'entry': request.form.get('log_entry'),
        'completion_status': int(request.form.get('completion_status', 0)),
        'date': datetime.now()
    }
    
    # Update project with new log entry
    mongo.db.projects.update_one(
        {'_id': ObjectId(project_id)},
        {'$push': {'construction_logs': log_entry}}
    )
    
    flash('Construction log entry added successfully')
    return redirect(url_for('admin.project_details', project_id=project_id))

@admin_bp.route('/projects/delete/<project_id>', methods=['POST'])
@admin_required
def delete_project(project_id):
    try:
        # Find the project first to get associated images
        project = mongo.db.projects.find_one({'_id': ObjectId(project_id)})
        
        if project:
            # Delete associated images from filesystem
            if 'progress_images' in project:
                for image in project['progress_images']:
                    if 'filename' in image:
                        file_path = os.path.join(UPLOAD_FOLDER, image['filename'])
                        if os.path.exists(file_path):
                            os.remove(file_path)
            
            # Delete images from status updates
            if 'status_updates' in project:
                for update in project['status_updates']:
                    if 'images' in update:
                        for image in update['images']:
                            if 'filename' in image:
                                file_path = os.path.join(UPLOAD_FOLDER, image['filename'])
                                if os.path.exists(file_path):
                                    os.remove(file_path)
            
            # Delete the project from database
            result = mongo.db.projects.delete_one({'_id': ObjectId(project_id)})
            
            if result.deleted_count > 0:
                flash('Project deleted successfully', 'success')
            else:
                flash('Project not found', 'error')
        else:
            flash('Project not found', 'error')
            
    except Exception as e:
        flash(f'Error deleting project: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_projects'))

# Add other admin routes as needed 