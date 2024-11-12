from flask import Flask, redirect, render_template, flash, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, logout_user, login_user, LoginManager, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "Ansh"

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/accessportal'
db = SQLAlchemy(app)

# Login manager configuration
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define models
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

class Student(UserMixin, db.Model):
    rollno = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))  # Store password in plain text if required
    
    def get_id(self):
        return str(self.rollno)

class Supervisor(UserMixin, db.Model):
    sid = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))  # Store password in plain text if required
    
    def get_id(self):
        return str(self.sid)
    
class Admin(UserMixin,db.Model):
    __tablename__ = 'admin'
    
    adminid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

# Load user function for student, supervisor, and admin
@login_manager.user_loader
def load_user(user_id):
    if user_id == "admin":
        return AdminUser(user_id)
    user = Student.query.get(user_id)
    if not user:
        user = Supervisor.query.get(user_id)
    return user

# AdminUser class to handle login
class AdminUser(UserMixin):
    def __init__(self, id):
        self.id = id

# Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        rollno = request.form.get('rollno')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if rollno or email is already in use
        user = Student.query.filter_by(rollno=rollno).first()
        emailUser = Student.query.filter_by(email=email).first()
        if user or emailUser:
            flash("Email or Roll Number is already taken", "warning")
            return render_template("usersignup.html")
        
        new_user = Student(rollno=rollno, email=email, password=password)  # Store plain password
        db.session.add(new_user)
        db.session.commit()
        flash("SignUp Success - Please Login", "success")
        return render_template("userlogin.html")
    return render_template("usersignup.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        rollno = request.form.get('rollno')
        password = request.form.get('password')
        
        # Validate user credentials
        user = Student.query.filter_by(rollno=rollno).first()
        if user and user.password == password:  # Compare plain password
            login_user(user, remember=True)
            flash("Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials", "danger")
            return render_template("userlogin.html")
    return render_template("userlogin.html")

@app.route('/supervisorsignup', methods=['POST', 'GET'])
def supervisorsignup():
    if request.method == "POST":
        sid = request.form.get('sid')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if email is already in use
        emailUser = Student.query.filter_by(email=email).first() or Supervisor.query.filter_by(email=email).first()
        if emailUser:
            flash("Email is already taken", "warning")
            return render_template("supervisorsignup.html")
        
        new_user = Supervisor(sid=sid, email=email, password=password)  # Store plain password
        db.session.add(new_user)
        db.session.commit()
        flash("SignUp Success - Please Login", "success")
        return render_template("supervisorlogin.html")
    return render_template("supervisorsignup.html")

@app.route('/supervisorlogin', methods=['POST', 'GET'])
def supervisorlogin():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate supervisor credentials
        user = Supervisor.query.filter_by(email=email).first()
        if user and user.password == password:  # Compare plain password
            login_user(user, remember=True)
            flash("Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials", "danger")
            return render_template("supervisorlogin.html")
    return render_template("supervisorlogin.html")

@app.route('/student_home')
@login_required
def student_home():
    return render_template("student_home.html")

@app.route('/supervisor_home')
@login_required
def supervisor_home():
    return render_template("supervisor_home.html")

@app.route('/reviewproject')
@login_required
def reviewproject():
    return render_template("gradeproject.html")

@app.route('/studentmygroup')
@login_required
def studentmygroup():
    return render_template("studentmygroup.html")

@app.route('/supervisormygroup')
@login_required
def supervisormygroup():
    return render_template("supervisormygroup.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successful", "warning")
    return redirect(url_for('login'))

@app.route('/supervisorlogout')
@login_required
def supervisorlogout():
    logout_user() 
    flash("Logout SuccessFul", "warning")
    return redirect(url_for('supervisorlogin'))

@app.route('/studentprojectportal')
def projectportal():
    
    return render_template("studentprojectportal.html")

@app.route('/uploadproject')
def uploadproject():
    
    return render_template("uploadproject.html")


@app.route('/changepassword', methods=['POST', 'GET'])
@login_required
def change_password():
    if request.method == "POST":
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Access the current user
        user = current_user
        
        # Check if the old password matches the current one in the database
        if user and user.password == old_password:
            if new_password == confirm_password:  # Check if new password and confirm match
                user.password = new_password  # Store the new password directly
                db.session.commit()
                flash("Password Changed Successfully", "success")
                return render_template("index.html")
            else:
                flash("New passwords do not match", "danger")
        else:
            flash("Old password is incorrect", "danger")
    
    return render_template("change_password.html")

# Admin user class for Flask-Login
class AdminUser(UserMixin):
    def __init__(self, id):
        self.id = id

# Load user function (for admin only)
@login_manager.user_loader
def load_user(user_id):
    if user_id == "admin":
        return AdminUser(user_id)
    return None

# Route for admin login
@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    if request.method == "POST":
        username = request.form.get('admin_id')
        password = request.form.get('password')
        
        # Query the database to find the admin
        admin = db.session.query(Admin).filter_by(username=username).first()
        
        # Check if admin exists and password matches
        if admin and admin.password == password:
            admin_user = AdminUser(id=admin.adminid)
            login_user(admin_user)
            flash("Admin Login Successful", "success")
            return render_template("admindashboard.html")
        else:
            flash("Invalid Credentials", "danger")
    return render_template("adminlogin.html")

@app.route('/admindashboard')
@login_required
def admin_dashboard():
    return render_template("admindashboard.html")

@app.route('/adminlogout')
@login_required
def admin_logout():
    logout_user()
    flash("Admin Logout Successful", "success")
    return redirect(url_for('adminlogin'))

@app.route('/studentdata')
@login_required
def studentdata():
    return render_template("studentdata.html")

@app.route('/supervisordata')
@login_required
def supervisordata():
    return render_template("supervisordata.html")


if __name__ == "__main__":
    app.run(debug=True)