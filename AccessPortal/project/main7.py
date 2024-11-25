from flask import Flask, redirect, render_template, flash, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, logout_user, login_user, LoginManager, current_user
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = "Ansh"

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/accessportal'
db = SQLAlchemy(app)

# Login manager configuration
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define models
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

@login_manager.user_loader
def load_user(user_id):
    user_type = session.get('user_type')
    
    if user_type == 'admin':
        return Admin.query.get(user_id)
    elif user_type == 'student':
        return Student1.query.get(user_id)
    elif user_type == 'supervisor':
        return Supervisor1.query.get(user_id)
    return None

# Routes
@app.route("/")
def home():
    return render_template("index.html")

# Signup and login routes for students and supervisors
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        rollno = request.form.get('rollno')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        user = Student1.query.filter_by(rollno=rollno).first()
        emailUser = Student1.query.filter_by(email=email).first()
        phoneUser = Student1.query.filter_by(phone=phone).first()
        if user or emailUser or phoneUser:
            flash("Email or Roll Number or Phone is already taken", "warning")
            return render_template("usersignup.html")
        
        password = secrets.token_urlsafe(8)  # 8-character random password
        
        new_user = Student1(rollno=rollno, name= name, email=email , phone= phone)
        new_login = StudentLogin1(rollno=rollno, password=password)
        db.session.add(new_user)
        db.session.add(new_login)
        db.session.commit()

        # Send the password via email
        try:
            send_email(email, name, password,rollno)
            flash("SignUp Success - Password sent to your email. Please Login", "success")
        except Exception as e:
            flash(f"SignUp Success, but failed to send email: {str(e)}", "warning")
        
        return render_template("studentdata.html")
    return render_template("usersignup.html")

@app.route('/supervisorsignup', methods=['POST', 'GET'])
def supervisor_signup():
    if request.method == "POST":
        empcode = request.form.get('empcode')
        name= request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        supervisor = Supervisor1.query.filter_by(empcode=empcode).first()
        emailUser = Supervisor1.query.filter_by(email=email).first()
        phoneUser = Supervisor1.query.filter_by(phone=phone).first()

        if supervisor or emailUser or phoneUser:
            flash("Email or Employee Code or Phone is already taken", "warning")
            return render_template("supervisorsignup.html")
        
        password = secrets.token_urlsafe(8)  # 8-character random password
        
        new_supervisor = Supervisor1(empcode=empcode, name= name, email=email, phone=phone)
        new_login = SupervisorLogin1(empcode=empcode, password=password)
        db.session.add(new_supervisor)
        db.session.add(new_login)
        db.session.commit()
        # Send the password via email
        try:
            send_email(email, name, password,empcode)
            flash("SignUp Success - Password sent to your email. Please Login", "success")
        except Exception as e:
            flash(f"SignUp Success, but failed to send email: {str(e)}", "warning")
        return render_template("supervisordata.html")
    return render_template("supervisorsignup.html")

def send_email(recipient_email, name, password,id):
    sender_email = "ansh.tiet@gmail.com"  # Replace with your email
    sender_password = "sobuqxrsznzpsixd"  # Replace with your email password or app-specific password
    
    subject = "Access Portal - Your Auto-Generated Password"
    body = f"""
    Hi {name},

    Welcome to the Access Portal! Below are your login credentials:

    ID: {id}
    Password: {password}

    Please use this password to login and change it immediately.

    Best regards,
    Access Portal Team
    """
    
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        rollno = request.form.get('rollno')
        password = request.form.get('password')
        
        # Find user and login details
        user = Student1.query.filter_by(rollno=rollno).first()
        login_details = StudentLogin1.query.filter_by(rollno=rollno, password=password).first()
        
        if user and login_details:
            login_user(user, remember=True)
            session['user_type'] = 'student'  # Store user type in session
            flash("Student Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Student Credentials", "danger")
            return render_template("userlogin.html")
    return render_template("userlogin.html")


