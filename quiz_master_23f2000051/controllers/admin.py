from quiz_master_23f2000051 import app , db , bcrypt
from flask import request , render_template , redirect , url_for , flash , jsonify
from quiz_master_23f2000051.models import Users , Subjects , Chapters , Quizzes , Questions , Scores
from quiz_master_23f2000051.form import RegistrationForm , LoginForm , SubjectForm , ChapterForm , QuizForm , QuestionForm , QuizForm2
from flask_login import login_user , current_user , logout_user , login_required




@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    subjects = Subjects.query.all()
    return render_template("admin/dashboard.html" , subjects = subjects)

@app.route('/search' , methods = ["GET" , "POST"])
@login_required
def search():
    if request.method == "POST":
        search = request.form.get("search")
        chosen = request.form.get("options")

        
        if not search:
            flash("Search-Field Empty, Showing All Results!" , "primary") 
            
        if chosen == "user":
            users = Users.query.filter(Users.username.like(f'%{search}%')).all()
            return render_template("admin/search.html", users = users , title = "Users")
        elif chosen == "subject":
            subjects = Subjects.query.filter(Subjects.subject_name.like(f'%{search}%')).all()
            return render_template("admin/search.html", subjects = subjects , title = "Subjects")
        else:
            quizzes = Quizzes.query.filter(Quizzes.quiz_name.like(f'%{search}%')).all()
            return render_template("admin/search.html", quizzes = quizzes , title = "Quizzes")    
    return redirect(url_for("admin_dashboard"))


@app.route('/admin/block/<int:id>')
@login_required 
def block_user(id):
    user = Users.query.get(id)
    user.active = False
    db.session.commit() 
    message = 'User has been blocked successfully!'
    flash(message , 'success') 
    return redirect(url_for('search'))         

@app.route('/admin/unblock/<int:id>')
@login_required 
def unblock_user(id):
    user = Users.query.get(id)
    user.active = True
    db.session.commit() 
    message = 'User has been unblocked successfully!'
    flash(message , 'success')          
    return redirect(url_for('search'))         
 


@app.route('/subject/view/<int:id>')
@login_required
def view_details(id):
   subject = Subjects.query.get(id)
    
   return render_template("admin/sub_details.html" , subject = subject , title = "Subject Details")

