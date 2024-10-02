from flask import Flask, render_template, request, redirect, url_for, session
import os
import subprocess
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a secure, random secret key

# Setup the SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model for Users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid Username or Password"
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password == confirm_password:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return render_template('create_account.html', error="User already exists")
            
            new_user = User(first_name=first_name, last_name=last_name, username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return render_template('create_account.html', success=True)
        else:
            return render_template('create_account.html', error="Passwords do not match")

    return render_template('create_account.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    video_url = None
    if request.method == 'POST':
        if 'play_video' in request.form:
            video_url = request.form['video_url']
            video_url = video_url.replace('watch?v=', 'embed/')
    
    # Get the ESP32-CAM streaming link (you can modify this to fetch dynamically)
    esp32_cam_url = 'http://192.168.243.232'

    return render_template('dashboard.html', video_url=video_url, esp32_cam_url=esp32_cam_url)

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_info = User.query.filter_by(username=session['username']).first()
    return render_template('profile.html', user_info=user_info)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000, debug=True)
