# import json
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import Book_DB_CRUD
import User_DB_CRUD

from Book_DB_CRUD import initialize as init_db
from User_DB_CRUD import get_users, find_user, create_user

users_collection, books_collection, borrowed_books_collection = init_db()

# class User(BaseModel):
#     username: str
#     borrowed_books: List[dict] = []


# class Book(BaseModel):
#     book_id: str
#     title: str
#     author: str
#     borrowed_by: Optional[str] = None
#     due_date: Optional[str] = None


class BorrowRequest(BaseModel):
    username: str
    book_name: str


class ReturnRequest(BaseModel):
    username: str
    book_name: str

class LoginUser(BaseModel):
    username: str
    password: str

class RegisterUser(BaseModel):
    _id: str
    username: str
    password: str

app = FastAPI(debug=True)

origins = [
    "http://localhost:3000",  # React front-end location
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
)

memory_db = {"borrowed_books": []}
users_collection, books_collection, borrowed_books_collection = Book_DB_CRUD.initialize()

print("Users Collection:", users_collection)
print("Books Collection:", books_collection)
print("Borrowed Books Collection:", borrowed_books_collection)

@app.get("/get-users")
def get_users():
    users = list(users_collection.find({}, {"_id": 0}))  # Exclude MongoDB's ObjectId
    return {"users": users}

@app.get("/get-books")
def get_books():
    books = list(books_collection.find({}, {"_id": 0}))
    return {"books": books}

@app.get("/get-user/{username}")
def get_user(username: str):
    user = users_collection.find_one({"username": username}, {"_id": 0})
    if user:
        return user
    # return {"message": "User not found"}
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/get-book/{book_name}")
def get_book(book_name: str):
    book = books_collection.find_one({"name": book_name}, {"_id": 0})
    if book:
        return book
    # return {"message": "Book not found"}
    raise HTTPException(status_code=404, detail="Book not found")

@app.post("/return-book")
def return_book(request: ReturnRequest):
    result = Book_DB_CRUD.return_book(users_collection, books_collection, borrowed_books_collection, request.username, request.book_name)
    return {"message": result}

@app.post("/borrow-book")
def borrow_book(request: BorrowRequest):
    result = Book_DB_CRUD.borrow_book(users_collection, books_collection, borrowed_books_collection, request.username, request.book_name)
    return {"message": result}

@app.get("/recommendations/{username}")
def get_recommendations(username: str):
    # user = users_collection.find_one({"username": username}, {"_id": 0})
    # if user:
    #     return {"message": "User found"}
    # raise HTTPException(status_code=404, detail="User not found")
    try:
        user = get_user(username)
        user_recommendations = Book_DB_CRUD.get_recommendations(username, users_collection, books_collection)
        return user_recommendations
    except HTTPException as e:
        raise e

@app.post("/login-user")
def login(login_user: LoginUser):
    users = User_DB_CRUD.get_users(users_collection)
    user_exists = any(user['username'] == login_user.username for user in users)
    if user_exists:
        for user in users:
            if (user["username"] == login_user.username) and (user["password"] == login_user.password):
                return {"username": login_user.username,
                        "message": "Login successful"}
        # return {"message": "Login failed"}
        raise HTTPException(status_code=404, detail="Login Failed")
    else:
        # return {"message": "User not found"}
        raise HTTPException(status_code=404, detail="User not found")

@app.post("/create-user")
@app.post("/register-user")
def register(register_user: RegisterUser):
    new_user = User_DB_CRUD.create_user(users_collection, register_user.username, register_user.password)
    return {"message": "User created", "id": new_user, "username": register_user.username}

@app.get("/get-user/{username}")
async def get_user_books(username: str):
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/get-popular-books")
async def get_popular_books():
    popular_books = list(books_collection.find().sort("average_rating", -1).limit(5))
    return [{"name": b["name"], "author": b.get("author", "Unknown")} for b in popular_books]

@app.get("/recommendations/{username}")
async def get_user_recommendations(username: str):
    try:
        recommendations = Book_DB_CRUD.get_recommendations(
            username, 
            users_collection, 
            books_collection
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/get-books-with-status")
def get_books_with_status():
    books = list(books_collection.find({}, {"_id": 0}))
    borrowed_books = list(borrowed_books_collection.find({}, {"_id": 0, "book_name": 1, "userID": 1}))
    
    # Create a map of borrowed books
    borrowed_map = {b["book_name"]: b["userID"] for b in borrowed_books}
    
    # Mark books as borrowed if they're in the borrowed collection
    for book in books:
        if book["name"] in borrowed_map:
            book["borrowed"] = True
            book["borrowedBy"] = borrowed_map[book["name"]]
        else:
            book["borrowed"] = False
    
    return {"books": books}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)