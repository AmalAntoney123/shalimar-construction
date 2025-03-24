from flask import Flask, render_template
from auth import auth_bp, init_auth
from admin import admin_bp, init_admin
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Initialize modules
init_auth(app)
init_admin(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/cost-estimate')
def cost_estimate():
    return render_template('cost-estimate.html')

if __name__ == "__main__":
    app.run(debug=True) 