@app.route('/supervisorlogin', methods=['POST', 'GET'])
def supervisor_login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find supervisor and login details
        supervisor = Supervisor1.query.filter_by(email=email).first()
        login_details = SupervisorLogin1.query.filter_by(empcode=supervisor.empcode, password=password).first() if supervisor else None
        
        if supervisor and login_details:
            login_user(supervisor, remember=True)
            session['user_type'] = 'supervisor'  # Store user type in session
            flash("Supervisor Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Supervisor Credentials", "danger")
            return render_template("supervisorlogin.html")
    return render_template("supervisorlogin.html")

@app.route('/studentmygroup')
@login_required
def studentmygroup():
    # Get the student information using the current logged-in user
    student = Student1.query.filter_by(email=current_user.email).first()
    
    if student:
        # Get supervisor mapping from Map1 based on student rollno
        student_info = Map1.query.filter_by(rollno=student.rollno).first()
        
        # Get supervisor details using empcodes related to the student
        supervisor1 = Supervisor1.query.filter_by(empcode=student_info.empcode1).first()
        supervisor2 = Supervisor1.query.filter_by(empcode=student_info.empcode2).first()

        return render_template("studentmygroup.html", student=student, supervisor1=supervisor1, supervisor2=supervisor2)
    else:
        # Handle case where no student data is found (optional)
        return render_template("error.html", message="Student data not found.")

@app.route('/supervisormygroup')
@login_required
def supervisormygroup():
    # Get the supervisor information using the current logged-in user
    supervisor = Supervisor1.query.filter_by(email=current_user.email).first()
    
    if supervisor:
        # Find all students assigned to this supervisor (empcode1 and empcode2)
        students_info = Map1.query.filter(
            (Map1.empcode1 == supervisor.empcode) | (Map1.empcode2 == supervisor.empcode)
        ).all()

        students = []
        for student_info in students_info:
            # Get the student details using roll number
            student = Student1.query.filter_by(rollno=student_info.rollno).first()
            if student:
                students.append(student)

        # Assuming Map1 holds both supervisor mappings, fetch supervisor details
        # Fetch the second supervisor (if assigned in the Map1 table)
        first_supervisor = Supervisor1.query.filter_by(empcode=students_info[0].empcode1).first() if students_info else None
        second_supervisor = Supervisor1.query.filter_by(empcode=students_info[0].empcode2).first() if students_info else None

        return render_template("supervisormygroup.html", supervisor=supervisor, first_supervisor=first_supervisor, second_supervisor=second_supervisor, students=students)
    else:
        # Handle case where no supervisor data is found (optional)
        return render_template("error.html", message="Supervisor data not found.")

@app.route('/logout')
def logout():
    logout_user()
    session.pop('user_type', None)  # Clear user type from session
    flash("Logged out successfully", "info")
    return redirect('/login')

@app.route('/supervisorlogout')
@login_required
def supervisorlogout():
    logout_user() 
    session.pop('user_type', None)  # Clear user type from session
    flash("Logout SuccessFul", "warning")
    return redirect(url_for('supervisor_login'))

@app.route('/adminlogout')
@login_required
def adminlogout():
    logout_user()
    session.pop('user_type', None)  # Clear user type from session
    flash("Logout Successful", "warning")
    return redirect(url_for('adminlogin'))

@app.route('/studentprojectportal')
@login_required
def projectportal():
    # Check if the current user has a PID linked to them in the ProjectMap1 table
    if isinstance(current_user, Student1):
        # Look for a project associated with the current student's roll number
        project_map = ProjectMap1.query.filter_by(rollno=current_user.rollno).first()
        if project_map:
            pid = project_map.pid  # Get the PID from the project map table
        else:
            pid = None  # No project associated with the student
    else:
        pid = None  # If the current user is not a student, set pid as None

    # Print the pid to the console for debugging
    print(f"PID in session: {pid}")
    
    # Pass the PID to the template
    return render_template("studentprojectportal.html", pid=pid)

@app.route('/changepassword', methods=['POST', 'GET'])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash("New Password and Confirm Password do not match", "danger")
            return render_template("change_password.html")
        
        if isinstance(current_user, Student1):
            user_login = StudentLogin1.query.filter_by(rollno=current_user.rollno).first()
        else:
            user_login = SupervisorLogin1.query.filter_by(empcode=current_user.empcode).first()
        
        if user_login and user_login.password == current_password:
            user_login.password = new_password
            db.session.commit()
            flash("Password Changed Successfully", "success")
        else:
            flash("Current Password is incorrect", "danger")
    return render_template("change_password.html")

