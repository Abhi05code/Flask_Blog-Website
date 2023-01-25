from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json
import re
import os
import math
from datetime import datetime, timedelta
from sqlalchemy import or_

from werkzeug.utils import secure_filename

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key = b'_5sfasf#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']

app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)

class Userinfo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    country = db.Column(db.String(80), nullable=False)
    contactno = db.Column(db.Integer, nullable=False)
    occupation = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    birthdate = db.Column(db.String(12), nullable=False)
    image = db.Column(db.String(12), nullable=True)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)

    content = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    name = db.Column(db.String(80), nullable=False)


app.permanent_session_lifetime = timedelta(minutes=1)

@app.route('/search', methods=['POST'])
def search():
    search_query = "%{}%".format(request.form['search_query'])
    posts = Posts.query.filter(or_(Posts.title.like(search_query), Posts.name.like(search_query))).all()
    print(posts)
    return render_template('search.html',params=params, posts=posts)

def password_check(password):
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"

    # compiling regex
    pat = re.compile(reg)

    # searching regex
    mat = re.search(pat, password)
    if mat:
        return True
    else:
        return False


@app.route("/")
def home():


    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts) / int(params['no_of_posts']))
    # [0: params['no_of_posts']]
    # posts = posts[]
    page = request.args.get('page')

    if (not str(page).isnumeric()):
        page = 1
    page = int(page)

    posts = posts[(page - 1) * int(params['no_of_posts']): (page - 1) * int(params['no_of_posts']) + int(
        params['no_of_posts'])]
    # Pagination Logic
    # First
    if (page == 1):
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif (page == last):
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)
    return render_template('index.html', params=params, posts=posts , prev=prev, next=next)


 # post entry on dashboard

@app.route("/post/<int:sno>", methods = ['GET', 'POST'])
def post_route(sno):
    user = Userinfo.query.filter_by(sno=sno).first()
    email = user.email
    name = user.name
    current_date = datetime.now()
    date = current_date.strftime("%Y-%m-%d %H:%M:%S")
    title = request.form['title']
    content = request.form['content']
    entry = Posts(email=email, title=title, content=content, date= date, name=name)
    db.session.add(entry)
    db.session.commit()
    count = Posts.query.filter_by(email=email).count()
    posts = Posts.query.filter_by(email=email).all()
    return render_template('dashboard1.html', params=params, user = user, count = count, posts=posts)

 # post display on dashboard
@app.route("/postdisplay/<int:sno>", methods = ['GET', 'POST'])
def post_display(sno):
    posts = Posts.query.filter_by(sno=sno).first()

    return render_template('postdisplay.html', params=params, posts = posts)



 # password change on dashboard
@app.route("/edit/<int:sno>", methods=['GET', 'POST'])
def update(sno):
    user = Userinfo.query.filter_by(sno=sno).first()

    if request.method == 'POST':
        user.password = request.form['password']
        file = request.files['file']
        if password_check(user.password):
            user.password = generate_password_hash(user.password)
            if file.filename == '':

                db.session.commit()

            else:

                # UPLOAD IMAGE FILE
                file = request.files['file']

                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.image = filename
                db.session.commit()
        else:
            flash("Password is not in correct format", 'danger')




    return render_template('dashboard1.html', params=params, user = user)

 # login page
@app.route("/login")
def login():


    return render_template('login.html', params=params)



 # register page
@app.route("/register", methods = ['GET', 'POST'])
def register():
    if (request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        birthdate = request.form.get("birthdate")
        country = request.form.get('country')
        contactno = request.form.get('contactno')

        occupation = request.form.get('occupation')
        email_exists = Userinfo.query.filter_by(email=email).first()
        date_object = datetime.strptime(birthdate, "%Y-%m-%d")
        formatted_date = date_object.strftime("%d-%m-%Y")

        # UPLOAD IMAGE FILE
        file = request.files['file']

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # filename = secure_filename(file.filename)
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


        image = filename
        if email_exists:
            flash("Email already exists", 'danger')
            return redirect('/register')
        else:


            # validating conditions
            if password_check(password):

                hashed_password = generate_password_hash(password)
                entry = Userinfo(name=name, email=email, password=hashed_password, birthdate=formatted_date, country = country, occupation = occupation, contactno = int(contactno), image = image )
                db.session.add(entry)
                db.session.commit()
                flash("Account Created", "success")


            else:

                flash("Password is not in correct format", 'danger')




    return render_template('register.html', params=params)


 # dashboard page
@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if ('user' in session):

        user = Userinfo.query.filter_by(email=session['email']).first()
        count = Posts.query.filter_by(email=session['email']).count()
        posts = Posts.query.filter_by(email=session['email']).all()
        return render_template('dashboard1.html', params=params, user = user, count = count, posts=posts )


    if request.method=='POST':
        # Check the user's login credentials
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        user = Userinfo.query.filter_by(email=username).first()

        password_hash = user.password

        if check_password_hash(password_hash, userpass):
            # create session data, we can access this data in other routes
            session.permanent = True
            session['loggedin'] = True
            session['user'] = user.name
            session['email'] = username
            return redirect('/dashboard')
        else:
            flash("Password Mismatched", 'danger')
            return render_template('login.html', params=params)





    else:
        return render_template('login.html', params=params)


@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route('/logout')
def logout():
    # Remove session data
    session.pop('loggedin', None)
    session.pop('user', None)
    session.pop('email', None)
    return redirect('/')

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        current_date = datetime.now()
        date = current_date.strftime("%Y-%m-%d %H:%M:%S")
        entry = Contacts(name=name, phone_num = phone, msg = message, date= date ,email = email )
        db.session.add(entry)
        db.session.commit()

    return render_template('contact.html', params=params)


app.run(debug=True)
