import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('postgres://ctcpxqjzdukioy:56a59ab6ea742f8153fbba5c2e3be76dd4b983e3ad646827c45d0c59ecbb9ac0@ec2-18-233-137-77.compute-1.amazonaws.com:5432/d8o06hdpji4t0p')
db = scoped_session(sessionmaker(bind=engine))

books = db.execute("SELECT * FROM books").fetchall()

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"{isbn} {title} {author} {year}")
    db.commit()


if __name__ == "__main__":
    main()

