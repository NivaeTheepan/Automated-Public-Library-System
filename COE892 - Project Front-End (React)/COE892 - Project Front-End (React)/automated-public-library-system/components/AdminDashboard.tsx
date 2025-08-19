import React, { useState } from "react";
import "./AdminDashboard.css";
import { FaArrowLeft, FaSignOutAlt } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

interface Book {
  title: string;
  renewalDate: string;
}

interface User {
  fullName: string;
  libraryID: string;
  phoneNumber: string;
  username: string;
  password: string;
  borrowedBooks: Book[];
}

const users: User[] = [
  {
    fullName: "Jugadbeer Sangha",
    libraryID: "501098645",
    phoneNumber: "678-999-8212",
    username: "j5sangha",
    password: "testpassword1!",
    borrowedBooks: [
      { title: "Yotsuba&! Vol. 1", renewalDate: "21-04-2025" },
      { title: "Look Back", renewalDate: "19-04-2025" },
    ],
  },
  {
    fullName: "Nivaethan Piratheepan",
    libraryID: "501099180",
    phoneNumber: "718-808-8342",
    username: "n7piratheepan",
    password: "testpassword2@",
    borrowedBooks: [
      { title: "Spider-Man Vol. 1", renewalDate: "17-04-2025" },
    ],
  },
  {
    fullName: "Lalith Ravichandran",
    libraryID: "501086076",
    phoneNumber: "407-224-1783",
    username: "l2ravichandran",
    password: "testpassword3#",
    borrowedBooks: [
      { title: "Invincible Vol. 12", renewalDate: "01-04-2025" },
    ],
  },
  {
    fullName: "Simrat Gill",
    libraryID: "501100893",
    phoneNumber: "609-582-4912",
    username: "s9gill",
    password: "testpassword4$",
    borrowedBooks: [
      { title: "Slam Dunk Vol. 12", renewalDate: "05-04-2025" },
    ],
  },
];

const AdminDashboard: React.FC = () => {
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const navigate = useNavigate();

  const handleBackToHome = () => {
    navigate('/');
  };

  const handleSignOut = () => {
    // Clear both localStorage and sessionStorage
    localStorage.clear();
    sessionStorage.clear();
    // Redirect to home page
    navigate('/');
  };

  return (
    <div className="admin-dashboard">
      <div className="button-container">
        <button onClick={handleBackToHome} className="back-button">
          <FaArrowLeft /> Back to Home
        </button>
        <button onClick={handleSignOut} className="signout-button">
          <FaSignOutAlt /> Sign Out
        </button>
      </div>
      <h1>Admin Dashboard</h1>
      <div className="user-list">
        <h2>Select a User:</h2>
        <ul>
          {users.map((user, index) => (
            <li key={index} onClick={() => setSelectedUser(user)}>
              {user.fullName} ({user.libraryID})
            </li>
          ))}
        </ul>
      </div>

      {selectedUser && (
        <div className="user-details">
          <h2>User Details</h2>
          <p><strong>Full Name:</strong> {selectedUser.fullName}</p>
          <p><strong>Library ID:</strong> {selectedUser.libraryID}</p>
          <p><strong>Phone Number:</strong> {selectedUser.phoneNumber}</p>
          <p><strong>Username:</strong> {selectedUser.username}</p>
          <p><strong>Password:</strong> {selectedUser.password}</p>
          <h3>Borrowed Books</h3>
          {selectedUser.borrowedBooks.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Renewal Date</th>
                </tr>
              </thead>
              <tbody>
                {selectedUser.borrowedBooks.map((book, index) => (
                  <tr key={index}>
                    <td>{book.title}</td>
                    <td>{book.renewalDate}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No borrowed books.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;