@app.route('/studentdata')
@login_required
def studentdata():
    return render_template("studentdata.html")

@app.route('/viewstudentdata')
@login_required  # Optional: Use if only logged-in users (e.g., admins) should access this
def view_student_data():

    
    # Fetch all students and their corresponding passwords
    students = db.session.query(
        Student1.rollno, Student1.name, Student1.email, Student1.phone, StudentLogin1.password
    ).join(StudentLogin1, Student1.rollno == StudentLogin1.rollno).all()

    return render_template('viewstudentdata.html', students=students)

@app.route('/viewsupervisordata')
@login_required  # Optional: Use if only logged-in users (e.g., admins) should access this
def view_supervisor_data():

    
    # Fetch all students and their corresponding passwords
    supervisor = db.session.query(
        Supervisor1.empcode, Supervisor1.name, Supervisor1.email, Supervisor1.phone, SupervisorLogin1.password
    ).join(SupervisorLogin1, Supervisor1.empcode == SupervisorLogin1.empcode).all()

    return render_template('viewsupervisordata.html', supervisor=supervisor)

@app.route('/viewmap')
def viewmap():
    # Query all mappings
    mappings = db.session.query(Map1, Student1, Supervisor1).join(
        Student1, Map1.rollno == Student1.rollno
    ).outerjoin(
        Supervisor1, Map1.empcode1 == Supervisor1.empcode
    ).all()

    # Prepare data for the table
    mapped_data = []
    for map_entry, student, supervisor1 in mappings:
        # Fetch second supervisor details if available
        supervisor2 = Supervisor1.query.filter_by(empcode=map_entry.empcode2).first()

        mapped_data.append({
            'rollno': student.rollno,
            'name': student.name,
            'supervisor1': supervisor1.empcode if supervisor1 else 'N/A',
            'supervisor2': supervisor2.empcode if supervisor2 else 'N/A'
        })

    # Render the HTML page with the data
    return render_template('viewmap.html', data=mapped_data)

@app.route('/viewstudentdata')
@login_required
def viewstudentdata():
    return render_template("viewstudentdata.html")

@app.route('/supervisordata')
@login_required
def supervisordata():
    return render_template("supervisordata.html")

# Project management routes
@app.route('/uploadproject', methods=['POST', 'GET'])
@login_required
def upload_project():
    if request.method == "POST":
        ptitle = request.form.get('ptitle')
        pdesc = request.form.get('pdesc')
        pobj = request.form.get('pobj')
        pwork = request.form.get('pwork')
        
        new_project = Project1(ptitle=ptitle, pdesc=pdesc, pobj=pobj, pwork=pwork)
        db.session.add(new_project)
        db.session.commit()
        
        # Link project to the student
        new_project_map = ProjectMap1(pid=new_project.pid, rollno=current_user.rollno)
        db.session.add(new_project_map)
        db.session.commit()
        
        flash("Project Uploaded Successfully", "success")
        
        # Redirect to the /studentprojectportal page after successful upload
        return redirect(url_for('projectportal'))
    
    return render_template("uploadproject.html")


