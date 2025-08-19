# Automated-Public-Library-System
An automated, cloud-enabled public library management system built with React, FastAPI, and MongoDB. This project enhances efficiency, scalability, and user experience by integrating secure authentication, digital inventory management, personalized recommendations, notifications, and an admin control panel.


<p align="left"> <b>📌 Project Overview</b> </p>
Traditional public libraries often face challenges with manual processes, limited accessibility, inconsistent inventory tracking, and a lack of personalized services. This project addresses those gaps by building a modern Automated Library System that:

- Streamlines cataloguing and borrowing
- Provides remote access to resources
- Offers personalized book recommendations
- Implements a notification system for users
- Improves scalability, performance, and user satisfaction



<p align="left"> <b>🚀 Features</b> </p>
👤 User Features

- Register/Login with secure JWT-based authentication
- Search & Borrow books from the digital catalogue
- View Dashboard with borrowing history and active reservations
- Receive Notifications for:
- Due dates
- New book arrivals
- Reservation availability
- Personalized Recommendations based on borrowing history and ratings

🛠️ Admin Features

- Admin Dashboard for library staff
- Manage books, users, and reservations
- View system analytics



<p align="left"> <b>⚙️ System Architecture</b> </p>

The system is structured around three main components:

1. Frontend (React)

  - Built with ReactJS for a responsive and user-friendly interface
  - Pages: Login, Registration, Search, Borrow, User Dashboard, Admin Panel
  - Styled with CSS for consistent UI across devices

2. Backend (FastAPI + MongoDB)

  - RESTful APIs to handle communication between frontend and database
  - MongoDB NoSQL Database stores user data, books, reservations, and borrowing history
  - API Endpoints (examples):
      - /login-user
      - /borrow-book
      - /recommend-books

3. Notification & Recommendation System

  - Notifications: Informs users about due dates, reservations, and new arrivals
  - Recommendation Engine: Suggests books using borrowing patterns, ratings, and preferences



<p align="left"> <b>🔐 Security Considerations</b> </p>

- JWT Authentication: Ensures only authorized users can access system features
- Data Encryption: Protects sensitive user information
- Access Control: Restricts admin-level features to authorized staff
