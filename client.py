from flask import Blueprint, render_template
from flask_login import login_required, current_user
from bson import ObjectId

client_bp = Blueprint('client', __name__, url_prefix='/client')

@client_bp.route('/dashboard')
@login_required
def dashboard():
    # Get all projects for the current client
    projects = mongo.db.projects.find({
        'client_id': ObjectId(current_user.id)
    }).sort('created_date', -1)
    
    return render_template('client/dashboard.html', projects=list(projects)) 