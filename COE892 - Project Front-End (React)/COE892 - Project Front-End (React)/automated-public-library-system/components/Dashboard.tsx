import { useState, useEffect } from 'react';
import './Dashboard.css';
import { useNavigate } from 'react-router-dom';
import React from 'react';

const DEFAULT_BOOK_IMAGE = 'https://comicfever.ca/cdn/shop/products/202307-0000426174.jpg?v=1698170103';

interface Book {
  _id: string;
  name: string;
  author: string;
  genre: string;
  description: string;
  cover_filename?: string;
  borrowingDate?: string;
  dueDate?: string;
  image?: string;
}

interface BorrowedBook extends Book {
  borrowingDate: string;
  dueDate: string;
}

interface Recommendation {
  name: string;
  author: string;
  genre: string;
  similarity?: number;
  reason?: string;
}

const formatDate = (dateString: string | undefined) => {
  if (!dateString || dateString === "N/A") return "N/A";
  
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return dateString;
    }
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } catch {
    return dateString || "N/A";
  }
};

const Dashboard = () => {
  const [selectedTab, setSelectedTab] = useState<'borrowing' | 'renewal'>('borrowing');
  const [borrowedBooks, setBorrowedBooks] = useState<BorrowedBook[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSignOut = () => {
    // Clear both localStorage and sessionStorage
    localStorage.clear();
    sessionStorage.clear();
    // Redirect to home page
    navigate('/');
  };

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const username = localStorage.getItem('username') || sessionStorage.getItem('username');
        
        if (!username) {
          navigate('/');
          return;
        }

        // Fetch user data
        const userResponse = await fetch(`http://localhost:5000/get-user/${username}`);
        
        if (!userResponse.ok) {
          throw new Error(`Failed with status ${userResponse.status}`);
        }

        const userData = await userResponse.json();
        
        if (userData.error) {
          throw new Error(userData.error);
        }

        const processedBooks = (userData.borrowed_books || []).map((book: any) => ({
          ...book,
          cover_filename: book.cover_filename || "",  // Add this line
          borrowingDate: book.borrowingDate || book.borrowing_date || "N/A",
          dueDate: book.dueDate || book.due_date || "N/A"
        }));

        setBorrowedBooks(processedBooks);

        // Fetch recommendations
        const recResponse = await fetch(`http://localhost:5000/recommendations/${username}`);
        if (!recResponse.ok) {
          console.log('No recommendations found, using empty array');
          setRecommendations([]);
        } else {
          const recData = await recResponse.json();
          setRecommendations(recData);
        }

        setLoading(false);
        
      } catch (err) {
        console.error('Fetch error:', err);
        setError(err instanceof Error ? err.message : 'Failed to load user data');
        setLoading(false);
      }
    };

    fetchUserData();
  }, [navigate]);

  const handleSearchClick = () => {
    navigate('/search');
  };

  const getUpcomingDueDates = () => {
    const today = new Date();
    return borrowedBooks
      .map(book => {
        const dueDate = new Date(book.dueDate);
        const diffTime = dueDate.getTime() - today.getTime();
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return { 
          title: book.name, 
          dueIn: diffDays,
          dueDate: formatDate(book.dueDate)
        };
      })
      .filter(book => book.dueIn >= 0 && book.dueIn <= 7)
      .sort((a, b) => a.dueIn - b.dueIn);
  };

  if (loading) return <div className="dashboard-container">Loading dashboard...</div>;
  if (error) return <div className="dashboard-container">Error: {error}</div>;

  const upcomingDueDates = getUpcomingDueDates();

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>User Dashboard</h1>
        <div className="dashboard-actions">
          <button 
            onClick={handleSearchClick}
            className="search-button"
          >
            Search Books
          </button>
          <button 
            onClick={handleSignOut}
            className="signout-button"
          >
            Sign Out
          </button>
        </div>
      </div>
      <h2>Welcome {localStorage.getItem('username') || sessionStorage.getItem('username')}!</h2>
      
      <div className="dashboard-layout">
        <aside className="recommendations">
          <h3>Recommended Books</h3>
          <ul>
            {recommendations.length > 0 ? (
              recommendations.map((book, index) => (
                <li key={index}>
                  <strong>{book.name}</strong><br/>
                  by {book.author}<br/>
                  Genre: {book.genre}<br/>
                  {book.similarity && (
                    <span>Match: {(book.similarity * 100).toFixed(0)}%</span>
                  )}
                  {book.reason && (
                    <span>({book.reason})</span>
                  )}
                </li>
              ))
            ) : (
              <li>No recommendations available</li>
            )}
          </ul>
        </aside>

        <main className="book-list">
          <table>
            <thead>
              <tr>
                <th>Borrowed Books</th>
                <th>Cover</th>
                <th>
                  <button 
                    onClick={() => setSelectedTab('borrowing')}
                    className={selectedTab === 'borrowing' ? 'active' : ''}
                  >
                    Borrowing Dates
                  </button>
                  <button 
                    onClick={() => setSelectedTab('renewal')}
                    className={selectedTab === 'renewal' ? 'active' : ''}
                  >
                    Due Dates
                  </button>
                </th>
              </tr>
            </thead>
            <tbody>
              {borrowedBooks.length > 0 ? (
                borrowedBooks.map((book) => (
                  <tr key={book._id}>
                    <td>
                      {book.name}<br/>
                      by {book.author}<br/>
                      Genre: {book.genre}<br/>
                    </td>
                    <td>
                    <img 
                      src={book.cover_filename 
                            ? `/images/book_covers/${book.cover_filename}`
                            : DEFAULT_BOOK_IMAGE} 
                      alt={`Cover of ${book.name}`}
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.src = DEFAULT_BOOK_IMAGE;
                      }}
                      width="150" 
                      height="150" 
                      style={{ 
                        objectFit: 'cover',
                        display: 'block',
                        backgroundColor: '#f0f0f0'
                      }}
                    />
                    </td>
                    <td>
                      {selectedTab === 'borrowing' 
                        ? `Borrowed on: ${formatDate(book.borrowingDate)}` 
                        : `Due by: ${formatDate(book.dueDate)}`}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={3}>No books currently borrowed</td>
                </tr>
              )}
            </tbody>
          </table>
        </main>
        
        <aside className="due-dates">
          <h3>Upcoming Due Dates</h3>
          <ul className="timestamp">
            {upcomingDueDates.length > 0 ? (
              upcomingDueDates.map((book, index) => (
                <li key={index}>
                  {book.title} - Due in {book.dueIn} {book.dueIn === 1 ? 'day' : 'days'}
                  <br/>({book.dueDate})
                </li>
              ))
            ) : (
              <li>No books due in the next 7 days</li>
            )}
          </ul>
        </aside>
      </div>
    </div>
  );
};

export default Dashboard;