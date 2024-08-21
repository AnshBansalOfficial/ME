from flask import Flask, json,redirect,render_template,flash,request
from flask.globals import request, session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash

from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user

# from flask_mail import Mail
import json


# mydatabase connection
local_server=True
app=Flask(__name__)
app.secret_key="Ansh"


with open('config.json','r') as c:
    params=json.load(c)["params"]



# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT='465',
#     MAIL_USE_SSL=True,
#     MAIL_USERNAME='gmail account',
#     MAIL_PASSWORD='gmail account password'
# )
# mail = Mail(app)



# this is for getting the unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/databsename'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/accessportal'
db=SQLAlchemy(app)



@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id))


class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))


class Student(UserMixin,db.Model):
    rollno=db.Column(db.String(50),primary_key=True)
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(50),unique=True)
    def get_id(self):
            return str(self.rollno);


class Supervisor(UserMixin,db.Model):
    sid=db.Column(db.String(50),primary_key=True)
    email=db.Column(db.String(50), unique= True)
    password=db.Column(db.String(50))

    def get_id(self):
            return str(self.sid);

class StudentGroup(UserMixin, db.Model):
    __tablename__ = 'studentgroup'
    groupid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll1 = db.Column(db.String(50), unique=True, nullable=False)
    roll2 = db.Column(db.String(50), unique=True, nullable=False)
    roll3 = db.Column(db.String(50), unique=True, nullable=False)
    roll4 = db.Column(db.String(50), unique=True, nullable=False)

    def get_id(self):
        return str(self.groupid)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        if hasattr(current_user, 'sid'):  # Supervisors
            if request.endpoint in ['login', 'supervisorlogin']:
                return redirect(url_for('index'))  # Redirect to home/dashboard
        elif hasattr(current_user, 'rollno'):  # Students
            if request.endpoint in ['supervisorlogin']:
                return redirect(url_for('index'))  # Redirect to home/dashboard



@app.route("/")
def home():
    return render_template("index.html")

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=="POST":
        rollno=request.form.get('rollno')
        email=request.form.get('email')
        password=request.form.get('password')
        # print(srfid,email,dob)
        #encpassword=generate_password_hash(dob)
        user=Student.query.filter_by(rollno=rollno).first()
        emailUser=Student.query.filter_by(email=email).first()
        if user or emailUser:
            flash("Email or srif is already taken","warning")
            return render_template("usersignup.html")
        # new_user=db.engine.execute(f"INSERT INTO `user` (`srfid`,`email`,`dob`) VALUES ('{srfid}','{email}','{dob}') ")
        new_user=Student(rollno=rollno,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()
                
        flash("SignUp Success - Please Login","success")
        return render_template("userlogin.html")

    return render_template("usersignup.html")


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=="POST":
        rollno=request.form.get('rollno')
        password=request.form.get('password')
        user=Student.query.filter_by(rollno=rollno).first()
        if user and user.password==password:
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("userlogin.html")


    return render_template("userlogin.html")


@app.route('/supervisorsignup',methods=['POST','GET'])
def supervisorsignup():
    if request.method=="POST":
        sid=request.form.get('sid')
        email=request.form.get('email')
        password=request.form.get('password')
        # print(srfid,email,dob)
        #encpassword=generate_password_hash(dob)
        user=Supervisor.query.filter_by(sid=sid).first()
        emailUser=Supervisor.query.filter_by(email=email).first()
        if user or emailUser:
            flash("Email is already taken","warning")
            return render_template("supervisorsignup.html")
        # new_user=db.engine.execute(f"INSERT INTO `user` (`srfid`,`email`,`dob`) VALUES ('{srfid}','{email}','{dob}') ")
        new_user=Supervisor(sid=sid,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()
                
        flash("SignUp Success - Please Login","success")
        return render_template("supervisorlogin.html")

    return render_template("supervisorsignup.html")


@app.route('/supervisorlogin',methods=['POST','GET'])
def supervisorlogin():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=Supervisor.query.filter_by(email=email).first()
        #if user and check_password_hash(user.password,password):
        if user and user.password==password:
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("supervisorlogin.html")


    return render_template("supervisorlogin.html")

@app.route('/uploadproject')
def uploadproject():
    return render_template("uploadproject.html")


    

@app.route('/reviewproject')
def reviewproject():
    return render_template("reviewproject.html")


@app.route('/logout')
@login_required
def logout():
    if hasattr(current_user, 'sid'):  # Supervisors
        logout_user()
        flash("Logout Successful", "warning")
        return redirect(url_for('supervisorlogin'))
    elif hasattr(current_user, 'rollno'):  # Students
        logout_user()
        flash("Logout Successful", "warning")
        return redirect(url_for('login'))


@app.route('/supervisorlogout')
@login_required
def supervisorlogout():
    
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))  # Listening on port 5678
    print("Waiting for debugger...")
    debugpy.wait_for_client()
    debugpy.breakpoint()  # Start debugging here


    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('supervisorlogin'))


@app.route('/studentgroupregistration', methods=['POST', 'GET'])
@login_required
def studentgroupreg():
    if request.method == "POST":
        roll1 = request.form.get('roll1')
        roll2 = request.form.get('roll2')
        roll3 = request.form.get('roll3')
        roll4 = request.form.get('roll4')

        # Ensure the current user’s roll number is included in the group
        current_user_rollno = current_user.rollno
        if current_user_rollno not in [roll1, roll2, roll3, roll4]:
            flash("Your roll number must be included in the group registration", "warning")
            return render_template("studentgroupreg.html")

        # Check if any of the roll numbers is already taken
        user1 = StudentGroup.query.filter_by(roll1=roll1).first()
        user2 = StudentGroup.query.filter_by(roll2=roll2).first()
        user3 = StudentGroup.query.filter_by(roll3=roll3).first()
        user4 = StudentGroup.query.filter_by(roll4=roll4).first()

        if user1 or user2 or user3 or user4:
            flash("One of the roll numbers is already taken", "warning")
            return render_template("studentgroupreg.html")

        # Create a new student group with the provided roll numbers
        new_group = StudentGroup(roll1=roll1, roll2=roll2, roll3=roll3, roll4=roll4)
        db.session.add(new_group)
        db.session.commit()

        flash("Group Registration Success", "success")

        # Fetch the newly created group details
        group = StudentGroup.query.filter_by(roll1=roll1, roll2=roll2, roll3=roll3, roll4=roll4).first()

        return render_template("studentgroupreg.html", group=group)

    return render_template("studentgroupreg.html")

    
# testing wheather db is connected or not  
@app.route("/test")
def test():
    try:
        a=Test.query.all()
        print(a)
        return f'MY DATABASE IS CONNECTED'
    except Exception as e:
        print(e)
        return f'MY DATABASE IS NOT CONNECTED {e}'

# @app.route("/logoutadmin")
# def logoutadmin():
#     session.pop('user')
#     flash("You are logout admin", "primary")

#     return redirect('/admin')


if __name__ == "__main__":
    app.run(debug=True)
