# Real-time Leaderboard System

This project is a **real-time leaderboard system** built using **FastAPI**, **Redis**, and **SQLite**. It allows users to register, log in, submit scores for games, and view a real-time leaderboard. The system combines **Redis** for real-time leaderboard updates and **SQLite** for persistent score history.

---

## Features

1. **User Authentication**:
   - Users can register and log in to the system.
   - Passwords are securely hashed using **bcrypt**.

2. **Score Submission**:
   - Users can submit scores for different games.
   - Scores are validated to ensure they are between 0 and 9.

3. **Real-time Leaderboard**:
   - Scores are stored in **Redis sorted sets** for efficient real-time updates.
   - The leaderboard displays all scores from both **Redis** (real-time) and **SQLite** (persistent).

4. **Persistent Score History**:
   - Scores are also stored in **SQLite** for persistent storage.
   - The leaderboard combines data from both Redis and SQLite.

5. **Frontend**:
   - A simple HTML frontend is provided for user interaction.
   - **TailwindCSS** is used for styling.

---

## Technologies Used

- **Backend**:
  - **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python.
  - **Redis**: An in-memory data structure store used for real-time leaderboard updates.
  - **SQLite**: A lightweight, serverless database for persistent score storage.
  - **SQLAlchemy**: An ORM (Object-Relational Mapping) library for interacting with SQLite.

- **Frontend**:
  - **HTML**: For the user interface.
  - **TailwindCSS**: A utility-first CSS framework for styling.

- **Authentication**:
  - **JWT (JSON Web Tokens)**: For secure user authentication.
  - **bcrypt**: For password hashing.

---
## Setup Instructions

### Prerequisites

1. **Python 3.8+**: Install Python from [python.org](https://www.python.org/).
2. **Redis**: Install Redis from [redis.io](https://redis.io/).
3. **SQLite**: Comes pre-installed with Python.

---
### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/fsuarez16/realtime-leaderboard.git
   cd realtime-leaderboard
2. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn redis passlib[bcrypt] python-multipart jinja2 python-dotenv sqlalchemy
3. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn redis passlib[bcrypt] python-multipart jinja2 python-dotenv sqlalchemy
4. **Start Redis**:
   ```bash
   redis-server
5. **Run the Application**:
   ```bash
   uvicorn backend.main:app --reload
6. **Access**:
   Open your browser and go to http://127.0.0.1:8000.
---
### How to Use

1. **Register a User**:

Go to /register and create a new user.

2. **Login**:

Go to /login and log in with your credentials.

3. **Submit a Score**:

Go to /submit_score, fill out the form, and submit it.

4. **View the Leaderboard**:

Go to /leaderboard/{game} to see the real-time leaderboard.

---
### Example Workflow

1. **Register a User**:

   ```bash
   curl -X POST "http://127.0.0.1:8000/register" -H "Content-Type: application/json" -d '{"username": "alice", "password": "alice123"}'

2. **Login**:

   ```bash
   curl -X POST "http://127.0.0.1:8000/login" -H "Content-Type: application/json" -d '{"username": "alice", "password": "alice123"}'

4. **Submit a Score**:

   ```bash
   curl -X POST "http://127.0.0.1:8000/submit_score" -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"game": "game1", "score": 5}'

5. **View the Leaderboard**:

Open http://127.0.0.1:8000/leaderboard/game1 in your browser.