@app.route('/reviewproject', methods=['POST', 'GET'])
@login_required
def review_project():
    # Ensure only supervisors can access this route
    if isinstance(current_user, Supervisor1):
        # Get the supervisor ID from the current user (assuming it's stored in the Supervisor1 model)
        supervisor_id = current_user.empcode  # Modify based on your actual model
        print(f"Supervisor ID: {supervisor_id}")  # Debugging line to check the supervisor's ID

        # Step 1: Get roll numbers of the students assigned to this supervisor from the map1 table
        assigned_students = db.session.query(Map1.rollno, Map1.empcode1, Map1.empcode2).filter(
            (Map1.empcode1 == supervisor_id) | (Map1.empcode2 == supervisor_id)
        ).all()
        print(f"Assigned Students: {assigned_students}")  # Debugging line to check assigned students

        # Step 2: Fetch the project IDs (pid) assigned to the students from the projectmap1 table
        student_project_ids = []
        for student in assigned_students:
            roll_no, empcode1, empcode2 = student  # Unpack the tuple to get rollno, empcode1, and empcode2
            print(f"Fetching projects for student with roll_no: {roll_no}")  # Debugging line to check current student
            projects = db.session.query(ProjectMap1.pid).filter(ProjectMap1.rollno == roll_no).all()
            print(f"Projects for student {roll_no}: {projects}")  # Debugging line to check projects for each student
            student_project_ids.extend([project[0] for project in projects])  # Extract the pid from the result

        # Debugging line to print the final list of project IDs
        print(f"Final Project IDs: {student_project_ids}")

        # Initialize feedback_locked as an empty list
        feedback_locked = []

        # Step 3: Check if the feedback1 or feedback2 is already given by the supervisor for any project
        for pid in student_project_ids:
            grade_entry = GradeProject1.query.filter_by(pid=pid).first()
            if grade_entry:
                # Check which feedback field corresponds to the supervisor
                if supervisor_id == empcode1 and grade_entry.feedback1:
                    feedback_locked.append(True)  # Feedback1 is locked
                elif supervisor_id == empcode2 and grade_entry.feedback2:
                    feedback_locked.append(True)  # Feedback2 is locked
                else:
                    feedback_locked.append(False)  # Feedback is not locked
            else:
                feedback_locked.append(False)  # If no grade entry, it's not locked
        print(feedback_locked)

        # Return to template, passing student_project_ids and feedback_locked
        return render_template("gradeproject.html", pid=student_project_ids, feedback_locked=feedback_locked)
    
    else:
        flash("Only supervisors can grade projects.", "danger")
        return redirect(url_for('home'))
    

@app.route('/viewproject')
@login_required
def viewproject():
    if isinstance(current_user, Supervisor1):
    # Get the supervisor ID
        supervisor_id = current_user.empcode
        print(f"Supervisor ID: {supervisor_id}")  # Debug output to confirm supervisor's ID

        # Step 1: Get roll numbers of students assigned to this supervisor from the Map1 table
        assigned_students = db.session.query(Map1.rollno).filter(
            (Map1.empcode1 == supervisor_id) | (Map1.empcode2 == supervisor_id)
        ).all()
        print(f"Assigned Students Roll Numbers: {[student.rollno for student in assigned_students]}")  # Debug output

        # Step 2: Retrieve project IDs (pid) assigned to the students from the ProjectMap1 table
        student_project_ids = []
        for student in assigned_students:
            roll_no = student.rollno
            projects = db.session.query(ProjectMap1.pid).filter(ProjectMap1.rollno == roll_no).all()
            student_project_ids.extend([project[0] for project in projects])

        print(f"Student Project IDs: {student_project_ids}")  # Debug output to confirm project IDs

        # Step 3: Retrieve project details from the Project1 table using the collected project IDs
        projects = db.session.query(Project1).filter(Project1.pid.in_(student_project_ids)).all()

        # Step 4: Pass the project details to the template
        return render_template("viewproject.html", projects=projects)



@app.route('/adminlogin', methods=['POST', 'GET'])
def adminlogin():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.password == password:  # Use `check_password_hash` for hashed passwords
            login_user(admin, remember=True)
            session['user_type'] = 'admin'  # Set user type in session
            flash("Admin Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Admin Credentials", "danger")
            return render_template("adminlogin.html")
    return render_template("adminlogin.html")


