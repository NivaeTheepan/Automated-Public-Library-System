import os
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


def initialize():
    load_dotenv(find_dotenv())
    username = os.environ.get("MONGO_USERNAME")
    password = os.environ.get("MONGO_PWD")

    connection_string = f"mongodb+srv://{username}:{password}@automatedlibrarysystema.hfspm.mongodb.net/"
    client = MongoClient(connection_string)
    users = client.LibraryDB.users
    books = client.LibraryDB.inventory
    borrowed_books = client.LibraryDB.borrowed_books

    return users, books, borrowed_books

def borrow_book(users, books, borrowed_books, user_name, book_name, days=14):
    user = users.find_one({"username": user_name})
    book = books.find_one({"name": book_name})
    borrowed = borrowed_books.find_one({"book_name": book_name})

    if not user:
        return "User not found"
    if not book:
        return "Book not found"
    if borrowed:
        return "Book is already borrowed"

    borrowing_date = datetime.now()
    due_date = borrowing_date + timedelta(days=days)
    
    borrow_doc = {
        "userID": user_name,
        "book_name": book_name,
        "borrowing_date": borrowing_date.isoformat(),
        "due_date": due_date.isoformat()
    }
    borrowed_books.insert_one(borrow_doc)

    users.update_one(
        {"username": user_name},
        {"$push": {"borrowed_books": {
            "book_name": book_name,
            "borrowing_date": borrowing_date.isoformat(),
            "due_date": due_date.isoformat()
        }}}
    )

    if user and book_name not in user.get("past_books", []):
        users.update_one(
            {"username": user_name},
            {"$push": {"past_books": book_name}}
        )

    return f"Book {book_name} borrowed successfully, due by {due_date.strftime('%Y-%m-%d')}"

def return_book(users, books, borrowed_books, user_name, book_name):
    user = users.find_one({"username": user_name})
    book = books.find_one({"name": book_name})
    borrowed = borrowed_books.find_one({"book_name": book_name})

    if not user:
        return "User not found"
    if not book:
        return "Book not found"
    if borrowed.get("userID") != user_name:
        return "Book was not borrowed by this user"

    borrowed_books.delete_one({"book_name": book_name})

    users.update_one(
        {"username": user_name},
        {"$pull": {"borrowed_books": {"book_name": book_name}}}
    )

    return f"Book {book_name} returned successfully"

def get_recommendations(username, users, books, num_recommendations=5):
    try:
        user = users.find_one({"username": username}, {"past_books": 1})
        if not user or not user.get("past_books"):
            print(f"No history found for user '{username}'")
            return get_popular_fallback(books, num_recommendations)
        
        past_books = user["past_books"]
        
        all_books = list(books.find(
            {},
            {"_id": 1, "name": 1, "description": 1, "author": 1, "genre": 1}
        ))
        
        if not all_books:
            print("No books found in inventory")
            return []
        
        valid_past_books = []
        inventory_names = {b["name"] for b in all_books}
        
        for book_name in past_books:
            if book_name in inventory_names:
                valid_past_books.append(book_name)
            else:
                print(f"Warning: Past book '{book_name}' not found in inventory")
        
        if not valid_past_books:
            return get_popular_fallback(books, num_recommendations)
        
        book_features = []
        book_data = []
        
        for book in all_books:
            features = (
                f"{book.get('name', '')} "
                f"{book.get('author', '')} "
                f"{book.get('genre', '')} "
                f"{book.get('description', '')}"
            )
            features = re.sub(r'[^\w\s]', '', features).lower()
            book_features.append(features)
            book_data.append(book)
        
        tfidf = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1
        )
        tfidf_matrix = tfidf.fit_transform(book_features)
        
        past_indices = [
            i for i, book in enumerate(all_books) 
            if book["name"] in valid_past_books
        ]
        
        if not past_indices:
            return get_popular_fallback(books, num_recommendations)
        
        avg_similarity = [0.0] * len(all_books)
        
        for idx in past_indices:
            similarities = cosine_similarity(tfidf_matrix[idx:idx+1], tfidf_matrix)[0]
            for i in range(len(all_books)):
                avg_similarity[i] += similarities[i]
        
        for i in range(len(avg_similarity)):
            avg_similarity[i] /= len(past_indices)
        
        recommendations = []
        seen_books = set(valid_past_books)
        
        for i in sorted(
            range(len(all_books)), 
            key=lambda x: -avg_similarity[x]
        ):
            book = all_books[i]
            if book["name"] not in seen_books:
                recommendations.append({
                    "name": book["name"],
                    "author": book["author"],
                    "genre": book.get("genre", "Unknown"),
                    "similarity": avg_similarity[i]
                })
                seen_books.add(book["name"])
                if len(recommendations) >= num_recommendations:
                    break
        
        return recommendations

    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        return []

def get_popular_fallback(books, n):
    """Fallback to popular books when no useful history exists"""
    popular = list(books.find().sort("average_rating", -1).limit(n))
    return [{
        "name": b["name"],
        "author": b["author"],
        "genre": b.get("genre", "Unknown"),
        "reason": "Popular"
    } for b in popular]


if __name__ == "__main__":
    users_collection, books_collection, borrowed_books_collection = initialize()

    # Example usage
    print(borrow_book(users_collection, books_collection, borrowed_books_collection, "user1", "book123"))
    print(return_book(users_collection, books_collection, borrowed_books_collection, "user1", "book123"))