import { useState, useEffect } from "react";
import React from "react";
import "./SearchPage.css";
import {useNavigate} from "react-router-dom";
import { FaArrowLeft } from "react-icons/fa";

interface Book {
  _id: string;
  name: string;
  author: string;
  genre: string;
  description: string;
  rating?: number;
  cover_filename?: string;
  borrowed?: boolean;
}

const SearchPage: React.FC = () => {
  const [query, setQuery] = useState<string>("");
  const [selectedBooks, setSelectedBooks] = useState<string[]>([]);
  const [message, setMessage] = useState<string>("");
  const [books, setBooks] = useState<Book[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [currentUser, setCurrentUser] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const username = localStorage.getItem('username') || sessionStorage.getItem('username');
    if (username) {
      setCurrentUser(username);
    }

    const fetchBooks = async () => {
      try {
        const response = await fetch("http://localhost:5000/get-books-with-status");
        const data = await response.json();
        setBooks(data.books);
        setIsLoading(false);
      } catch (error) {
        console.error("Error fetching books:", error);
        setIsLoading(false);
      }
    };

    fetchBooks();
  }, []);

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  const filteredBooks = books.filter((book) => 
    book.name.toLowerCase().includes(query.toLowerCase()) ||
    book.author.toLowerCase().includes(query.toLowerCase()) ||
    book.genre.toLowerCase().includes(query.toLowerCase()) ||
    book.description.toLowerCase().includes(query.toLowerCase())
  );

  const toggleSelection = (bookId: string) => {
    const book = books.find(b => b._id === bookId);
    if (book?.borrowed) return;
    
    setSelectedBooks((prev: string[]) =>
      prev.includes(bookId) ? prev.filter((id) => id !== bookId) : [...prev, bookId]
    );
  };

  const handleCheckout = async () => {
    if (selectedBooks.length === 0 || !currentUser) {
      setMessage("Please select books and ensure you're logged in");
      return;
    }

    try {
      const response = await fetch("http://localhost:5000/borrow-books", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: currentUser,
          bookIds: selectedBooks,
        }),
      });

      const result = await response.json();

      if (response.ok) {
        navigate('/dashboard');
      } else {
        setMessage(result.message || "Error borrowing books");
      }
    } catch (error) {
      console.error("Error borrowing books:", error);
      setMessage("Error borrowing books");
    }
  };

  const renderRating = (rating: number | undefined) => {
    if (rating === undefined) return "No rating";
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    
    return (
      <div className="rating-display">
        {[...Array(5)].map((_, i) => {
          if (i < fullStars) {
            return <span key={i} className="star">★</span>;
          } else if (i === fullStars && hasHalfStar) {
            return <span key={i} className="star">½</span>;
          } else {
            return <span key={i} className="star">☆</span>;
          }
        })}
        <span className="rating-value">({rating.toFixed(1)})</span>
      </div>
    );
  };

  if (isLoading) {
    return <div className="search-container">Loading books...</div>;
  }

  return (
    <div className="search-container">
      <div className="button-container">
        <button onClick={handleBackToDashboard} className="back-button">
          <FaArrowLeft /> Back to Dashboard
        </button>
      </div>
      <h1>Search Books</h1>
      <input
        type="text"
        placeholder="Search by Title, Author, Genre, or Description..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="search-box"
      />
      <div className="book-list">
        {filteredBooks.length > 0 ? (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Image</th>
                  <th>Author</th>
                  <th>Genre</th>
                  <th>Rating</th>
                  <th>Description</th>
                  <th>Borrow</th>
                </tr>
              </thead>
              <tbody>
                {filteredBooks.map((book) => (
                  <tr key={book._id}>
                    <td>{book.name}</td>
                    <td>
                    <img
                      src={book.cover_filename 
                            ? `/images/book_covers/${book.cover_filename}`
                            : "../resources/default-book.jpg"}
                      alt={book.name}
                      width="120"
                      height="120"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.src = "../resources/default-book.jpg";
                      }}
                    />
                    </td>
                    <td>{book.author}</td>
                    <td>{book.genre}</td>
                    <td>{renderRating(book.rating)}</td>
                    <td className="description-cell">
                      <div className="description-content">{book.description}</div>
                    </td>
                    <td>
                      <input
                        type="checkbox"
                        disabled={book.borrowed}
                        checked={selectedBooks.includes(book._id)}
                        onChange={() => toggleSelection(book._id)}
                      />
                      {book.borrowed && <span className="borrowed-label">(Borrowed)</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="no-results">No matching books found</p>
        )}
      </div>
      <button onClick={handleCheckout}>Checkout</button>
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default SearchPage;