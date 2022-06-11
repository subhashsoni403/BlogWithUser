from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey , Table, Column, Integer
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, Login, Register, Comment
from flask_gravatar import Gravatar
from functools import wraps


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    author_id = db.Column(db.Integer, ForeignKey('user.id'))
    blog_cmt = relationship('BlogComment')

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    post = relationship('BlogPost')
    comment = relationship('BlogComment')

class BlogComment(db.Model):
    __tablename__ = 'blog_comment'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    blog_id = db.Column(db.Integer, ForeignKey('blog_posts.id'))

## DEFINE RELATIONSHIP

db.create_all()

## LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Login Manager Loading User
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts, user = current_user, logged_in = current_user.is_authenticated)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = Register()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email = form.email.data).first()
        if user:
            flash('This email already exists try another one')
            return redirect(url_for('login'))
        else :
            new_user = User(
                name = form.name.data,
                email = form.email.data,
                password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length= 8)
            )
            db.session.add(new_user)
            db.session.commit()
            flash('New User has been created')
            return redirect(url_for('get_all_posts'))
    return render_template("register.html", form = form, logged_in = current_user.is_authenticated)


@app.route('/login',methods=['POST', 'GET'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email = form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('You are successfully logged in')
                return redirect(url_for('get_all_posts'))
            else:
                flash('Please check your password')
                return redirect(url_for('login'))
        else:
            flash('Please check you mail id')
            return redirect(url_for('login'))

    return render_template("login.html", form = form, logged_in = current_user.is_authenticated)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=['POST', 'GET'])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    comments = BlogComment.query.filter_by(blog_id = post_id).all()
    comment_form = Comment()
    if comment_form.validate_on_submit():
        new_comment =  BlogComment(comment=comment_form.blog_comment.data, user_id = current_user.id, blog_id = post_id)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('show_post', post_id= post_id))
    return render_template("post.html", post=requested_post, user = current_user, logged_in = current_user.is_authenticated, cmt_form = comment_form, comments = comments)


@app.route("/about")
def about():
    return render_template("about.html", logged_in = current_user.is_authenticated)


@app.route("/contact")
def contact():
    return render_template("contact.html", logged_in = current_user.is_authenticated)


@app.route("/new-post", methods=['POST', 'GET'])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user.name,
            date=date.today().strftime("%B %d, %Y"),
            author_id = current_user.id
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, user = current_user, logged_in = current_user.is_authenticated)


@app.route("/edit-post/<int:post_id>", methods=['POST','GET'])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, user = current_user, logged_in = current_user.is_authenticated)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
