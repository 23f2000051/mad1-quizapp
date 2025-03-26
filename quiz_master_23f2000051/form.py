from flask_wtf import FlaskForm
from wtforms import StringField , PasswordField , SubmitField , FloatField, TextAreaField , IntegerField , SelectField , DateField
from wtforms.validators import DataRequired , Length , Email , EqualTo , ValidationError , NumberRange
from quiz_master_23f2000051.models import Users, Quizzes , Chapters 


chapter_name = [chapter.chapter_name for chapter in Chapters.query.all()]
for i in range(len(chapter_name)):
    chapter_name[i] = (chapter_name[i] , chapter_name[i])

class RegistrationForm(FlaskForm):
    username = StringField('Username' ,
                           validators  = [DataRequired() , Length(min=2 , max = 20)])
    name = StringField('Name' ,
                           validators  = [DataRequired() , Length(min=2 , max = 30)])
    email = StringField('Email' ,
                        validators = [DataRequired() , Email()])
    password = PasswordField('Password' ,
                            validators  = [DataRequired()])
    confirm_password = PasswordField('Confirm Password' ,
                            validators  = [DataRequired() , EqualTo('password')])
    submit = SubmitField('SignUp')

    def validate_username(self , username):
        user = Users.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError("Username Already Taken! Please Use Another Username.")
        
    def validate_email(self , email):
        email_given = Users.query.filter_by(email = email.data).first()
        if email_given:
            raise ValidationError("Email Already Taken! Please Use Another Email.")
        try:
            index_at = email.data.index("@")
            for i in range(index_at+1,len(email.data)):
                if not(email.data[i].isalpha() or email.data[i] in "-." or email.data[i].isdigit()):
                    raise ValidationError("Enter a Valid Email!")
        except:
            raise ValidationError("Enter a Valid Email!")
                

    
class LoginForm(FlaskForm):
    username = StringField('Username' ,
                           validators  = [DataRequired() , Length(min=2 , max = 20)])
    password = PasswordField('Password',validators  = [DataRequired()])
    login = SubmitField('Login')


        
class SubjectForm(FlaskForm):
    name = StringField('Subject Name' , 
                       validators = [DataRequired(), Length(min=2 , max = 40)])
    code = StringField('Subject Code' ,
                          validators = [DataRequired(), Length(min=2 , max = 10)])
    description = TextAreaField('Subject Description',
                                validators=[DataRequired()])
    save = SubmitField('Save')
    
class ChapterForm(FlaskForm):
    name = StringField('Chapter Name',
                       validators = [DataRequired(), Length(min=2 , max = 40)])
    description = TextAreaField('Chapter Description',
                                validators=[DataRequired()])
    save = SubmitField('Save')

    
class QuizForm(FlaskForm):
    name = StringField('Quiz Name',
                       validators = [DataRequired(), Length(min=2 , max = 40)])
    date = DateField('Quiz Date', format='%Y-%m-%d', validators=[DataRequired()])
    time = IntegerField("Total Time (in minutes)",
                         validators=[DataRequired() , NumberRange(min=1 , max= 500)])
    save = SubmitField('Save')

        
class QuestionForm(FlaskForm):
    title = StringField('Question Title',
                       validators = [DataRequired(), Length(min=2 , max = 40)])
    statement = TextAreaField('Question Statement',
                       validators = [DataRequired(), Length(min=2 , max = 1000)])
    option1 = StringField('Option 1',
                          validators = [DataRequired()])
    option2 = StringField('Option 2',
                            validators = [DataRequired()])
    option3 = StringField('Option 3')
    option4 = StringField('Option 4')
    answer = SelectField('Correct Option',
                         choices= [('option1' , 'Option 1'),('option2' , 'Option 2'),('option3' , 'Option 3'),('option4' , 'Option 4')],validators = [DataRequired()])
    marks = FloatField('Marks(per Qs.)' ,
                         validators=[DataRequired() , NumberRange(min=0.5 , max = 20)])
    save = SubmitField('Save And Next')

class QuizForm2(FlaskForm):
    name = StringField('Quiz Name',
                       validators = [DataRequired(), Length(min=2 , max = 40)])
    date = DateField('Quiz Date', format='%Y-%m-%d', validators=[DataRequired()])
    time = IntegerField("Total Time (in minutes)",
                         validators=[DataRequired() , NumberRange(min=1 , max= 500)])
    chapter = SelectField('Chapter' , validators = [DataRequired()] , choices=chapter_name)
    save = SubmitField('Save')