from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, email, Length
from flask_ckeditor import CKEditorField


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class Login(FlaskForm):
    email = StringField('email', validators=[DataRequired(),email()])
    password = PasswordField('password', validators=[DataRequired(),Length(min=8,max=15)])
    submit = SubmitField('Login')

class Register(FlaskForm):
    name = StringField('name',validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), email()])
    password = PasswordField('password', validators=[DataRequired(),Length(min=8,max=15)])
    submit = SubmitField('Register')

class Comment(FlaskForm):
    blog_comment = CKEditorField('comment')
    submit = SubmitField('Post Comment')