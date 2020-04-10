import os #Importa library de Operation Systems

from flask import Flask, render_template, session, request, flash, logging
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = engine = create_engine(os.getenv("postgres://ctcpxqjzdukioy:56a59ab6ea742f8153fbba5c2e3be76dd4b983e3ad646827c45d0c59ecbb9ac0@ec2-18-233-137-77.compute-1.amazonaws.com:5432/d8o06hdpji4t0p"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    books = "hablaremos de libros y de jules"
    return render_template("index.html", books=books)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method =="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        confirm=request.form.get("confirm") # Field where you confirm the password

        if password == confirm:
            db.execute("INSERT INTO users(username, password) VALUES(:username, :password)",
            {"username":username,"password":password})
            db.commit()
            flash("Now you are registered, try to log in!","success")
            return render_template("login.html")
        else:
            flash("password does not match","danger")
            return render_template("register.html")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method =="POST":
        username = request.form.get("username")
        password = request.form.get("password")

        usernamedata = db.execute("SELECT username FROM users WHERE username=:username",{"username":username}).fetchone()
        passworddata = db.execute("SELECT password FROM users WHERE username=:username",{"username":username}).fetchone()

        if usernamedata is None:
            flash("No username","danger")
            return render_template("login.html")
            
        else:
            for password_data in passworddata:
                if bcrypt.check_password_hash(hashed, password):
                    flash("It matches!","danger")
                    return render_template("login.html")
                else:
                    flash("password does not match","danger")
                    return render_template("login.html")
        
    

    return render_template("login.html")
                
        



if __name__ =="__main__":
    app.run(debug=True)
    
