import os #Importa library de Operation Systems

from flask import Flask, render_template, session, request, flash, logging
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bcrypt import Bcrypt


app = Flask(__name__)
bcrypt = Bcrypt(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://ctcpxqjzdukioy:56a59ab6ea742f8153fbba5c2e3be76dd4b983e3ad646827c45d0c59ecbb9ac0@ec2-18-233-137-77.compute-1.amazonaws.com:5432/d8o06hdpji4t0p") # (SQL ALCHEMY) Set Environment Variable y recuerda todo pegado y sin comillas
db = scoped_session(sessionmaker(bind=engine)) # (SQL ALCHEMY) Creas diferentes sesiones para diferentes personas es decir si persona A ingresa a la pagina tendra una sesion diferente a Persona B con respecto a los cambios que se hagan en la base de datos, Ademas de que es el codigo que nos per

books = db.execute("SELECT * FROM books LIMIT 100").fetchall() # Call books for index

@app.route("/")
def index():
    return render_template("index.html", books=books)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method =="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm") # Field where you confirm the password
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        

        if password == confirm:

            db.execute("INSERT INTO users(username, password) VALUES(:username, :password)",
            {"username":username,"password":pw_hash})
            db.commit()
            flash("Now you are registered, try to log in!","success")
            return render_template("login.html")

        else:
            flash("Password does not match","danger")
            return render_template("register.html")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method =="POST":
        username = request.form.get("username")
        password = request.form.get("password")

        usernamedata = db.execute("SELECT username FROM users WHERE username=:username",{"username":username}).fetchone()
        passworddata = db.execute("SELECT password FROM users WHERE username=:username",{"username":username}).fetchone()
        pw_hash = bcrypt.generate_password_hash(passworddata).decode('utf-8')

        print(passworddata)
        print(pw_hash)

        if usernamedata is None:
            flash("No username","danger")
            return render_template("login.html")

        else: 
            for password_data in passworddata:
                if bcrypt.check_password_hash(pw_hash, passworddata):
                    flash("You are logged in!","success")
                    return render_template("index.html", books=books)

                else:
                    flash("Password does not match","danger")
                    return render_template("login.html")
        
    

    return render_template("login.html")
                
        



if __name__ =="__main__":
    app.run(debug=True)
    
