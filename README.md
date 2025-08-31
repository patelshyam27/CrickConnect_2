# GameConnect - Cricket Community Platform

A web application that helps cricket lovers find local players, access coaching resources, watch live matches, and purchase cricket equipment.

## Features

- User registration and authentication
- Player search by location and role
- Profile management
- Follow other players
- Coaching advertisements
- Live match streaming
- Cricket equipment store
- Admin dashboard for content management
- Owner dashboard for user management

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python run.py
   ```

## Deployment

This application is configured for deployment on platforms like Heroku using Gunicorn:

```
web: gunicorn wsgi:app
```

## Technologies Used

- Flask
- SQLAlchemy
- Flask-Login
- Bootstrap 5
- Font Awesome
- SQLite (development) / PostgreSQL (production)

## Project Structure

- `/GameConnect` - Main application package
  - `app.py` - Application configuration
  - `models.py` - Database models
  - `routes.py` - Application routes
  - `/templates` - HTML templates
  - `/static` - CSS, JavaScript, and other static files
- `run.py` - Development server script
- `wsgi.py` - WSGI entry point for production
- `Procfile` - Deployment configuration
- `requirements.txt` - Project dependencies