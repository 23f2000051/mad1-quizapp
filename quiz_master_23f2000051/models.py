from datetime import datetime
from quiz_master_23f2000051 import db , login_manager
import os
from quiz_master_23f2000051 import app , bcrypt
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model , UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20) , unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    score = db.relationship("Scores" , backref = 'user' , lazy = True)
    active = db.Column(db.Boolean, default=True)

    def get_id(self):
        return str(self.user_id)

class Subjects(db.Model):
    subject_id = db.Column(db.Integer, primary_key=True)
    subject_code = db.Column(db.String(10), unique=True, nullable=False)
    subject_name = db.Column(db.String(128), unique=True, nullable=False)
    subject_description = db.Column(db.String())
    chapters = db.relationship('Chapters', backref='subject', lazy=True)

class Chapters(db.Model):
    chapter_id = db.Column(db.Integer, primary_key=True)
    chapter_name = db.Column(db.String(128), unique=True, nullable=False)
    chapter_description = db.Column(db.String())
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'))
    quizzes = db.relationship('Quizzes', backref='chapter', lazy=True)

class Quizzes(db.Model):
    quiz_id = db.Column(db.Integer, primary_key=True)
    quiz_name = db.Column(db.String(128), unique=True, nullable=False)
    quiz_date = db.Column(db.Date , nullable=False)
    time_duration = db.Column(db.Float, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False , default=0)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.chapter_id'))
    questions = db.relationship('Questions', backref='quiz', lazy=True)
    score = db.relationship("Scores" , backref = 'quiz' , lazy = True)

class Questions(db.Model):
    question_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128) , nullable = False)
    statement = db.Column(db.String(1024), nullable=False)
    option1 = db.Column(db.String(1024), nullable=False)
    option2 = db.Column(db.String(1024), nullable=False)
    option3 = db.Column(db.String(1024))
    option4 = db.Column(db.String(1024))
    answer = db.Column(db.String(32), nullable=False)
    marks = db.Column(db.Integer, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.quiz_id'))
    

class Scores(db.Model):
    score_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.quiz_id'))
    total_marks_scored = db.Column(db.Integer, nullable=False)
    attempted_timestamp = db.Column(db.DateTime , nullable=False , default=datetime.utcnow)

if not os.path.exists('quizmaster.sqlite3'):
    app.app_context().push()
    db.create_all()
    if not Users.query.filter_by(username='admin').first():
        password=bcrypt.generate_password_hash('admin').decode('utf-8')
        admin = Users(username='admin', name='admin', password = password ,is_admin=True)
        db.session.add(admin)
        db.session.commit()

