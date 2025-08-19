import os
from dotenv import find_dotenv, load_dotenv
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

load_dotenv(find_dotenv())
username = os.environ.get("MONGO_USERNAME")
password = os.environ.get("MONGO_PWD")
connection_string = f"mongodb+srv://{username}:{password}@automatedlibrarysystema.hfspm.mongodb.net/"
client = MongoClient(connection_string)
db = client["LibraryDB"]

# Access your collections
books_col = db["inventory"]
borrowed_col = db["borrowed_books"]
users_col = db["users"]
ratings_col = db["ratings"]

def get_user_history_recommendations(username, n_recommendations=5):
    try:
        
        user = users_col.find_one({"username": username}, {"past_books": 1})
        if not user or not user.get("past_books"):
            print(f"No history found for user '{username}'")
            return get_popular_fallback(n_recommendations)
        
        past_books = user["past_books"]
        
        all_books = list(books_col.find(
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
            return get_popular_fallback(n_recommendations)
        
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
            return get_popular_fallback(n_recommendations)
        
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
                if len(recommendations) >= n_recommendations:
                    break
        
        return recommendations

    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        return []

def get_popular_fallback(n):
    """Fallback to popular books when no useful history exists"""
    popular = list(books_col.find().sort("average_rating", -1).limit(n))
    return [{
        "name": b["name"],
        "author": b["author"],
        "genre": b.get("genre", "Unknown"),
        "reason": "Popular"
    } for b in popular]

if __name__ == "__main__":
    username = "user1"
    recommendations = get_user_history_recommendations(username, 5)
    
    if not recommendations:
        print("No recommendations could be generated")
    else:
        print(f"Recommended books based on {username}'s reading history:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['name']} by {rec['author']}")
            print(f"   Genre: {rec['genre']}")
            if 'similarity' in rec:
                print(f"   Similarity: {rec['similarity']:.2f}")
            else:
                print("   (Popular fallback recommendation)")
            print()