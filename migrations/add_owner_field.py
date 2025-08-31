import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from GameConnect.app import app, db
from GameConnect.models import User
from flask import Flask

# This script adds the is_owner field to the User model and sets up the first owner account

def run_migration():
    with app.app_context():
        # Check if we need to add the column
        try:
            # Try to access the is_owner attribute on a user
            user = User.query.first()
            # If this doesn't raise an exception, the column exists
            print("is_owner column already exists")
        except Exception as e:
            # Column doesn't exist, add it
            print("Adding is_owner column to User model...")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN is_owner BOOLEAN DEFAULT FALSE'))
                conn.commit()
            print("Column added successfully")
        
        # Set up the first owner account if none exists
        owner = User.query.filter_by(is_owner=True).first()
        if not owner:
            print("No owner account found. Creating one...")
            username = input("Enter owner username: ")
            password = input("Enter owner password: ")
            email = input("Enter owner email: ")
            name = input("Enter owner name: ")
            
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                # Update existing user to be owner
                existing_user.is_owner = True
                db.session.commit()
                print(f"User {username} has been set as the owner")
            else:
                # Create new owner account
                owner = User(
                    username=username,
                    email=email,
                    name=name,
                    is_owner=True
                )
                owner.set_password(password)
                db.session.add(owner)
                db.session.commit()
                print(f"Owner account created with username: {username}")
        else:
            print(f"Owner account already exists with username: {owner.username}")

if __name__ == "__main__":
    run_migration()
    print("Migration completed successfully")