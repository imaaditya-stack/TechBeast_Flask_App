from flask import Flask, render_template, request, flash, logging, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash 
from functools import wraps
from datetime import datetime

app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tb.sqlite3'

db = SQLAlchemy(app)

app.secret_key = "151FAHUI216892GAOP"

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(200), nullable=False)
    tags = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
        
@app.route("/")

def home(): 

    session.clear()
    return render_template("home.html")

@app.route("/login") 

def login():
    
    return render_template("login.html")

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized Login","danger")
            return render_template("login.html")
    return wrap

@app.route("/success", methods=["GET", "POST"])
def loginsuccess():
    
    if request.method == "POST":
        
        email = request.form["email"]
        password = request.form["pass"]
        validate_user = Users.query.filter_by(email=email).first()

    if validate_user and check_password_hash(validate_user.password, password):
            
        session["logged_in"] = True
        session["username"] = validate_user.username
        return redirect(url_for("articles"))
            
    else:
            
        flash("Invalid Credentials ! Please enter correct email and password", "danger")
        return redirect(url_for("login"))

@app.route("/signup")

def signup():
    
    return render_template("signup.html")

@app.route("/signupsuccess", methods=["GET", "POST"])

def signupsuccess():
    
    if request.method == "POST":
        
        name = request.form["name"]
        email = request.form["email"]
        _password = request.form["pass"]
        _hashpass = generate_password_hash(_password)
        _cpassword = request.form["cpass"]
        validate_username = Users.query.filter_by(username=name).first()
        validate_email = Users.query.filter_by(email=email).first()
    
    if validate_username:
        
        flash("Ooops, Username already exists, please choose a different username, sorry !", "danger")
        return render_template("signup.html")
    
    if validate_email:
        
        flash("Email already exists, please choose a different email !", "danger")
        return render_template("signup.html")
    
    if len(name) < 3:
        
        flash("Username should contain more than 3 characters", "danger")
        return render_template("signup.html")
    
    if _password != _cpassword:
        
        flash("Ooops, Passwords do not match !", "danger")
        return render_template("signup.html")
            
    else:
            
        user =  Users(name, email, _hashpass)
        db.session.add(user)
        db.session.commit()
        return render_template("login.html", msg = True)
    
    return render_template("main.html")
    
@app.route("/getstarted")
@is_logged_in
def getstarted():
    
    return render_template("signupinfo.html")

@app.route("/logout")   
@is_logged_in
def logout():
       
    session.clear()
    flash("You are logged out, see you soon :)", "success")
    return render_template("login.html")       


@app.route("/postarticle")   
@is_logged_in
def postarticle():
    return render_template("articleform.html")


@app.route("/articles", methods=["GET", "POST"])   
@is_logged_in
def articles():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["editor"]
        cat = request.form["cat"]
        tags = request.form["tag"]
        post = Post(title=title, content=content, category=cat, tags=tags)
        db.session.add(post)
        db.session.commit()
    return render_template("articles.html", articles = Post.query.order_by(desc(Post.date_created)).all())

@app.route("/articles/<int:ID>")
@is_logged_in
def viewarticle(ID):
    article = Post.query.filter_by(id=ID).first()
    return render_template("article.html", article=article)
    
@app.route("/edit/<int:ID>", methods = ["GET", "POST"])
@is_logged_in
def edit(ID):
    article = Post.query.filter_by(id=ID).first()
    return render_template("edit.html",article=article)  

@app.route("/update/<int:ID>", methods = ["GET", "POST"])
@is_logged_in
def update(ID):
    article = Post.query.filter_by(id=ID).first()
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["editor"]
        cat = request.form["cat"]
        tags = request.form["tag"]
    article.title = title
    article.content = content
    article.category = cat
    article.tags = tags
    db.session.commit()
    flash("Article Updated Successfully !", "success")
    return render_template("article.html", article=article)
    
@app.route("/delete/<int:ID>", methods = ["GET", "POST"])
@is_logged_in
def delete(ID):
    article = Post.query.filter_by(id=ID).first()
    flash("Article titled ~ "+article.title+" deleted successfully !","danger")
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for("articles"))

@app.route("/preview", methods = ["GET", "POST"])
@is_logged_in
def preview():
    title, content, cat, tags = "","","",""
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["editor"]
        cat = request.form["cat"]
        tags = request.form["tag"]
    return render_template("preview.html",title=title,content=content,tags=tags)

@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
