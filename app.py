# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash,g
from functools import wraps
import sqlite3
from passlib.hash import sha256_crypt,pbkdf2_sha256#for password hashing 


# create the application object
app = Flask(__name__)

# config
app.secret_key = 'my precious'
app.database = 'sample.db'
app.database2='usersDB.db'

# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            #flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


# logout required decorator
def logout_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            return f(*args, **kwargs)
        else:
            session.pop('logged_in', None)#logging out
            return render_template('signup.html')
    return wrap



# use decorators to link the function to a url
@app.route('/')
@login_required
def home():
    g.db = connect_db()# fun created by us
    cur = g.db.execute('select * from posts')
    posts = [dict(title=row[0], details=row[1]) for row in cur.fetchall()]
    g.db.close()
    return render_template('index.html', posts=posts)  # render a template
    #return render_template('index.html')  # render a template
    #return "Hello, World!"  # return a string

'''
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template
'''    

# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usernameEntered=request.form['username']
        passwordEntered=request.form['password']
        g.db2 = connect_db2()
        hashedPassword = g.db2.execute("SELECT * FROM users WHERE username =:who",{"who":usernameEntered})
        if hashedPassword.fetchone() is not None:
            hashedPassword = g.db2.execute("SELECT password FROM users WHERE username =:who",{"who":usernameEntered})
            hashedPasswordValue=hashedPassword.fetchone()[0]
            if not sha256_crypt.verify(passwordEntered, hashedPasswordValue):
                error = 'Invalid Credentials. Please try again.'
            else:
                session['logged_in']= True
                flash('You were logged in.')
                return redirect(url_for('home'))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET','POST'])
@logout_required
def signup():
    error = None
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        password2=request.form['password2']
        email=request.form['email']
        g.db2 = connect_db2()
        uname = g.db2.execute("SELECT username FROM users WHERE username =:who",{"who":username})
        eml=g.db2.execute("SELECT email FROM users WHERE email =:whatMail",{"whatMail":email})
        if len(username)<4:
            error = 'Username must be atleast 4 characters long'
        elif uname.fetchone() is not None:
            error = 'Username already exists'
        elif eml.fetchone() is not None:
            error = 'Email already exists'   
        elif  len(password)<4:   
             error = 'Password must be atleast 4 characters long' 
        else:
            if password != password2:
                error = 'Password don\'t match.'
            else:
                flash('Sign up completed')
                ## sending to usersDB
                #g.db2 = connect_db2()# function created by us also it is shifted to above as we need to check for existence
                password = sha256_crypt.encrypt(password)#hashing password for security
                print(password)
                g.db2.execute('insert into users (username,password,email) values '\
                    '(?,?,?)',[username,
                                password,
                                email])
                g.db2.commit()
                g.db2.close()
                #fetching the usersDB
                # cur2 = g.db2.execute('select * from users')
                # users = [dict(username=row[0], password=row[1],email=row[2]) for row in cur2.fetchall()]
                # print(users)
                # g.db2.close()
                return redirect(url_for('login'))
    return render_template('signup.html',error=error)  


@app.route('/index', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        rfc=request.form['rfc']
        return "Hello "+rfc
    


# connect to database
def connect_db():
    return sqlite3.connect(app.database)

# connect to database2
def connect_db2():
    return sqlite3.connect(app.database2)    

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)