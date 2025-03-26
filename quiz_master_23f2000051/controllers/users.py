from quiz_master_23f2000051 import app , db , bcrypt
from flask import request , render_template , redirect , url_for , flash , jsonify , session
from quiz_master_23f2000051.models import Users , Subjects , Chapters , Quizzes , Questions , Scores
from quiz_master_23f2000051.form import RegistrationForm , LoginForm , SubjectForm , ChapterForm , QuizForm , QuestionForm
from flask_login import login_user , current_user , logout_user , login_required
from datetime import date

response = []
index = 0

@app.route("/user_dashboard" , methods = ['GET' , 'POST'])
@login_required
def home():
    global response , index
    response = []
    index = 0

    current_quiz = []
    upcoming_quiz = []
    passed_quiz = []
    quizzes = Quizzes.query.all()

    for quiz in quizzes:
        if(quiz.quiz_date==date.today()):
            if quiz.questions:
                current_quiz.append(quiz)
        elif((quiz.quiz_date-date.today()).days)>0:
            upcoming_quiz.append(quiz)
        else:
            passed_quiz.append(quiz)
    current_validity = [1 for i in range(len(current_quiz))]
    passed_validity = [0 for i in range(len(passed_quiz))]
    for quiz in current_quiz:
        for score in quiz.score:
            if score.user_id == current_user.user_id:
                current_validity[current_quiz.index(quiz)]=0
                break
    
    for quiz in passed_quiz:
        for score in quiz.score:
            if score.user_id == current_user.user_id:
                passed_validity[passed_quiz.index(quiz)]=1
                break
    
    return render_template('users/home.html' , title = 'Dashboard-Quizmaster' , 
                           current_quiz = current_quiz , current_validity = current_validity ,
                           upcoming_quiz = upcoming_quiz , passed_quiz = passed_quiz , passed_validity = passed_validity
                           )


@app.route("/user_start/quiz/<int:quiz_id>" , methods = ['GET' , 'POST'])
@login_required
def quiz_start(quiz_id):

    global response
    global index
    score = 0
    quiz = Quizzes.query.get(quiz_id)
    questions = Questions.query.filter_by(quiz_id = quiz_id).all()
    if request.method == "POST":
        data = request.json
        if not response:
            response = [0 for i in questions]
        question_statement = data.get("question_statement")
        user_response = data.get("selected_option")
        
        

        if data.get("action") == "save_next":
            response[index] = user_response
            index+=1
            if index == len(questions):
                index = 0
            next_question = dict()
            next_question["index"] = (index+1)
            next_question["statement"] = questions[index].statement
            next_question["option1"] = questions[index].option1
            next_question["option2"] = questions[index].option2
            next_question["option3"] = questions[index].option3
            next_question["option4"] = questions[index].option4
            next_question["answer"] = response[index]
            return jsonify({"status": "next", "question": next_question})
        
        elif data.get("action") == "submit":
            for i in range(len(questions)):
                if str(questions[i].answer) == response[i]:
                    score+=int(questions[i].marks)
            
            score = Scores(user_id = current_user.user_id , quiz_id = quiz_id , total_marks_scored = score)
            db.session.add(score)
            db.session.commit()

            return jsonify({"status": "submitted", "redirect_url": url_for("quiz_end", quiz_id=quiz_id)})

        
        return redirect(url_for("score"))

    elif request.method == "GET":
        score = Scores.query.filter_by(quiz_id = quiz_id , user_id = current_user.user_id).first()
        if score:
            return render_template('users/quiz_submit.html' , title = 'Quiz-Quizmaster')
        time_left = quiz.time_duration
    return render_template('users/quiz_start.html' , title = 'Quiz-Quizmaster' , quiz = quiz , questions = questions , time_left = time_left)

    
    

@app.route('/user/<int:quiz_id>/score')
@login_required
def quiz_end(quiz_id):
    marks = Scores.query.filter_by(quiz_id = quiz_id , user_id = current_user.user_id).first()
    numbers = marks.total_marks_scored
    return render_template("users/quiz_end.html" , title = "Quiz Done" , scores = numbers)

