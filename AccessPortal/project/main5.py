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

class Student1(UserMixin, db.Model):
    __tablename__ = 'student1'
    rollno = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(100))

    def get_id(self):
        return str(self.rollno)

class Supervisor1(UserMixin, db.Model):
    __tablename__ = 'supervisor1'
    empcode = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(100))

    def get_id(self):
        return str(self.empcode)

class StudentLogin1(db.Model):
    __tablename__ = 'studentlogin1'
    rollno = db.Column(db.String(100), db.ForeignKey('student1.rollno'), primary_key=True)
    password = db.Column(db.String(100))

class SupervisorLogin1(db.Model):
    __tablename__ = 'supervisorlogin1'
    empcode = db.Column(db.String(100), db.ForeignKey('supervisor1.empcode'), primary_key=True)
    password = db.Column(db.String(100))

class Map1(db.Model):
    __tablename__ = 'map1'
    rollno = db.Column(db.String(100), db.ForeignKey('student1.rollno'), primary_key=True)
    empcode1 = db.Column(db.String(100), db.ForeignKey('supervisor1.empcode'))
    empcode2 = db.Column(db.String(100), db.ForeignKey('supervisor1.empcode'))

class Project1(db.Model):
    __tablename__ = 'project1'
    pid = db.Column(db.Integer, primary_key=True)
    ptitle = db.Column(db.String(500))
    pdesc = db.Column(db.String(2000))
    pobj = db.Column(db.String(2000))
    pwork = db.Column(db.String(2000))

class ProjectMap1(db.Model):
    __tablename__ = 'projectmap1'
    pid = db.Column(db.Integer, db.ForeignKey('project1.pid'), primary_key=True)
    rollno = db.Column(db.String(100), db.ForeignKey('student1.rollno'))

class GradeProject1(db.Model):
    __tablename__ = 'gradeproject1'
    pid = db.Column(db.Integer, db.ForeignKey('project1.pid'), primary_key=True)
    feedback1 = db.Column(db.String(2000))
    feedback2 = db.Column(db.String(2000))
    marks = db.Column(db.Integer)
    
class Admin(UserMixin, db.Model):
    adminid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))  # Store the hashed password if needed

    def get_id(self):
        return str(self.adminid)

# Load user
@login_manager.user_loader
def load_user(user_id):
    user = Student1.query.get(user_id) or Supervisor1.query.get(user_id) or Admin.query.get(user_id)
    return user

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
        user = Student1.query.filter_by(rollno=rollno).first()
        emailUser = Student1.query.filter_by(email=email).first()
        if user or emailUser:
            flash("Email or Roll Number is already taken", "warning")
            return render_template("usersignup.html")
        
        new_user = Student1(rollno=rollno, email=email, password=password)  # Store plain password
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
        user = Student1.query.filter_by(rollno=rollno).first()
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
        emailUser = Student1.query.filter_by(email=email).first() or Supervisor1.query.filter_by(email=email).first()
        if emailUser:
            flash("Email is already taken", "warning")
            return render_template("supervisorsignup.html")
        
        new_user = Supervisor1(empcode=sid, email=email, password=password)
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
        user = Supervisor1.query.filter_by(email=email).first()
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

@app.route('/adminlogout')
@login_required
def adminlogout():
    logout_user()
    flash("Logout Successful", "warning")
    return redirect(url_for('adminlogin'))

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


@app.route('/studentdata')
@login_required
def studentdata():
    return render_template("studentdata.html")

@app.route('/supervisordata')
@login_required
def supervisordata():
    return render_template("supervisordata.html")


@app.route('/adminlogin', methods=['POST', 'GET'])
def adminlogin():
    if request.method == "POST":
        username = request.form.get('username')  # Get username instead of admin_id
        password = request.form.get('password')
        
        # Validate admin credentials by username
        admin = Admin.query.filter_by(username=username).first()
        
        # Check the password (use check_password_hash if the password is hashed)
        if admin and admin.password == password:  # Adjust if passwords are hashed
            login_user(admin, remember=True)
            flash("Admin Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Admin Credentials", "danger")
            return render_template("adminlogin.html")
    return render_template("adminlogin.html")


if __name__ == "__main__":
    app.run(debug=True)

