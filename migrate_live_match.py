from GameConnect.app import app, db
import sqlalchemy as sa
import sqlite3

with app.app_context():
    # Get database connection
    conn = db.engine.raw_connection()
    cursor = conn.cursor()
    
    # Check if columns exist before adding them
    try:
        # Add new columns to live_match table
        cursor.execute('ALTER TABLE live_match ADD COLUMN state VARCHAR(50)')
        print("Added state column")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print("State column already exists")
        else:
            print(f"Error adding state column: {e}")
    
    try:
        cursor.execute('ALTER TABLE live_match ADD COLUMN city VARCHAR(50)')
        print("Added city column")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print("City column already exists")
        else:
            print(f"Error adding city column: {e}")
    
    try:
        cursor.execute('ALTER TABLE live_match ADD COLUMN area VARCHAR(100)')
        print("Added area column")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print("Area column already exists")
        else:
            print(f"Error adding area column: {e}")
    
    try:
        cursor.execute('ALTER TABLE live_match ADD COLUMN location VARCHAR(200)')
        print("Added location column")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print("Location column already exists")
        else:
            print(f"Error adding location column: {e}")
    
    # Commit the changes
    conn.commit()
    conn.close()
    
    print('Migration completed!')