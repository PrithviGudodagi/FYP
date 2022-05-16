from flask import Flask, render_template, url_for, request, session, redirect
from pymongo import MongoClient
import bcrypt

app  = Flask(__name__)
app.secret_key = "super secret key"

client = MongoClient()
client = MongoClient('localhost', 27017)
db = client['organizationdata']


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logindata', methods =["GET", "POST"])
def logindata():
    loginuser = db.orgdata.find_one({'email' : request.form['email']})

    if loginuser:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), loginuser['password']) == loginuser['password']:
            session['email'] = request.form['email']
            return redirect(url_for('dashboard'))

    return 'invalid username/password combination'




@app.route('/register', methods =["GET", "POST"])
def register():
    if request.method == 'POST':
        
        existing_user = db.orgdata.find_one({'email' : request.form['email']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            db.orgdata.insert_one({'name' : request.form['name'], 'email' : request.form['email'] , 'password' : hashpass})
            session['email'] = request.form['email']
            return redirect(url_for('dashboard'))
        else:
            return 'username exists'

    return render_template('register.html')    
        

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        username  = db.orgdata.find({'email': session['email']})
        return render_template('dashboard.html', data = username)
    else:
        return redirect(url_for('index'))


@app.route('/syllabus')
def syllabus():
    if 'email' in session:
        return render_template('syllabus.html')
    else:
        return redirect(url_for('index'))       

@app.route('/syllabusdata', methods =["GET", "POST"])
def syllabusdata():
    db.syllabusdata.insert_one({'email' : session['email'],'syllabus' : request.form['syllabustext'], 'option' : request.form['option']})
    return 'syllbus uploaded successfully'

@app.route('/addedsyllabus')
def addedsyllabus():
    data  = db.syllabusdata.find({'email': session['email']})
    return render_template('addedsyllabus.html', data = data)


if __name__ == '__main__':
    app.debug = True
    app.run()