@app.route('/grade', methods=['GET', 'POST'])
@login_required
def grade_project():
    # Ensure the user is logged in and has the necessary permissions
    if request.method == 'POST':
        # Retrieve form data
        pgrade = request.form['pgrade']
        pfeedback = request.form['pfeedback']
        
        # Validate inputs (example: grade should be an integer)
        try:
            pgrade = int(pgrade)
        except ValueError:
            flash("Invalid grade. Please enter a valid number.", "danger")
            return redirect(url_for('grade_project'))
        
        if pgrade < 0 or pgrade > 5:
            flash("Grade should be between 0 and 5.", "danger")
            return redirect(url_for('grade_project'))

        if isinstance(current_user, Supervisor1):
            # Get the supervisor ID from the current user (assuming it's stored in the Supervisor1 model)
            supervisor_id = current_user.empcode  # Modify based on your actual model
            print(f"Supervisor ID: {supervisor_id}")  # Debugging line to check the supervisor's ID

            # Step 1: Get roll numbers of the students assigned to this supervisor from the map1 table
            assigned_students = db.session.query(Map1.rollno, Map1.empcode1, Map1.empcode2).filter(
                (Map1.empcode1 == supervisor_id) | (Map1.empcode2 == supervisor_id)
            ).all()
            print(f"Assigned Students: {assigned_students}")  # Debugging line to check assigned students

            # Step 2: Fetch the project IDs (pid) assigned to the students from the projectmap1 table
            student_project_ids = []
            for student in assigned_students:
                roll_no = student.rollno
                print(f"Fetching projects for student with roll_no: {roll_no}")  # Debugging line to check current student
                projects = db.session.query(ProjectMap1.pid).filter(ProjectMap1.rollno == roll_no).all()
                print(f"Projects for student {roll_no}: {projects}")  # Debugging line to check projects for each student
                student_project_ids.extend([project[0] for project in projects])  # Extract the pid from the result
            pid = student_project_ids[0] if student_project_ids else None  # Ensure pid is available

            # If no projects found, show an error message
            if pid is None:
                flash("No projects found for the assigned students.", "danger")
                return redirect(url_for('student_project_portal'))

        # Fetch the project using pid, ensure it exists
        project = Project1.query.filter_by(pid=pid).first()
        if not project:
            flash("Project not found.", "danger")
            return redirect(url_for('student_project_portal'))  # Redirect to a valid page

        # Check if the project has already been graded
        grade_entry = GradeProject1.query.filter_by(pid=pid).first()

        # Determine which feedback field to update based on the supervisor's position in Map1
        feedback_field = None
        for student in assigned_students:
            if student.empcode1 == supervisor_id:
                feedback_field = 'feedback1'
                break
            elif student.empcode2 == supervisor_id:
                feedback_field = 'feedback2'
                break
        
        if not feedback_field:
            flash("Supervisor does not match the assigned student's roles.", "danger")
            return redirect(url_for('student_project_portal'))

        # Update or create the grade entry
        if grade_entry:
            # When the grade entry exists, retain feedback1 if it's already set and update feedback2
            if grade_entry.marks is not None:
                # If marks already exist, don't update them
                if feedback_field == 'feedback1':
                    if not grade_entry.feedback1:
                        grade_entry.feedback1 = pfeedback
                elif feedback_field == 'feedback2':
                    if not grade_entry.feedback2:
                        grade_entry.feedback2 = pfeedback
            else:
                # If marks do not exist, set them along with feedback
                grade_entry.marks = pgrade
                if feedback_field == 'feedback1':
                    grade_entry.feedback1 = pfeedback
                    grade_entry.feedback2 = ""  # Ensure feedback2 is set to an empty string if not used
                elif feedback_field == 'feedback2':
                    grade_entry.feedback2 = pfeedback
                    grade_entry.feedback1 = ""  # Ensure feedback1 is set to an empty string if not used
        else:
            # If the entry does not exist, create a new one with the appropriate feedback field
            grade_entry = GradeProject1(pid=pid, marks=pgrade)

            # Set feedback fields, ensure that the other feedback is set to an empty string
            if feedback_field == 'feedback1':
                grade_entry.feedback1 = pfeedback
                grade_entry.feedback2 = ""  # Ensure feedback2 is set to an empty string if not used
            elif feedback_field == 'feedback2':
                grade_entry.feedback2 = pfeedback
                grade_entry.feedback1 = ""  # Ensure feedback1 is set to an empty string if not used

            db.session.add(grade_entry)

        # Commit the transaction
        db.session.commit()
        
        flash("Project graded successfully!", "success")
        return redirect(url_for('review_project'))  # Redirect to another page

    # Handle GET request (rendering the form)
    return render_template('grade.html')  # Assuming the grade.html is set correctly in your templates folder