@app.route('/user/scores')
@login_required
def score():
    quiz_titles = []
    scores = Scores.query.filter_by(user_id = current_user.user_id)
    for score in scores:
        if score.user_id==current_user.user_id:
            for quiz in Quizzes.query.all():
                if score.quiz_id==quiz.quiz_id  :
                    quiz_titles.append((quiz.quiz_name,quiz.quiz_date,len(quiz.questions),score.total_marks_scored))
                    break
    return render_template('users/score.html' , scores = quiz_titles)



@app.route("/user_view/quiz/<int:quiz_id>" , methods = ['GET','POST'])
@login_required
def quiz_details(quiz_id):
    quiz = Quizzes.query.filter_by(quiz_id = quiz_id).first()
    chapter = Chapters.query.filter_by(chapter_id = quiz.chapter_id).first()
    subject = Subjects.query.filter_by(subject_id = chapter.subject_id).first()
    return render_template("users/quiz_details.html" , quiz = quiz , chapter = chapter , subject = subject)


@app.route("/user_summary")
@login_required
def user_summary():

    subject_names = dict()
    quizzes = Quizzes.query.all()
    for quiz in quizzes:
        chapter = Chapters.query.get(quiz.chapter_id)
        subject = Subjects.query.get(chapter.subject_id)
        if(subject.subject_name in subject_names):
            subject_names[subject.subject_name] += 1
        else:
            subject_names[subject.subject_name] = 1

    sub_names = [key for key in subject_names]
    sub_counts = [subject_names[key] for key in subject_names]

    # print(sub_names , sub_counts)

    
    months = [0 for i in range(12)]
    quizs = []
    scores = Scores.query.all()
    for score in scores:
        if score.user_id == current_user.user_id:
            quizs.append(Quizzes.query.get(score.quiz_id))

    # print(quizs)

    for quiz in quizs:
        indx = (quiz.quiz_date.month)-1
        months[indx]+=1

    return render_template("/users/summary/chart.html" , title = "Summary" , sub_names = sub_names ,
                           sub_counts = sub_counts , months = months
                           )

@app.route("/user_search" , methods = ['GET' , 'POST'])
@login_required
def user_search():
    if request.method == "POST":
        search = request.form.get("search").strip()
        chosen = request.form.get("options")

        if not search:
            flash("Search-Field Empty, Showing All Results!" , "primary")   
        # print(search , chosen)
        if chosen == "chapter":

            chapters = Chapters.query.filter(Chapters.chapter_name.like(f'%{search}%')).all()
            quizzes = [[] for i in range(len(chapters))]
            for i in range(len(chapters)):
                for quiz in chapters[i].quizzes:
                    quizzes[i].append(quiz)
            return render_template("users/search.html", chapters = chapters , quizzes = quizzes , title = "Chapter")
        elif chosen == "subject":
            subjects = Subjects.query.filter(Subjects.subject_name.like(f'%{search}%')).all()
            chapters = [[] for i in range(len(subjects))]
            quizzes = [[] for i in range(len(subjects))]
            for i in range(len(subjects)):
                for chapter in subjects[i].chapters:
                    chapters[i].append(chapter)
                    quizzes[i] = [[] for j in range(len(chapters[i]))]
                    for j in range(len(chapters[i])):
                        for quiz in chapters[i][j].quizzes:
                            quizzes[i][j].append(quiz)
            return render_template("users/search.html", subjects = subjects ,chapters = chapters , quizzes = quizzes , title = "Subject")
        else:
            scores = Scores.query.filter_by(total_marks_scored = search).all()
            quizzes  = [Quizzes.query.get(score.quiz_id) for score in scores]
            return render_template("users/search.html", quizzes = quizzes , scores = scores , title = "Score")
    return redirect(url_for("home"))





