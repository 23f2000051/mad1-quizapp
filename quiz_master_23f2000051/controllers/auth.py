from quiz_master_23f2000051 import app , db , bcrypt
from flask import request , render_template , redirect , url_for , flash , session
from quiz_master_23f2000051.models import Users , Subjects , Chapters , Quizzes , Questions , Scores
from quiz_master_23f2000051.form import RegistrationForm , LoginForm , SubjectForm , ChapterForm , QuizForm , QuestionForm
from flask_login import login_user , current_user , logout_user , login_required
from quiz_master_23f2000051.controllers.admin import admin_dashboard
from quiz_master_23f2000051.controllers.users import home
# ------------------------Login Page And Register Page--------------------------
@app.route('/login' , methods = ['GET' , 'POST'])
@app.route('/' , methods = ['GET' , 'POST'])
def login ():

    logout()
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username = form.username.data.strip()).first()
        if user and bcrypt.check_password_hash(user.password , form.password.data):
            if user.is_admin:
                login_user(user)
                flash(f'Welcome {form.username.data}!' , 'success')
                return redirect(url_for('admin_dashboard'))
            
            else:
                if(user.active == True):
                    login_user(user)
                    flash(f'Welcome {form.username.data}!' , 'success')
                    return redirect(url_for('home'))
                else:
                    message = 'Login Unsuccessful.User Access Blocked!'
                    flash(message , 'danger') 
        elif(user == None):
            message = 'Login Unsuccessful.User Not Found Please Register First!'
            flash(message , 'danger')
        else:
            message = 'Login Unsuccessful.Wrong Password!'
            flash(message , 'danger')
    return render_template('login.html' , title = 'Login-Quizmaster' , form = form)

@app.route('/register' , methods = ['GET' , 'POST'])
def register ():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(username = form.username.data.strip() , name = form.name.data.strip() , email = form.email.data.strip() , password = hashed_password.strip())
        db.session.add(user)
        db.session.commit()
        message = f'Account created for username "{form.username.data.strip()}"!'
        flash(message, 'success')
        return redirect(url_for('login'))
    return render_template('register.html' , title = 'Register-Quizmaster' , form = form)



@app.route('/logout')
def logout ():
    logout_user()
    return redirect(url_for('login'))

