import json
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient
import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from Book_DB_CRUD import borrow_book
from Book_DB_CRUD import get_recommendations
import Book_DB_CRUD

app = Flask(__name__)
CORS(app)

def initialize():
    load_dotenv(find_dotenv())
    username = os.environ.get("MONGO_USERNAME")
    password = os.environ.get("MONGO_PWD")
    connection_string = f"mongodb+srv://{username}:{password}@automatedlibrarysystema.hfspm.mongodb.net/"
    client = MongoClient(connection_string)
    return client.LibraryDB  # Return the whole database now

def get_users(db):
    return list(db.users.find())

def find_user(db, user_name):
    # Check regular users first
    user = db.users.find_one({"username": user_name})
    if user:
        return user, False  # Return user and isAdmin flag
    
    # Check admin collection if not found in users
    admin = db.admins.find_one({"username": user_name})
    if admin:
        return admin, True  # Return admin and isAdmin flag
    
    return None, False

def create_user(db, user_name, pwd):
    doc = {
        "username": user_name,
        "password": pwd,
    }
    result = db.users.insert_one(doc).inserted_id
    return str(result)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    db = initialize()  # Get the database connection
    user, is_admin = find_user(db, username)
    
    if user and user['password'] == password:
        response_data = {
            'success': True,
            'message': 'Login successful',
            'username': username,
            'token': 'sample-auth-token',
            'isAdmin': is_admin  # Use the flag from find_user
        }
        return jsonify(response_data)
    else:
        return jsonify({
            'success': False, 
            'message': 'Invalid username or password'
        }), 401

@app.route('/get-user/<username>')
def get_user_endpoint(username):
    try:
        db = initialize()
        user, is_admin = find_user(db, username)
        
        if not user:
            return jsonify({"error": "User not found"}), 404

        processed_books = []
        if not is_admin and 'borrowed_books' in user:
            for book in user.get("borrowed_books", []):
                book_details = db.inventory.find_one(
                    {"name": book.get("book_name")},
                    {"_id": 1, "name": 1, "author": 1, "genre": 1, "cover_filename": 1}  # Add cover_filename
                ) or {}
                
                processed_books.append({
                    "_id": str(book_details.get("_id", "")),
                    "name": book.get("book_name") or book_details.get("name", "Unknown Book"),
                    "author": book.get("author") or book_details.get("author", "Unknown Author"),
                    "genre": book.get("genre") or book_details.get("genre", "Unknown"),
                    "cover_filename": book_details.get("cover_filename", ""),  # Add this line
                    "borrowingDate": book.get("borrowing_date", book.get("borrowingDate", "N/A")),
                    "dueDate": book.get("due_date", book.get("dueDate", "N/A"))
                })

        return jsonify({
            "username": user["username"],
            "isAdmin": is_admin,
            "borrowed_books": processed_books,
            "past_books": user.get("past_books", []) if not is_admin else []
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

        return jsonify({
            "username": user["username"],
            "isAdmin": is_admin,
            "borrowed_books": processed_books,
            "past_books": user.get("past_books", []) if not is_admin else []
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/get-books')
def get_books():
    try:
        db = initialize()
        books = list(db.inventory.find({}, {
            "_id": 1, 
            "name": 1, 
            "author": 1, 
            "genre": 1, 
            "description": 1, 
            "image": 1,
            "rating": 1  # Include rating field
        }))
        # Convert ObjectId to string
        for book in books:
            book["_id"] = str(book["_id"])
        return jsonify(books)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/borrow-books', methods=['POST'])
def borrow_books():
    try:
        data = request.get_json()
        username = data.get('username')
        book_ids = data.get('bookIds', [])
        
        db = initialize()
        users = db.users
        books = db.inventory
        borrowed_books = db.borrowed_books
        
        results = []
        
        for book_id in book_ids:
            # Convert string id back to ObjectId
            from bson import ObjectId
            book_oid = ObjectId(book_id)
            
            # Get book details
            book = books.find_one({"_id": book_oid})
            if not book:
                results.append(f"Book with ID {book_id} not found")
                continue
                
            # Borrow the book
            result = borrow_book(users, books, borrowed_books, username, book['name'])
            results.append(result)
            
        return jsonify({
            "success": True,
            "results": results,
            "message": "Books borrowed successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/recommendations/<username>')
def get_recommendations_endpoint(username):
    try:
        db = initialize()
        users = db.users
        books = db.inventory
        
        # Get recommendations using the existing function from Book_DB_CRUD
        recommendations = Book_DB_CRUD.get_recommendations(username, users, books)
        
        return jsonify(recommendations)
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/get-books-with-status')
def get_books_with_status():
    try:
        db = initialize()
        books = list(db.inventory.find({}, {
            "_id": 1,
            "name": 1,
            "author": 1,
            "genre": 1,
            "description": 1,
            "cover_filename": 1,
            "rating": 1,
            "borrowed": 1
        }))
        
        borrowed_books = list(db.borrowed_books.find({}, {"book_name": 1}))
        borrowed_names = {b["book_name"] for b in borrowed_books}
        
        for book in books:
            book["_id"] = str(book["_id"])
            book["borrowed"] = book["name"] in borrowed_names
        
        return jsonify({"books": books})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    db = initialize()
    get_users(db)
    app.run(port=5000)