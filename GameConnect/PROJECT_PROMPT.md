
# CrickConnect - Cricket Community Platform

## Project Overview
CrickConnect is a comprehensive web-based platform designed to unite cricket enthusiasts by providing tools for player discovery, community building, coaching services, live match streaming, and cricket equipment shopping. Built with Flask and modern web technologies, it serves as a one-stop solution for the cricket community.

## Core Features

### 🏏 Player Discovery & Networking
- **Location-Based Search**: Find cricket players by state, city, and area
- **Role-Based Filtering**: Search by cricket roles (batsman, bowler, all-rounder)
- **Social Networking**: Follow/unfollow system for building connections
- **Direct Communication**: WhatsApp integration for instant player contact
- **Privacy Controls**: Profile view tracking with search-based access

### 👥 User Management System
- **User Registration**: Comprehensive profile creation with cricket-specific details
- **Authentication**: Secure login/logout with session management
- **Profile Management**: Editable profiles with age, location, availability, and contact info
- **Gender Diversity**: Inclusive gender options and filtering

### 🎯 Admin
- **Content Creation**: Tools for managing coaching ads, live matches, and store products
- **User Administration**: Complete user management with search, filtering, and status control
- **Analytics Dashboard**: Statistics and platform insights

### 🏆 Coaching Services
- **Coaching Advertisements**: Create and browse coaching opportunities
- **Location-Based Coaching**: Find coaching services in specific areas
- **Contact Integration**: Direct contact with coaches via WhatsApp and  pay fees and we get Commission

### 📺 Live Match Streaming
- **YouTube Integration**: Embed live cricket matches
- **Match Management**: Add, edit, and delete live match streams
- **Team Information**: Display team details and match descriptions
- **Live Status**: Toggle live/offline status for matches

### 🛒 Cricket Store
- **Product Catalog**: Browse cricket equipment and accessories
- **Category Filtering**: Organize products by type (bat, ball, gloves, etc.)
- **Search Functionality**: Find products by name and description
- **Affiliate Links**: Support for external product links
- **Stock Management**: Track product availability

## Technical Architecture  /  if according to you

### Backend Stack
- **Framework**: Flask (Python)
- **Database**: SQLAlchemy ORM with SQLite (PostgreSQL compatible)
- **Authentication**: Flask-Login for session management
- **Security**: Werkzeug password hashing and security utilities

### Frontend Technologies
- **Template Engine**: Jinja2
- **CSS Framework**: Bootstrap 5.3.0
- **Icons**: Font Awesome 6.4.0
- **JavaScript**: Vanilla JS with Bootstrap components
- **Responsive Design**: Mobile-first approach

### Database Design
- **User Model**: Player profiles with location hierarchy (state → city → area)
- **Follow System**: Many-to-many relationships for social networking
- **Admin System**: Hierarchical admin approval workflow
- **Content Models**: Coaching ads, live matches, and store products
- **Privacy System**: Profile view tracking and access control

### External Integrations
- **WhatsApp API**: Direct messaging via WhatsApp URL scheme
- **YouTube**: Embedded video streaming for live matches
- **Responsive Design**: Works seamlessly across desktop and mobile devices

## User Roles & Permissions

### 🏏 Regular Users
- Create and manage personal cricket profiles
- Search and connect with local players
- Follow/unfollow other players
- View coaching services and store products
- Contact players via WhatsApp




## Key Use Cases

### For Players
1. **Find Local Teammates or plyer**: Search for players in your area by role and availability
2. **Build Networks**: Follow interesting players and build cricket connections
3. **Coordinate Matches**: Use WhatsApp integration to organize games
4. **Find Coaching**: Discover coaching opportunities with location and pricing filters
5. **Shop Equipment**: Browse and purchase cricket gear through integrated store

### For Coaches
1. **Advertise Services**: Create coaching ads with location, pricing, and contact details
2. **Offer Discounts**: Use coupon codes to attract students
3. **Reach Local Players**: Target players in specific geographic areas




## Business Model Opportunities
- **Coaching Commissions**: Revenue sharing with coaching service providers
- **Equipment Sales**: Affiliate marketing for cricket equipment
- **Premium Features**: Enhanced search and networking capabilities
- **Local Sponsorships**: Location-based advertising opportunities


*CrickConnect - Bringing the cricket community together, one connection at a time!* 🏏
