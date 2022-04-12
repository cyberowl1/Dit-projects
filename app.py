from flask import Flask, render_template,request,session
from flask_session import Session
import bcrypt
from cs50 import SQL

app=Flask("__name__")
db=SQL("sqlite:///ditproject.db")
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)
# app.config['BCRYPT_LOG_ROUNDS'] = 6
# app.config['BCRYPT_HASH_IDENT'] = '2b'
# app.config['BCRYPT_HANDLE_LONG_PASSWORDS'] = True
# bcrypt = Bcrypt(app)


@app.route('/')
def index():

    return render_template("index.html")

@app.route('/projects')
def projects():
    rows=db.execute("select * from project")
    return render_template("projects.html", rows=rows)



@app.route('/Register', methods=["POST"])
def register():
   if request.method == "POST":
      if not request.form.get('sap') or not request.form.get('pswrd') or not request.form.get('email'):
         return render_template("error.html",msg="missing something")
   sap = request.form.get('sap')
   name = request.form.get('name')
   email = request.form.get('email')
   pswrd = request.form.get('pswrd')
   h = bcrypt.hashpw(pswrd.encode("utf-8"), bcrypt.gensalt(12))
   db.execute("INSERT INTO user (sapid,name,pswrd,email) VALUES(?,?,?,?)",sap,name,h,email)
   return render_template("index.html",sap=sap,email=email)

@app.route('/login',methods=["POST","GET"])
def login():
   if request.method == "POST":
      if not request.form.get('sap') or not request.form.get('pswrd'):
         return render_template("error.html",msg="missing username or pswrd")
      username = request.form.get('sap')
      pswrd = request.form.get('pswrd')
      # h= bcrypt.hashpw(pswrd.encode("utf-8"),bcrypt.gensalt())
      rows=db.execute(("select * from user where sapid=?"),username)
      if not rows:
          return render_template("index.html",msg=True)
      else:
         p=rows[0]['pswrd']
         if bcrypt.checkpw(pswrd.encode("utf-8"),p):
            session["sap"]=request.form.get("sap")
            session["pswrd"]=request.form.get("pswrd")
            session["name"]=rows[0]['name']
            session["loggedin"]=True
            return render_template("index.html")



   return render_template("index.html")



@app.route('/logout')
def logout():
   session["sap"]=None
   session["pswrd"]=None
   session["loggedin"]=None

   return render_template("index.html")

@app.route('/submitp',methods=["POST","GET"])
def submitp():
   if request.method == "POST":
      if not request.form.get('pname') or not request.form.get('ptech'):
         return render_template("error.html",msg="missing project details fill all fields")
      pname = request.form.get('pname')
      ptech = request.form.get('ptech')
      pdesc = request.form.get('pdesc')
      pbranch = request.form.get('pbranch')
      pgithub = request.form.get('githuburl')
      sapid = session["sap"]
      db.execute("INSERT INTO project (pname,tech,desc,sapid,branch,github) VALUES (?,?,?,?,?,?)",pname,ptech,pdesc,sapid,pbranch,pgithub)
      return render_template("sprojects.html", done=True, pname=pname)
   return render_template("sprojects.html")

@app.route("/dashboard")
def dashboard():
   sap=session["sap"]
   projects=db.execute(("select * from project where sapid=?"),sap)
   return render_template("dashboard.html",projects=projects)