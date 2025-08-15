# -*- coding: utf-8 -*-
"""
Entry point for Render deployment
Mobile Store System - Production Ready
"""

from flask import Flask
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_app():
    """Create and configure the Flask application for production"""
    
    # Import the main app
    from app import app, db
    
    # Production configuration
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    # Use environment variables for production settings
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-production-secret-key-change-this')
    
    # Database configuration for production
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Handle PostgreSQL URL format for Render
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fallback to SQLite for development
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phone_store.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Create tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    return app

# Create the application instance
application = create_app()
app = application  # For compatibility

@app.route("/health")
def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy", "message": "🚀 Mobile Store System is running on Render!"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)