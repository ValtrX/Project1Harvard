import os #Importa library de Operation Systems
import requests #something about the API

from flask import Flask, render_template, session, request, flash, logging, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bcrypt import Bcrypt


#FLASK Bcrypt code 
app = Flask(__name__)
bcrypt = Bcrypt()
app.secret_key = 'this-is-a-very-secret-key'

#API request 1st code 
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "oa9BAej7RbvIY4luSUz8A", "isbns": "9781632168146"})
print(res.json())


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://ctcpxqjzdukioy:56a59ab6ea742f8153fbba5c2e3be76dd4b983e3ad646827c45d0c59ecbb9ac0@ec2-18-233-137-77.compute-1.amazonaws.com:5432/d8o06hdpji4t0p") # (SQL ALCHEMY) Set Environment Variable y recuerda todo pegado y sin comillas
db = scoped_session(sessionmaker(bind=engine)) # (SQL ALCHEMY) Creas diferentes sesiones para diferentes personas es decir si persona A ingresa a la pagina tendra una sesion diferente a Persona B con respecto a los cambios que se hagan en la base de datos, Ademas de que es el codigo que nos per

books = db.execute("SELECT * FROM books LIMIT 100").fetchall() # Call books for index

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method =="GET":
        booksearchrequest = request.args.get('search') #Book search request
        booksearch = "%{}%".format(booksearchrequest) #Book search result formating 

        #Book search result Query
        booksearchdata = db.execute("SELECT * FROM books WHERE (author LIKE :booksearch) OR (title LIKE :booksearch) OR (isbn LIKE :booksearch)",{"booksearch":booksearch}).fetchall()
        

    return render_template("index.html", books=books, booksearchdata=booksearchdata)

@app.route("/book/<int:book_id>") #Book details page
def book(book_id):
    url = request.referrer
    print(url)
    book = db.execute("SELECT * FROM books WHERE book_id=:id",{"id":book_id}).fetchone()
    return render_template("book.html", books=books, book=book, url=url)
    


@app.route("/register", methods=["GET", "POST"]) #Register Page
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
            return redirect(url_for('login'))

        else:
            flash("Password does not match","danger")
            return redirect(url_for('register'))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"]) #Login page
def login():

    if request.method =="POST":
        username = request.form.get("username")
        password = request.form.get("password")

        usernamedata = db.execute("SELECT username FROM users WHERE username=:username",{"username":username}).fetchone()
        passworddata = db.execute("SELECT password FROM users WHERE username=:username",{"username":username}).fetchone()

        # Formatting password & Username
        f_pass = ''.join(passworddata) #Formated password
        print(f_pass)

        pw_hash = bcrypt.generate_password_hash(f_pass).decode('utf-8') #Passowrd Hashing
        passcrypt = bcrypt.check_password_hash(f_pass, password)

        if usernamedata is None: #If There's no user
            flash("No username","danger")
            return redirect(url_for('login'))

        else: 
            for password_data in passworddata: #Search for a user and then compare the passwords
                if passcrypt:
                    session["logged_in"] = True
                    session['username'] = username
                    
                    flash("You are logged in!","success")
                    return redirect(url_for('index'))

                else:
                    flash("Password does not match","danger") #If the password does not match say "Password does not match"
                    return redirect(url_for('login'))

    return render_template("login.html")


@app.route("/logout") #Logout function
def logout():
    session.clear()
    flash("Bye! You are logged out now","danger")
    return redirect(url_for('login'))




if __name__ =="__main__":
    app.run(debug=True)
