import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = "~\x8e\xb0\x08=\x03\xb0/Y*U\x98\x18\x90\xd6\xe2N\x84f%\xb1\xb7\xf8\xdb"

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 #10MB max upload
app.config['DATABASE'] = "db.sqlite"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 #TODO: remove later. This doesn't let browser cache files

import db
db.init_app(app)

#later remake it into angular/or and make it all different views

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def face():
 return render_template('index.html')

@app.route('/teacher') #this page is for creating a teacher profile before answering a question
def teacher():
 return render_template('teacher.html')


import re
email_pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

@app.route('/login-teacher', methods=['POST']) #TODO: join login for student and teacher. Just make different if statements. Add column to db.users
def login_teacher():
  if request.method == 'POST':
    print(request.form)
    email = request.form.get('user_name')
    match = email_pattern.match(email);
    if not match:
      pass
    session['name'] = request.form.get('user_name')
    session['email'] = request.form.get('user_email')
    return redirect(url_for('feed'))
 

@app.route('/login-student', methods=['POST'])
def login_student():
  if request.method == 'POST':
    data = request.get_json(silent=True);

    # we get email, pswd, name, school
    cur = db.get_db().cursor();
    cur.execute("SELECT * FROM users WHERE email = \"" + data['email'] + "\"") # possible injection here ( " ; ...")
    res = cur.fetchall();
    if res:
      print("This email seems to exist already")
    else:
      print("New user creation")
      cur.execute("""INSERT INTO users (name, surname, email, password, school)
        VALUES (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")""".format(data['name'], "Weird Last Name", data['email'], data['password'], data['school']))
      db.get_db().commit()
      # TODO: fix last name inquiry

    session['name'] = data['name']
    session['email'] = data['email']
    session['school'] = data['school']

    return redirect(url_for('question'))

@app.route('/ask', methods=['POST'])
def ask():
  if request.method == 'POST':
    file = request.files['q_image']
    if file.filename == '':
      flash('No selected file', request.url)
      return redirect(request.url)

    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      return "Upload successful"
    return "How did you get here?"

   #a = (request.form.get('q_topic'), request.form.get('q_desc'), request.form.get('q_image'))

@app.route('/student') #this page is for creating a student profile before asking a question
def student():
 return render_template('student.html')

@app.route('/question') #this page is for asking a question (+ the ML part)
def question():  #TODO: make the forms and actually think about what to ask. Add redirect to the materials
 return render_template('question.html', name=session['name'])

@app.route('/feed') #this page is for answering quesitions. TODO: add database part and click redirect to videocall
def feed():
 #session['isTeacher'] add it later so that you know whether it's a student of a teacher
 #get questions from DB
 questions = ({'id': 'question 1'}, {'id': "question 2"}, {'id': "question 2"})
 return render_template('feed.html', name=session['name'], email=session['email'], questions=questions)

@app.route('/materials') #this page is for recomending materials (should work on this one a lot)
def materials():
 return render_template('materials.html')

@app.route('/videocall') # actually the call part. Later make it into a separate view and just AJAX it in
def videocall():
 return render_template('videocall.html')