@app.route('/subject/delete/<int:id>')
@login_required
def delete_subject(id):
    subject = Subjects.query.get(id)
    Chapters.query.filter_by(subject_id = id).delete()
    for chapter in Chapters.query.filter_by(subject_id = id).all():
        Quizzes.query.filter_by(chapter_id = chapter.chapter_id).delete()
        for quiz in Quizzes.query.filter_by(chapter_id = chapter.chapter_id).all():
            Questions.query.filter_by(quiz_id = quiz.quiz_id).delete()
    db.session.delete(subject)
    db.session.commit()
    message = 'Subject has been deleted successfully!'
    flash(message , 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/add_subject' , methods = ["GET","POST"])
@login_required
def add_subject():
    form = SubjectForm()
    if form.validate_on_submit():
        existing_subject = Subjects.query.filter_by(subject_code = form.code.data.strip()).first()
        if not existing_subject:
            existing_subject = Subjects.query.filter_by(subject_name = form.name.data.strip()).first()
            if not existing_subject:
                subject = Subjects(subject_name = form.name.data.strip() , subject_code = form.code.data.strip() , subject_description = form.description.data.strip())
                db.session.add(subject)
                db.session.commit()
                message = f'Subject "{form.name.data}" has been added successfully!'
                flash(message,'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash("Subject Name Already Taken! Please Use Another Subject Name." , 'danger')
        else:
            flash("Subject Code Already Taken! Please Use Another Subject Code." , 'danger')
    return render_template("admin/sub_addition.html" , form = form , title = "Add Subjects")

@app.route('/subject/update/<int:id>' , methods = ["GET","POST"])
@login_required
def update_subject(id):
    form = SubjectForm()
    form.is_update = True
    subject = Subjects.query.get(id)
    if form.validate_on_submit():
        existing_subject = Subjects.query.filter_by(subject_code = form.code.data.strip()).first()
        if subject.subject_code == form.code.data.strip() or not existing_subject:
            existing_subject = Subjects.query.filter_by(subject_name = form.name.data.strip()).first()
            if subject.subject_name == form.name.data.strip() or not existing_subject:
                subject.subject_code = form.code.data.strip()
                subject.subject_name = form.name.data.strip()
                subject.subject_description = form.description.data.strip()
                db.session.commit()
                message = f'Subject "{form.name.data}" has been updated successfully!'
                flash(message,'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash("Subject Name Already Taken! Please Use Another subject Name." , 'danger')
        else:
            flash("Subject Code Already Taken! Please Use Another subject Code." , 'danger')
    form.code.data = subject.subject_code
    form.name.data = subject.subject_name
    form.description.data = subject.subject_description
    return render_template("admin/sub_update.html" , form = form , title = "Update Subject")

# ------------------------Chapter---------------------------------------

@app.route('/subject/<int:sub_id>/add_chapter' , methods = ["GET","POST"])
@login_required
def add_chapter(sub_id):
    form = ChapterForm()
    if form.validate_on_submit():
        existing_chapter = Chapters.query.filter_by(chapter_name = form.name.data.strip()).first()
        if existing_chapter:
            flash("Chapter Name Already Taken! Please Use Another Chapter Name." , 'danger')
            return render_template("admin/chapters/add_chapters.html" , form = form , title = "Add Chapters")
        chapter = Chapters(chapter_name = form.name.data.strip() , chapter_description = form.description.data.strip() , subject_id = sub_id)
        db.session.add(chapter)
        db.session.commit()
        message = f'Chapter "{form.name.data.strip()}" has been added successfully!'
        flash(message,'success')
        return redirect(url_for('admin_dashboard'))
    return render_template("admin/chapters/add_chapters.html" , form = form , title = "Add Chapters")

@app.route('/update/chapter/<int:chap_id>' , methods = ["GET","POST"])
@login_required
def update_chapter(chap_id):
    form = ChapterForm()
    chapter = Chapters.query.get(chap_id)
    if form.validate_on_submit():
        existing_chapter = Chapters.query.filter_by(chapter_name = form.name.data.strip()).first()
        if chapter.chapter_name == form.name.data.strip() or not existing_chapter:
            chapter.chapter_name = form.name.data.strip()
            chapter.chapter_description = form.description.data.strip()
            db.session.commit()
            message = f'Chapter "{form.name.data.strip()}" has been updated successfully!'
            flash(message,'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Chapter Name Already Taken! Please Use Another Chapter Name." , 'danger')
            form.name.data = chapter.chapter_name
            form.description.data = chapter.chapter_description
            return render_template("admin/chapters/update_chapter.html" , form = form , title = "Update Chapter")
    form.name.data = chapter.chapter_name
    form.description.data = chapter.chapter_description
    return render_template("admin/chapters/update_chapter.html" , form = form , title = "Update Chapter")

@app.route('/delete/chapter/<int:chap_id>' , methods = ["GET","POST"])
@login_required
def delete_chapters(chap_id):
    chapter = Chapters.query.get(chap_id)
    Quizzes.query.filter_by(chapter_id = chap_id).delete()
    for quiz in Quizzes.query.filter_by(chapter_id = chap_id).all():
        Questions.query.filter_by(quiz_id = quiz.quiz_id).delete()
    db.session.delete(chapter)
    db.session.commit()
    message = 'Chapter has been deleted successfully!'
    flash(message , 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/view/chapter/<int:id>')
@login_required
def view_chapters(id):
    chapter = Chapters.query.get(id)
    return render_template("admin/chapters/chapters.html" , chapter = chapter , title = "Chapter Details")

# ------------------------Quiz---------------------------------------

@app.route('/chapter/<int:chap_id>/add_quiz' , methods = ["GET","POST"])
@login_required
def add_quiz(chap_id):
    form = QuizForm()
    if form.validate_on_submit():
        existing_quiz = Quizzes.query.filter_by(quiz_name = form.name.data.strip()).first()
        if existing_quiz:
            flash("Quiz Name Already Taken! Please Use Another Quiz Name." , 'danger')
            return render_template("admin/quiz/add_quiz.html" , form = form , title = "Add Quiz")
        quiz = Quizzes(quiz_name = form.name.data.strip(), quiz_date = form.date.data ,time_duration = form.time.data , chapter_id = chap_id)
        db.session.add(quiz)
        db.session.commit()
        message = f'Quiz "{form.name.data.strip()}" has been added successfully!'
        flash(message,'success')
        return redirect(url_for('view_chapters' , id = chap_id))
    return render_template("admin/quiz/add_quiz.html" , form = form , title = "Add Quiz")

@app.route('/update/quiz/<int:quiz_id>' , methods = ["GET","POST"])
@login_required
def update_quiz(quiz_id):
    form = QuizForm()
    quiz = Quizzes.query.get(quiz_id)
    if form.validate_on_submit():
        existing_quiz = Quizzes.query.filter_by(quiz_name = form.name.data.strip()).first()
        if quiz.quiz_name == form.name.data.strip() or not existing_quiz:
            quiz.quiz_name = form.name.data.strip()
            quiz.quiz_date = form.date.data
            quiz.time_duration = form.time.data
            db.session.commit()
            message = f'Quiz "{form.name.data.strip()}" has been updated successfully!'
            flash(message,'success')
            return redirect(url_for('view_quiz' , quiz_id = quiz_id))
        else:
            flash("Quiz Name Already Taken!!" "danger")
            redirect(url_for("update_quiz" , quiz_id = quiz_id))
    form.name.data = quiz.quiz_name
    form.date.data = quiz.quiz_date
    form.time.data = quiz.time_duration
    return render_template("admin/quiz/update_quiz.html" , form = form , title = "Update Quiz")

@app.route('/delete/quiz/<int:quiz_id>' , methods = ["GET","POST"])
@login_required
def delete_quiz(quiz_id):
    quiz = Quizzes.query.get(quiz_id)
    chap_id = quiz.chapter_id
    Questions.query.filter_by(quiz_id = quiz_id).delete()
    Scores.query.filter_by(quiz_id = quiz_id).delete()
    db.session.delete(quiz)
    db.session.commit()
    message = 'Quiz has been deleted successfully!'
    flash(message , 'success')
    return redirect(url_for('view_chapters' , id = chap_id)) 

@app.route('/view/quiz/<int:quiz_id>' , methods = ["GET" , "POST"])
@login_required
def view_quiz(quiz_id):
    quiz = Quizzes.query.get(quiz_id)
    Total_marks = 0
    questions = quiz.questions
    for i in questions :
        Total_marks+=i.marks
    return render_template("admin/quiz/quiz.html" , title = "Quiz-Details" , quiz = quiz , Total_marks = Total_marks)

@app.route('/quiz_addition' , methods = ["GET" , "POST"])
@login_required
def quiz_addition():
    form = QuizForm2()
    chapter_name = [chapter.chapter_name for chapter in Chapters.query.all()]
    for i in range(len(chapter_name)):
        chapter_name[i] = (chapter_name[i] , chapter_name[i])
    form.chapter.choices = chapter_name
    quizzes = Quizzes.query.all()
    if form.validate_on_submit():
        existing_quiz = Quizzes.query.filter_by(quiz_name = form.name.data.strip()).first()
        if existing_quiz:
            flash("Quiz Name Already Taken! Please Use Another Quiz Name." , 'danger')
            return render_template("admin/quiz/add_quiz2.html" , title = "Add Quiz"  , form = form)
        chapter = Chapters.query.filter_by(chapter_name = form.chapter.data.strip()).first()
        chap_id = chapter.chapter_id
        quiz = Quizzes(quiz_name = form.name.data.strip(), quiz_date = form.date.data ,time_duration = form.time.data , chapter_id = chap_id)
        db.session.add(quiz)
        db.session.commit()
        quizzes = Quizzes.query.all()
        chapters= []
        subjects = []   
        for quiz in quizzes:
            chapter = Chapters.query.get(quiz.chapter_id)
            chapters.append(chapter)
            subject = Subjects.query.get(chapter.subject_id)
            subjects.append(subject)
        message = f'Quiz "{form.name.data.strip()}" has been added successfully!'
        flash(message,'success')
        return render_template("admin/quiz/quizzes.html" , title = "Quiz" , quizzes = quizzes , chapters = chapters , subjects = subjects)
    return render_template("admin/quiz/add_quiz2.html" , title = "Quiz" , form = form)

@app.route("/quiz" , methods = ["GET" , "POST"])
@login_required
def quiz():
    quizzes = Quizzes.query.all()
    chapters= []
    subjects = []   
    for quiz in quizzes:
        chapter = Chapters.query.get(quiz.chapter_id)
        chapters.append(chapter)
        subject = Subjects.query.get(chapter.subject_id)
        subjects.append(subject)
    return render_template("admin/quiz/quizzes.html" , title = "Quiz" , quizzes = quizzes , chapters = chapters , subjects = subjects)
#---------------------------Question------------------------------

@app.route("/quiz/<int:quiz_id>/add_question" , methods = ["GET" , "POST"])
@login_required
def add_qs(quiz_id):
    form = QuestionForm()
    if form.validate_on_submit():
        question = Questions.query.filter_by(title = form.title.data.strip() , quiz_id = quiz_id).first()
        if question:
            flash("Title Already Taken.Use Another!" , "Danger")
            return render_template("admin/questions/add_qs.html" , form = form , title = "Add Question" , quiz_id = quiz_id)
        question = Questions(title = form.title.data.strip() , statement = form.statement.data.strip(), 
                             option1 = form.option1.data.strip() , option2 = form.option2.data.strip(),
                             option3 = form.option3.data.strip(), option4 = form.option4.data.strip(),
                             answer = form.answer.data.strip() , marks = form.marks.data , quiz_id = quiz_id)
        quiz = Quizzes.query.filter_by(quiz_id = quiz_id).first()
        quiz.total_marks+=form.marks.data
        db.session.add(question)
        db.session.commit()
        form  = QuestionForm()
        flash("Question Added" , "success")
        return redirect(url_for('add_qs' , quiz_id = quiz_id))
    return render_template("admin/questions/add_qs.html" , form = form , title = "Add Question" , quiz_id = quiz_id)


@app.route('/delete/question/<int:question_id>' , methods = ["GET","POST"])
@login_required
def delete_question(question_id):
    quizzes = Quizzes.query.all()
    question = Questions.query.get(question_id)
    quiz_id = question.quiz_id
    quiz = Quizzes.query.filter_by(quiz_id = quiz_id).first()
    quiz.total_marks-= question.marks
    db.session.delete(question)
    db.session.commit()
    message = 'Question has been deleted successfully!'
    flash(message , 'success')
    url = request.referrer
    print(url)
    if url == "http://127.0.0.1:5000/quiz" or url == "http://localhost:5000/quiz":
        return redirect(url_for('quiz'))
    return redirect(url_for('view_quiz' , quiz_id = quiz_id))

@app.route('/view/question/<int:question_id>' , methods = ["GET" , "POST"])
@login_required
def view_question(question_id):
    question = Questions.query.get(question_id)
    return render_template("admin/questions/question.html" , title = "Question-Details" , question = question)

@app.route('/update/question/<int:question_id>' , methods = ["GET","POST"])
@login_required
def update_question(question_id):
    form = QuestionForm()
    question = Questions.query.get(question_id)
    quiz_id = question.quiz_id

    if form.validate_on_submit():
        existing_question = Questions.query.filter_by(title = form.title.data.strip()).first()
        if question.title == form.title.data.strip() or not existing_question:
            quiz = Quizzes.query.filter_by(quiz_id = quiz_id).first()
            quiz.total_marks-= question.marks
            question.title  = form.title.data.strip()
            question.statement = form.statement.data.strip()
            question.option1 = form.option1.data.strip()
            question.option2 = form.option2.data.strip()
            question.option3 = form.option3.data.strip()
            question.option4 = form.option4.data.strip()
            question.answer = form.answer.data.strip()
            question.marks = form.marks.data
            quiz.total_marks+= form.marks.data

            db.session.commit()
            flash("Question Updated Successfully" , "success")
            return redirect(url_for("view_question" , question_id = question_id , quiz_id = quiz_id))
        else:
            flash("Title Already Taken! Please use Another!")
    form.title.data = question.title
    form.statement.data = question.statement
    form.option1.data = question.option1
    form.option2.data = question.option2
    form.option3.data = question.option3
    form.option4.data = question.option4
    form.answer.data = question.answer
    form.marks.data = question.marks

    return render_template("admin/questions/update_qs.html" , form = form , title = "Update Question" , quiz_id = quiz_id)

#-----------------------------------------------Summmary--------------------------------------------------
@login_required
@app.route("/summary" , methods = ['GET','POST'])
def summary():
    scores = Scores.query.all()
    sub_freq = dict()
    sub_names = []
    sub_users = []
    top_users = []
    for score in scores:
        quiz_id = score.quiz_id
        quiz = Quizzes.query.get(quiz_id)
        chapter_id = quiz.chapter_id
        chapter = Chapters.query.get(chapter_id)
        subject_id = chapter.subject_id
        subject = Subjects.query.get(subject_id)
        if subject.subject_name in sub_freq:
            sub_freq[subject.subject_name][0]+=1
            if score.total_marks_scored == quiz.total_marks:
                sub_freq[subject.subject_name][1]+=1
        else:
            sub_freq[subject.subject_name] = [1 , 0]
            if score.total_marks_scored == quiz.total_marks:
                sub_freq[subject.subject_name][1]+=1
    for key in sub_freq:
        sub_names.append(key)
        sub_users.append(sub_freq[key][0])
        top_users.append(sub_freq[key][1])
    return render_template("/admin/summary/chart.html" , title = "Summary" , sub_names = sub_names , sub_users = sub_users , top_users = top_users)