@app.route('/viewfeedbackportal', methods=['GET', 'POST'])
@login_required
def view_feedback_portal():
    # Initialize variables
    pid = None
    feedback1 = None
    feedback2 = None

    # Check if the current user is a student
    if isinstance(current_user, Student1):
        # Look for a project associated with the current student's roll number
        project_map = ProjectMap1.query.filter_by(rollno=current_user.rollno).first()
        
        if project_map:
            pid = project_map.pid  # Get the PID from the project map table
            
            # Retrieve feedback based on the PID if it exists in GradeProject1
            grade_project = GradeProject1.query.filter_by(pid=pid).first()
            if grade_project:
                feedback1 = grade_project.feedback1  # Feedback from supervisor 1
                feedback2 = grade_project.feedback2  # Feedback from supervisor 2
        else:
            pid = None  # No project associated with the student
    # Pass pid, feedback1, and feedback2 to the template
    return render_template("viewfeedbackportal.html", pid=pid, feedback1=feedback1, feedback2=feedback2)


@app.route('/viewfeedback', methods=['GET', 'POST'])
@login_required
def view_feedback():
    # Initialize variables
    pid = None
    feedback1 = None
    feedback2 = None

    # Check if the current user is a student
    if isinstance(current_user, Student1):
        # Look for a project associated with the current student's roll number
        project_map = ProjectMap1.query.filter_by(rollno=current_user.rollno).first()
        
        if project_map:
            pid = project_map.pid  # Get the PID from the project map table
            
            # Retrieve feedback based on the PID if it exists in GradeProject1
            grade_project = GradeProject1.query.filter_by(pid=pid).first()
            if grade_project:
                feedback1 = grade_project.feedback1  # Feedback from supervisor 1
                feedback2 = grade_project.feedback2  # Feedback from supervisor 2
        else:
            pid = None  # No project associated with the student
    # Pass pid, feedback1, and feedback2 to the template
    return render_template("viewfeedback.html", pid=pid, feedback1=feedback1, feedback2=feedback2)

@app.route('/adminviewgrades')
def adminviewgrades():
    # Querying to get grades, projects, and student details
    grades = db.session.query(
        GradeProject1, Project1, Student1
    ).join(
        Project1, GradeProject1.pid == Project1.pid
    ).join(
        ProjectMap1, ProjectMap1.pid == Project1.pid
    ).join(
        Student1, ProjectMap1.rollno == Student1.rollno
    ).all()

    # Prepare data for the template
    grade_data = []
    for grade_entry, project, student in grades:
        grade_data.append({
            'rollno': student.rollno,
            'student_name': student.name,
            'pid': project.pid,
            'project_title': project.ptitle,
            'marks': grade_entry.marks,
            'feedback1': grade_entry.feedback1,
            'feedback2': grade_entry.feedback2
        })

    # Render the template with data
    return render_template('adminviewgrades.html', data=grade_data)


@app.route('/addmap', methods=['GET', 'POST'])
def addmap():
    if request.method == 'POST':
        rollno = request.form.get('rollno')
        empcode1 = request.form.get('empcode1')
        empcode2 = request.form.get('empcode2')

        # Check if roll number and empcodes exist in the database
        student = Student1.query.filter_by(rollno=rollno).first()
        supervisor1 = Supervisor1.query.filter_by(empcode=empcode1).first()
        supervisor2 = Supervisor1.query.filter_by(empcode=empcode2).first()

        if not student:
            flash(f"Student with Roll Number {rollno} does not exist.", "error")
            return redirect(url_for('addmap'))
        if not supervisor1:
            flash(f"Supervisor with Empcode {empcode1} does not exist.", "error")
            return redirect(url_for('addmap'))
        if not supervisor2:
            flash(f"Supervisor with Empcode {empcode2} does not exist.", "error")
            return redirect(url_for('addmap'))

        # Check if mapping already exists
        existing_mapping = Map1.query.filter_by(rollno=rollno).first()
        if existing_mapping:
            flash(f"Mapping for Roll Number {rollno} already exists.", "error")
            return redirect(url_for('addmap'))

        # Add new mapping to the database
        new_mapping = Map1(rollno=rollno, empcode1=empcode1, empcode2=empcode2)
        db.session.add(new_mapping)
        db.session.commit()

        flash(f"Mapping for Roll Number {rollno} added successfully.", "success")
        return redirect(url_for('viewmap'))

    # Render the HTML form
    return render_template('addmap.html')

@app.route('/manageprojects')
def manageprojects():
    return render_template('manageprojects.html')

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
