# CrickConnect Website

## Overview

This is a Flask-based web application designed to connect cricket enthusiasts with local players and provide a comprehensive platform for cricket-related activities. The platform features user registration/login, player discovery based on location, coaching advertisements, live match streaming, and an integrated cricket store.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite as default (configurable via DATABASE_URL environment variable)
- **Authentication**: Flask-Login for session management
- **Security**: Werkzeug for password hashing and security utilities

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default templating)
- **CSS Framework**: Bootstrap 5.3.0 for responsive design
- **Icons**: Font Awesome 6.4.0 for UI icons
- **JavaScript**: Vanilla JavaScript with Bootstrap components

### Database Design
- **User Model**: Stores player profiles with location data (state, city, area), cricket roles, gender, and contact information
- **Follow System**: Many-to-many relationship for user connections
- **Admin System**: Separate admin authentication with approval workflow
- **Content Models**: CoachingAd, LiveMatch, and StoreProduct (referenced but not fully implemented)

## Key Components

### User Management
- **Registration**: Multi-step form collecting cricket-specific profile data
- **Authentication**: Username/password login with session management
- **Profile System**: Detailed player profiles with cricket roles and availability
- **Follow System**: Social networking features for player connections

### Location-Based Discovery
- **Hierarchical Search**: State > City > Area filtering system
- **Player Matching**: Location-based player discovery with role filtering
- **Search Interface**: Advanced filtering options for finding compatible players

### Admin Panel
- **Dual Admin System**: Owner (protected credentials) and approved admins
- **User Management**: Complete user profile management with search, filtering, and status control
- **Content Management**: Tools for managing coaching ads, live matches, and store products
- **Dashboard**: Statistics and management interface

### Communication Features
- **WhatsApp Integration**: Direct WhatsApp links for player communication
- **Profile Sharing**: Player detail pages with contact options

## Data Flow

1. **User Registration**: New users create profiles with location and cricket preferences
2. **Player Discovery**: Users search for nearby players using location filters
3. **Connection**: Users can follow other players and contact them via WhatsApp
4. **Admin Content**: Admins manage coaching ads, live matches, and store products
5. **Monetization**: Platform supports coaching ads, YouTube live matches, and product sales

## External Dependencies

### Frontend Dependencies
- Bootstrap 5.3.0 (CDN)
- Font Awesome 6.4.0 (CDN)
- Custom CSS and JavaScript files

### Backend Dependencies
- Flask and Flask extensions (SQLAlchemy, Login)
- Werkzeug for security utilities
- SQLAlchemy for database operations

### Third-Party Integrations
- **WhatsApp**: Direct messaging links using WhatsApp URL scheme
- **YouTube**: Embedded live match videos (referenced but embed logic not implemented)
- **Database**: Configurable database backend (SQLite default, PostgreSQL supported)

## Deployment Strategy

### Environment Configuration
- **Session Secret**: Configurable via SESSION_SECRET environment variable
- **Database**: Configurable via DATABASE_URL environment variable
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies

### Database Setup
- **Auto-initialization**: Database tables created automatically on app startup
- **Migration Support**: SQLAlchemy-based schema management
- **Connection Pooling**: Configured for production deployment

### Security Considerations
- **Password Hashing**: Werkzeug security for password protection
- **Session Management**: Flask-Login for secure user sessions
- **Admin Access**: Two-tier admin system with owner approval workflow

### Scalability Features
- **Database Pooling**: Connection pool with pre-ping for reliability
- **Static Assets**: Separate static file serving capability
- **Template Caching**: Jinja2 template system with caching support

### Recent Changes (July 29, 2025)
- **Website Rebranding**: Changed name from "Cricket Community" to "CrickConnect" throughout
- **Copyright Update**: Updated footer to "© 2025 CrickConnect. All rights reserved."
- **Privacy System**: Implemented profile view tracking - users can only see profiles after searching
- **Search Enhancement**: Modified search to show no players by default, only displaying results after active search
- **Database Enhancement**: Added ProfileView table to track user profile access
- **Gender Field**: Added gender selection to user profiles with database migration
- **User Management System**: Created comprehensive user management for owner dashboard
- **Protected Owner Credentials**: Removed visible owner credentials from admin login page
- **Enhanced User Profiles**: Added gender display in search results and player details
- **Admin Dashboard**: Added user management card to owner dashboard with statistics
- **Delete Functionality**: Added remove/delete options for YouTube matches, coaching ads, and store products (owner/admin access only)
- **Search Functionality**: Added search bars for products and coaching ads on both management and public pages
- **Public Pages**: Created public coaching and store pages with search and filter capabilities accessible to all users
- **Navigation Enhancement**: Added coaching and store links to main navigation for easy access

### Incomplete Features
- Some models (CoachingAd, LiveMatch, StoreProduct, Admin, Follow) are referenced in routes but not defined in models.py
- YouTube embed functionality referenced but not implemented
- Some template filters (youtube_embed, whatsapp_url) used but not defined
- Chat functionality mentioned in requirements but not implemented