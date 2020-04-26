import os #Importa library de Operation Systems
import requests #something about the API

from flask import Flask, render_template, session, request, flash, logging, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bcrypt import Bcrypt

#FLASK Bcrypt code 

app = Flask(__name__)
bcrypt = Bcrypt()
app.secret_key = 'this-is-a-very-secret-key'

# Just Being Curious | How to get the reviews_widget
# res = requests.get("https://www.goodreads.com/book/isbn/0590353403?key=P1SeBqMxamC66BsKtE5BOg?format=json", params={"format": "json", "user_id": "113261926", "isbn": "1857231082"})
# print(res.json()) 


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
# engine = create_engine("postgres://ctcpxqjzdukioy:56a59ab6ea742f8153fbba5c2e3be76dd4b983e3ad646827c45d0c59ecbb9ac0@ec2-18-233-137-77.compute-1.amazonaws.com:5432/d8o06hdpji4t0p") # (SQL ALCHEMY) Set Environment Variable y recuerda todo pegado y sin comillas
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine)) # (SQL ALCHEMY) Creas diferentes sesiones para diferentes personas es decir si persona A ingresa a la pagina tendra una sesion diferente a Persona B con respecto a los cambios que se hagan en la base de datos, Ademas de que es el codigo que nos per

# Get recent books for index

books = db.execute("SELECT * FROM books ORDER BY year DESC").fetchall() 

# Index Page

@app.route("/", methods=["GET", "POST"]) 
def index(): 
    if request.method =="GET":
        
        # Getting data from input 
        booksearchrequest = request.args.get('search') # Get text from the search input 
        booksearch = "%{}%".format(booksearchrequest) # Formating input get  

            # Queries
        booksearchdata = db.execute("SELECT * FROM books WHERE (author ILIKE :booksearch) OR (title ILIKE :booksearch) OR (isbn ILIKE :booksearch)",{"booksearch":booksearch}).fetchall() # Book search result Query
        breviews = db.execute("SELECT books.book_id, reviews.content, reviews.rating, books.title, users.username FROM reviews JOIN books ON reviews.book_id = books.book_id JOIN users ON reviews.user_id = users.user_id ORDER BY books.book_id DESC").fetchall() # Get recent comments
            
            # Check if the result of the search is empty
        bcheck = booksearchdata == [] and booksearchrequest is not None 
    
    return render_template("index.html", bcheck=bcheck, books=books, breviews=breviews, booksearchdata=booksearchdata, booksearchrequest=booksearchrequest)

@app.route("/book/<int:book_id>", methods=["GET","POST"]) #Book details page
def book(book_id):
    # Go back last URL

    url = request.referrer 

    # Queries    
    book = db.execute("SELECT * FROM books WHERE book_id=:id",{"id":book_id}).fetchone() #SQL command to get the book ID
    book_isbn = db.execute("SELECT isbn FROM books WHERE book_id=:id",{"id":book_id}).fetchone() #SQL command to get isbn number
    book_reviews = db.execute("SELECT username, content, rating FROM users JOIN reviews ON reviews.user_id = users.user_id JOIN books ON reviews.book_id = books.book_id WHERE books.book_id=:id",{"id":book_id}).fetchall() #SQL command to get Review by Book ID
    
    # Formated isbn
    f_isbn = ''.join(book_isbn) 

    # API request by isbn
    isbn_res = requests.get("https://www.goodreads.com/book/review_counts.json", 
    params={"key": "P1SeBqMxamC66BsKtE5BOg", "isbns": "{}".format(f_isbn)}) # API code to get ISBN number from book_isbn variable

    isbn_json = isbn_res.json() #Converting the Request to JSON

    isbn_data = isbn_json['books'] # Returning the 'books' dictionary

    for item in isbn_data: #Getting values from the dictionary 

        book_api_isbn = item['isbn']
        book_api_total = item['work_ratings_count']
        book_api_avg = item['average_rating']

    if session.get('logged_in') == True:
        # Getting username from the session
        logged_in_user = session['username'] 

        user_id = db.execute("SELECT user_id FROM users WHERE username=:name",{"name":logged_in_user}).fetchone() # Get user_id from username of logged_in_user

        for name in user_id: #Getting values from user_id as they are 'int' instead 'str'
            f_user_id = name
        if request.method =="POST":

            # Getting data from inputs
            rating = request.form.get("rating")
            content = request.form.get("content")

            # Queries 
            user_reviewed_before = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id",  {"user_id":f_user_id, "book_id": book_id}).fetchone()

            # Check if the user has commented before
            if user_reviewed_before:
                flash("You've already submit a review","danger")

            # Insert review into the database if the content input is not empty
            elif content is not None:

                # Query to insert review
                db.execute("INSERT INTO reviews(book_id, user_id, content, rating) VALUES(:book_id, :user_id, :content, :rating)",
                {"book_id":book_id, "user_id":f_user_id, "content":content, "rating":rating})
                db.commit()

            return redirect(url_for('book', book_id=book_id))
    else: 
        flash("You must be logged in to make a review","danger")
     
    return render_template("book.html", books=books, book=book, url=url, book_api_total=book_api_total, book_api_avg=book_api_avg, book_reviews=book_reviews)
    
    
@app.route("/register", methods=["GET", "POST"]) #Register Page
def register():
    if request.method =="POST":
        # Getting data form inputs
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm") # Field where you confirm the password

        # Code to hash the password using bcrypt
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8') 
        
        # Checking if passwords match
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

        # Getting data form inputs
        username = request.form.get("username")
        password = request.form.get("password")

        #Queries
        usernamedata = db.execute("SELECT username FROM users WHERE username=:username",{"username":username}).fetchone()
        passworddata = db.execute("SELECT password FROM users WHERE username=:username",{"username":username}).fetchone()

        # Formatting password & Username
        f_pass = ''.join(passworddata) #Formated password

        pw_hash = bcrypt.generate_password_hash(f_pass).decode('utf-8') #Passowrd Hashing
        passcrypt = bcrypt.check_password_hash(f_pass, password) # Checking hashed password

        # Check If There's no user
        if usernamedata is None:
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



@app.route("/api/<string:isbn>")
def book_api(isbn):
      """Return details about a single book."""

      # Make sure if book exists.
      book = db.execute("SELECT * FROM books where isbn=:isbn",{"isbn":isbn}).fetchone()

      # Check if there's a book
      if book is None:
          return jsonify({"error": "Invalid isbn"}), 404
      
      # Get goodreads API data
      goodreads = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "P1SeBqMxamC66BsKtE5BOg", "isbns": isbn})
      goodreads_book = goodreads.json()["books"][0]

      return jsonify({
                "title": book.title,
                "author": book.author,
                "year": book.year,
                "isbn": book.isbn,
                "review_count": goodreads_book["work_reviews_count"],
                "average_score": goodreads_book["average_rating"]
            })

if __name__ =="__main__":
    app.run(debug=True)