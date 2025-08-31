from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from .app import app, db
from .models import User, Admin, Follow, CoachingAd, LiveMatch, StoreProduct, ProfileView
import urllib.parse
from sqlalchemy import or_

# Owner credentials are now stored in the database
# The first user with is_owner=True will be the owner

@app.route('/')
def index():
    # Don't display live matches and store products on the home page
    # They will only be displayed on their respective pages after a search
    return render_template('index.html', 
                         live_matches=None,
                         store_products=None)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        age = request.form.get('age')
        state = request.form.get('state')
        city = request.form.get('city')
        area = request.form.get('area')
        cricket_role = request.form.get('cricket_role')
        availability = request.form.get('availability')
        phone = request.form.get('phone')
        gender = request.form.get('gender')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            name=name,
            age=int(age) if age else None,
            state=state,
            city=city,
            area=area,
            cricket_role=cricket_role,
            availability=availability,
            phone=phone,
            gender=gender
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # First check if it's a regular user or owner
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # Check if user is the owner
            if user.is_owner:
                session['is_owner'] = True
                session['admin_username'] = username
                login_user(user)  # Also login as regular user
                return redirect(url_for('owner_dashboard'))
            else:
                # Regular user login
                login_user(user)
                return redirect(url_for('profile'))
        
        # Then check if it's an admin
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password) and admin.is_approved:
            session['is_admin'] = True
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            return redirect(url_for('admin_dashboard'))
        
        # If we get here, the credentials were invalid
        flash('Invalid username or password')
    
    return render_template('unified_login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    # Redirect owners to the owner dashboard
    if current_user.is_owner:
        return redirect(url_for('owner_dashboard'))
    
    followers_count = current_user.get_followers_count()
    following_count = current_user.get_following_count()
    return render_template('profile.html', 
                         followers_count=followers_count,
                         following_count=following_count)

@app.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    current_user.name = request.form.get('name')
    current_user.age = int(request.form.get('age')) if request.form.get('age') else None
    current_user.state = request.form.get('state')
    current_user.city = request.form.get('city')
    current_user.area = request.form.get('area')
    current_user.cricket_role = request.form.get('cricket_role')
    current_user.availability = request.form.get('availability')
    current_user.phone = request.form.get('phone')
    current_user.gender = request.form.get('gender')
    
    db.session.commit()
    flash('Profile updated successfully!')
    return redirect(url_for('profile'))

@app.route('/reset_password', methods=['POST'])
@login_required
def reset_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Validate current password
    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('profile'))
    
    # Validate new password
    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('profile'))
    
    # Update password
    current_user.set_password(new_password)
    db.session.commit()
    
    flash('Your password has been updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/search_players')
@login_required
def search_players():
    state = request.args.get('state', '')
    city = request.args.get('city', '')
    area = request.args.get('area', '')
    role = request.args.get('role', '')
    
    # Only show players if at least one search parameter is provided
    players = []
    coaching_ads = []
    search_performed = any([state, city, area, role])
    
    if search_performed:
        query = User.query.filter(User.id != current_user.id)
        
        if state:
            query = query.filter(User.state.ilike(f'%{state}%'))
        if city:
            query = query.filter(User.city.ilike(f'%{city}%'))
        if area:
            query = query.filter(User.area.ilike(f'%{area}%'))
        if role and role != 'all':
            query = query.filter(User.cricket_role == role)
        
        players = query.all()
        
        # Record profile views for each player in search results
        for player in players:
            # Check if already viewed
            existing_view = ProfileView.query.filter_by(
                viewer_id=current_user.id,
                viewed_id=player.id
            ).first()
            
            # If not viewed before, create a new view record
            if not existing_view:
                view_record = ProfileView(
                    viewer_id=current_user.id,
                    viewed_id=player.id
                )
                db.session.add(view_record)
        
        # Find coaching ads based on user's location search criteria
        coaching_query = CoachingAd.query
        
        # Use the same location filters as the player search
        if state:
            coaching_query = coaching_query.filter(CoachingAd.state.ilike(f'%{state}%'))
        if city:
            coaching_query = coaching_query.filter(CoachingAd.city.ilike(f'%{city}%'))
        if area:
            coaching_query = coaching_query.filter(CoachingAd.area.ilike(f'%{area}%'))
            
        coaching_ads = coaching_query.all()
        
        db.session.commit()
    
    return render_template('search_players.html', 
                         players=players,
                         coaching_ads=coaching_ads,
                         search_performed=search_performed,
                         search_state=state, 
                         search_city=city, 
                         search_area=area, 
                         search_role=role)

@app.route('/player/<int:player_id>')
@login_required
def player_detail(player_id):
    player = User.query.get_or_404(player_id)
    
    # Check if user has permission to view this profile
    has_viewed = ProfileView.query.filter_by(
        viewer_id=current_user.id,
        viewed_id=player_id
    ).first()
    
    # Allow viewing own profile or if already viewed through search
    if player_id != current_user.id and not has_viewed:
        flash('You must search for players to view their profiles.')
        return redirect(url_for('search_players'))
    
    is_following = current_user.is_following(player)
    followers_count = player.get_followers_count()
    following_count = player.get_following_count()
    
    return render_template('player_detail.html', 
                         player=player,
                         is_following=is_following,
                         followers_count=followers_count,
                         following_count=following_count)

@app.route('/follow/<int:player_id>')
@login_required
def follow_player(player_id):
    player = User.query.get_or_404(player_id)
    if player != current_user:
        current_user.follow(player)
        db.session.commit()
        flash(f'You are now following {player.name}!')
    return redirect(url_for('player_detail', player_id=player_id))

@app.route('/unfollow/<int:player_id>')
@login_required
def unfollow_player(player_id):
    player = User.query.get_or_404(player_id)
    current_user.unfollow(player)
    db.session.commit()
    flash(f'You unfollowed {player.name}!')
    return redirect(url_for('player_detail', player_id=player_id))

# Admin routes

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    # Check if user is logged in and is the owner
    if not current_user.is_authenticated or not current_user.is_owner:
        flash('Only the owner can create admin accounts', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        if Admin.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('admin_register.html')
        
        if Admin.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('admin_register.html')
        
        admin = Admin(username=username, email=email, name=name, is_approved=True)  # Auto-approve since owner is creating
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        flash('Admin account created successfully!', 'success')
        return redirect(url_for('owner_dashboard'))
    
    return render_template('admin_register.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_owner', None)
    session.pop('is_admin', None)
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    return redirect(url_for('index'))

@app.route('/owner/dashboard')
@login_required
def owner_dashboard():
    # Check if the current user is the owner
    if not current_user.is_owner:
        flash('Only the owner can access this page', 'danger')
        return redirect(url_for('profile'))
    
    # Set the session variable for backward compatibility
    session['is_owner'] = True
    session['admin_username'] = current_user.username
    
    pending_admins = Admin.query.filter_by(is_approved=False).all()
    approved_admins = Admin.query.filter_by(is_approved=True).all()
    total_users = User.query.count()
    total_coaching_ads = CoachingAd.query.count()
    total_matches = LiveMatch.query.count()
    total_products = StoreProduct.query.count()
    
    return render_template('owner_dashboard.html',
                         pending_admins=pending_admins,
                         approved_admins=approved_admins,
                         total_users=total_users,
                         total_coaching_ads=total_coaching_ads,
                         total_matches=total_matches,
                         total_products=total_products)

@app.route('/database/management')
@login_required
def database_management():
    # Only owner can access this page
    if not current_user.is_owner:
        flash('Only the owner can access the database management page.', 'danger')
        return redirect(url_for('profile'))
    
    import os
    import sqlite3
    import datetime
    
    # Get the path to the SQLite database file
    db_path = os.path.join(app.root_path, '..', 'instance', 'cricket_community.db')
    backup_dir = os.path.join(app.root_path, 'backups')
    last_backup_file = os.path.join(backup_dir, 'last_backup.txt')
    
    # Calculate database size
    try:
        db_size_bytes = os.path.getsize(db_path)
        if db_size_bytes < 1024:
            db_size = f"{db_size_bytes} bytes"
        elif db_size_bytes < 1024 * 1024:
            db_size = f"{db_size_bytes / 1024:.1f} KB"
        else:
            db_size = f"{db_size_bytes / (1024 * 1024):.1f} MB"
    except Exception:
        db_size = "Unknown"
    
    # Get last backup time
    try:
        if os.path.exists(last_backup_file):
            with open(last_backup_file, 'r') as f:
                last_backup = f.read().strip()
        else:
            last_backup = 'Never'
    except Exception:
        last_backup = 'Never'
    
    # Get database statistics
    total_tables = 7  # User, Admin, Follow, CoachingAd, LiveMatch, StoreProduct, ProfileView
    total_records = User.query.count() + Admin.query.count() + Follow.query.count() + \
                   CoachingAd.query.count() + LiveMatch.query.count() + \
                   StoreProduct.query.count() + ProfileView.query.count()
    
    # Get table information with actual sizes
    tables = []
    
    # Connect to the database to get table sizes
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get the page size and page count for each table
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        
        # Get table information
        model_map = {
            'User': User,
            'Admin': Admin,
            'Follow': Follow,
            'CoachingAd': CoachingAd,
            'LiveMatch': LiveMatch,
            'StoreProduct': StoreProduct,
            'ProfileView': ProfileView
        }
        
        for table_name, model in model_map.items():
            # Get record count
            record_count = model.query.count()
            
            # Get table size (approximate)
            cursor.execute(f"SELECT count(*) FROM sqlite_master WHERE name='{table_name.lower()}'")
            if cursor.fetchone()[0] > 0:
                cursor.execute(f"PRAGMA table_info({table_name.lower()})")
                columns = cursor.fetchall()
                
                # Estimate size based on record count and column types
                avg_row_size = 0
                for col in columns:
                    col_type = col[2].lower()
                    if 'int' in col_type:
                        avg_row_size += 8
                    elif 'text' in col_type or 'varchar' in col_type:
                        avg_row_size += 50  # Assume average text length
                    elif 'bool' in col_type:
                        avg_row_size += 1
                    elif 'date' in col_type or 'time' in col_type:
                        avg_row_size += 8
                    else:
                        avg_row_size += 8  # Default size
                
                estimated_size = record_count * avg_row_size
                
                if estimated_size < 1024:
                    size_str = f"{estimated_size} bytes"
                elif estimated_size < 1024 * 1024:
                    size_str = f"{estimated_size / 1024:.1f} KB"
                else:
                    size_str = f"{estimated_size / (1024 * 1024):.1f} MB"
            else:
                size_str = "Unknown"
            
            tables.append({
                'name': table_name,
                'records': record_count,
                'size': size_str
            })
        
        conn.close()
    except Exception as e:
        # If there's an error, fall back to basic information
        tables = [
            {'name': 'User', 'records': User.query.count(), 'size': 'Unknown'},
            {'name': 'Admin', 'records': Admin.query.count(), 'size': 'Unknown'},
            {'name': 'Follow', 'records': Follow.query.count(), 'size': 'Unknown'},
            {'name': 'CoachingAd', 'records': CoachingAd.query.count(), 'size': 'Unknown'},
            {'name': 'LiveMatch', 'records': LiveMatch.query.count(), 'size': 'Unknown'},
            {'name': 'StoreProduct', 'records': StoreProduct.query.count(), 'size': 'Unknown'},
            {'name': 'ProfileView', 'records': ProfileView.query.count(), 'size': 'Unknown'}
        ]
    
    return render_template('database_management.html', 
                          total_tables=total_tables,
                          total_records=total_records,
                          db_size=db_size,
                          last_backup=last_backup,
                          tables=tables)

@app.route('/backup_database')
@login_required
def backup_database():
    # Only owner can access this functionality
    if not current_user.is_owner:
        flash('Only the owner can perform database backups.', 'danger')
        return redirect(url_for('profile'))
    
    import os
    import datetime
    import shutil
    from flask import send_file
    
    # Create backups directory if it doesn't exist
    backup_dir = os.path.join(app.root_path, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'database_backup_{timestamp}.db'
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Get the path to the SQLite database file
    db_path = os.path.join(app.root_path, '..', 'instance', 'cricket_community.db')
    
    try:
        
        # Create a copy of the database file
        shutil.copy2(db_path, backup_path)
        
        # Update last backup time in a file for tracking
        with open(os.path.join(backup_dir, 'last_backup.txt'), 'w') as f:
            f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Return the backup file as a download
        return send_file(backup_path, as_attachment=True, download_name=backup_filename)
    except Exception as e:
        flash(f'Error creating backup: {str(e)}', 'danger')
        return redirect(url_for('database_management'))

@app.route('/optimize_database')
def optimize_database():
    # Only owner can access this functionality
    if not session.get('is_owner'):
        flash('Only the owner can optimize the database.', 'danger')
        return redirect(url_for('login'))
    
    import sqlite3
    import os
    
    # Get the path to the SQLite database file
    db_path = os.path.join(app.root_path, '..', 'instance', 'cricket_community.db')
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Run VACUUM to rebuild the database file, reclaiming free space
        cursor.execute('VACUUM')
        
        # Run ANALYZE to collect statistics that help optimize queries
        cursor.execute('ANALYZE')
        
        # Optimize all tables by rebuilding indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            if not table_name.startswith('sqlite_'):
                cursor.execute(f'REINDEX {table_name}')
        
        conn.commit()
        conn.close()
        
        flash('Database optimization completed successfully. Performance has been improved.', 'success')
    except Exception as e:
        flash(f'Error optimizing database: {str(e)}', 'danger')
    
    return redirect(url_for('database_management'))

@app.route('/reset_database', methods=['POST'])
def reset_database():
    # Only owner can access this functionality
    if not session.get('is_owner'):
        flash('Only the owner can reset the database.', 'danger')
        return redirect(url_for('login'))
    
    confirmation = request.form.get('confirmation')
    if confirmation != 'RESET':
        flash('Invalid confirmation. Database reset aborted.', 'danger')
        return redirect(url_for('database_management'))
    
    import os
    import sqlite3
    import shutil
    import datetime
    
    # Create a backup before resetting
    backup_dir = os.path.join(app.root_path, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Generate backup filename with timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'pre_reset_backup_{timestamp}.db'
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Get the path to the SQLite database file
    db_path = os.path.join(app.root_path, '..', 'instance', 'cricket_community.db')
    
    try:
        # Create a backup copy before resetting
        shutil.copy2(db_path, backup_path)
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = cursor.fetchall()
        
        # Drop all tables except for admin and owner accounts
        for table in tables:
            table_name = table[0]
            if table_name != 'admin':
                cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
        
        # Recreate the schema (this would typically be done by importing your models and calling db.create_all())
        # For this implementation, we'll just recreate the Admin table and keep the owner account
        
        # Create the Admin table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            is_approved BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create the User table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT,
            age INTEGER,
            state TEXT,
            city TEXT,
            area TEXT,
            cricket_role TEXT,
            availability TEXT,
            phone TEXT,
            gender TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create other tables as needed
        # ...
        
        conn.commit()
        conn.close()
        
        # Reinitialize the database with SQLAlchemy
        db.create_all()
        
        flash('Database has been reset to its initial state. A backup was created before resetting.', 'success')
    except Exception as e:
        flash(f'Error resetting database: {str(e)}', 'danger')
    
    return redirect(url_for('database_management'))

@app.route('/restore_database', methods=['POST'])
def restore_database():
    # Only owner can access this functionality
    if not session.get('is_owner'):
        flash('Only the owner can restore database backups.', 'danger')
        return redirect(url_for('login'))
    
    # Check if a file was uploaded
    if 'backup_file' not in request.files:
        flash('No backup file selected.', 'danger')
        return redirect(url_for('database_management'))
    
    backup_file = request.files['backup_file']
    if backup_file.filename == '':
        flash('No backup file selected.', 'danger')
        return redirect(url_for('database_management'))
    
    import os
    import shutil
    import datetime
    import sqlite3
    
    # Get the path to the SQLite database file
    db_path = os.path.join(app.root_path, '..', 'instance', 'cricket_community.db')
    
    # Create a temporary directory for the uploaded file
    temp_dir = os.path.join(app.root_path, 'temp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Create a backup of the current database before restoring
    backup_dir = os.path.join(app.root_path, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Generate backup filename with timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'pre_restore_backup_{timestamp}.db'
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # Create a backup of the current database
        shutil.copy2(db_path, backup_path)
        
        # Save the uploaded file to a temporary location
        temp_file_path = os.path.join(temp_dir, 'temp_restore.db')
        backup_file.save(temp_file_path)
        
        # Verify that the uploaded file is a valid SQLite database
        try:
            conn = sqlite3.connect(temp_file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            if not tables:
                flash('The uploaded file is not a valid database backup.', 'danger')
                os.remove(temp_file_path)
                return redirect(url_for('database_management'))
        except sqlite3.Error:
            flash('The uploaded file is not a valid SQLite database.', 'danger')
            os.remove(temp_file_path)
            return redirect(url_for('database_management'))
        
        # Replace the current database with the uploaded backup
        shutil.copy2(temp_file_path, db_path)
        
        # Clean up the temporary file
        os.remove(temp_file_path)
        
        flash('Database restored successfully from backup. A backup of the previous state was created.', 'success')
    except Exception as e:
        flash(f'Error restoring database: {str(e)}', 'danger')
    
    return redirect(url_for('database_management'))

@app.route('/view_table/<table_name>')
def view_table(table_name):
    # Only owner can access this functionality
    if not session.get('is_owner'):
        flash('Only the owner can view database tables.', 'danger')
        return redirect(url_for('login'))
    
    import sqlite3
    import os
    
    # Get the path to the SQLite database file
    db_path = os.path.join(app.root_path, '..', 'instance', 'cricket_community.db')
    
    # Validate table name to prevent SQL injection
    valid_tables = ['user', 'admin', 'follow', 'coaching_ad', 'live_match', 'store_product', 'profile_view']
    model_map = {
        'user': User,
        'admin': Admin,
        'follow': Follow,
        'coaching_ad': CoachingAd,
        'live_match': LiveMatch,
        'store_product': StoreProduct,
        'profile_view': ProfileView
    }
    
    # Convert CamelCase to snake_case for table name
    import re
    snake_case_table = re.sub(r'(?<!^)(?=[A-Z])', '_', table_name).lower()
    
    if snake_case_table not in valid_tables and table_name not in valid_tables:
        flash(f'Invalid table name: {table_name}', 'danger')
        return redirect(url_for('database_management'))
    
    try:
        # Use SQLAlchemy to get table data
        if table_name in model_map:
            model = model_map[table_name]
        else:
            model = model_map[snake_case_table]
        
        # Get all records from the table
        records = model.query.all()
        
        # Get column names
        if records:
            # Get the first record and extract its attributes
            first_record = records[0]
            columns = [column.name for column in model.__table__.columns]
        else:
            # If no records, get columns from the model's __table__ attribute
            columns = [column.name for column in model.__table__.columns]
        
        # Prepare data for display
        table_data = []
        for record in records:
            row_data = {}
            for column in columns:
                row_data[column] = getattr(record, column)
            table_data.append(row_data)
        
        # Render a template to display the table data
        return render_template('view_table.html', 
                              table_name=table_name,
                              columns=columns,
                              records=table_data,
                              record_count=len(records))
    except Exception as e:
        flash(f'Error viewing table {table_name}: {str(e)}', 'danger')
        return redirect(url_for('database_management'))

@app.route('/export_table/<table_name>')
def export_table(table_name):
    # Only owner can access this functionality
    if not session.get('is_owner'):
        flash('Only the owner can export database tables.', 'danger')
        return redirect(url_for('login'))
    
    import csv
    import io
    import os
    import re
    from flask import send_file
    from datetime import datetime
    
    # Validate table name to prevent SQL injection
    valid_tables = ['user', 'admin', 'follow', 'coaching_ad', 'live_match', 'store_product', 'profile_view']
    model_map = {
        'user': User,
        'admin': Admin,
        'follow': Follow,
        'coaching_ad': CoachingAd,
        'live_match': LiveMatch,
        'store_product': StoreProduct,
        'profile_view': ProfileView
    }
    
    # Convert CamelCase to snake_case for table name
    snake_case_table = re.sub(r'(?<!^)(?=[A-Z])', '_', table_name).lower()
    
    if snake_case_table not in valid_tables and table_name not in valid_tables:
        flash(f'Invalid table name: {table_name}', 'danger')
        return redirect(url_for('database_management'))
    
    try:
        # Use SQLAlchemy to get table data
        if table_name in model_map:
            model = model_map[table_name]
        else:
            model = model_map[snake_case_table]
        
        # Get all records from the table
        records = model.query.all()
        
        # Get column names
        if records:
            columns = [column.name for column in model.__table__.columns]
        else:
            columns = [column.name for column in model.__table__.columns]
        
        # Create a CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header row
        writer.writerow(columns)
        
        # Write data rows
        for record in records:
            row = [getattr(record, column) for column in columns]
            writer.writerow(row)
        
        # Prepare the CSV for download
        output.seek(0)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{table_name}_export_{timestamp}.csv'
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Error exporting table {table_name}: {str(e)}', 'danger')
        return redirect(url_for('database_management'))

@app.route('/truncate_table/<table_name>')
def truncate_table(table_name):
    # Only owner can access this functionality
    if not session.get('is_owner'):
        flash('Only the owner can truncate database tables.', 'danger')
        return redirect(url_for('login'))
    
    import re
    import os
    import sqlite3
    import datetime
    import shutil
    
    # Validate table name to prevent SQL injection
    valid_tables = ['user', 'admin', 'follow', 'coaching_ad', 'live_match', 'store_product', 'profile_view']
    model_map = {
        'user': User,
        'admin': Admin,
        'follow': Follow,
        'coaching_ad': CoachingAd,
        'live_match': LiveMatch,
        'store_product': StoreProduct,
        'profile_view': ProfileView
    }
    
    # Convert CamelCase to snake_case for table name
    snake_case_table = re.sub(r'(?<!^)(?=[A-Z])', '_', table_name).lower()
    
    if snake_case_table not in valid_tables and table_name not in valid_tables:
        flash(f'Invalid table name: {table_name}', 'danger')
        return redirect(url_for('database_management'))
    
    # Protect the admin table if the owner is trying to truncate it
    if table_name == 'admin' or snake_case_table == 'admin':
        flash('Cannot truncate the admin table for security reasons.', 'danger')
        return redirect(url_for('database_management'))
    
    # Get the path to the SQLite database file
    db_path = os.path.join(app.root_path, '..', 'instance', 'cricket_community.db')
    
    # Create a backup before truncating
    backup_dir = os.path.join(app.root_path, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Generate backup filename with timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'pre_truncate_{table_name}_{timestamp}.db'
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # Create a backup copy before truncating
        shutil.copy2(db_path, backup_path)
        
        # Use SQLAlchemy to truncate the table
        if table_name in model_map:
            model = model_map[table_name]
        else:
            model = model_map[snake_case_table]
        
        # Delete all records from the table
        model.query.delete()
        db.session.commit()
        
        flash(f'Table {table_name} has been truncated successfully. A backup was created before truncating.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error truncating table {table_name}: {str(e)}', 'danger')
    
    return redirect(url_for('view_table', table_name=table_name))

@app.route('/owner/approve_admin/<int:admin_id>')
def approve_admin(admin_id):
    if not session.get('is_owner'):
        return redirect(url_for('admin_login'))
    
    admin = Admin.query.get_or_404(admin_id)
    admin.is_approved = True
    db.session.commit()
    flash(f'Admin {admin.username} approved successfully!')
    return redirect(url_for('owner_dashboard'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    admin_id = session.get('admin_id')
    coaching_ads = CoachingAd.query.filter_by(created_by=admin_id).count()
    live_matches = LiveMatch.query.filter_by(created_by=admin_id).count()
    store_products = StoreProduct.query.filter_by(created_by=admin_id).count()
    
    return render_template('admin_dashboard.html',
                         coaching_ads=coaching_ads,
                         live_matches=live_matches,
                         store_products=store_products)

@app.route('/admin/coaching')
def manage_coaching():
    if not session.get('is_admin') and not session.get('is_owner'):
        return redirect(url_for('admin_login'))
    
    admin_id = session.get('admin_id')
    search = request.args.get('search', '')
    
    if session.get('is_owner'):
        query = CoachingAd.query
    else:
        query = CoachingAd.query.filter_by(created_by=admin_id)
    
    if search:
        query = query.filter(
            or_(
                CoachingAd.title.ilike(f'%{search}%'),
                CoachingAd.description.ilike(f'%{search}%'),
                CoachingAd.city.ilike(f'%{search}%'),
                CoachingAd.state.ilike(f'%{search}%'),
                CoachingAd.area.ilike(f'%{search}%')
            )
        )
    
    coaching_ads = query.all()
    
    return render_template('manage_coaching.html', coaching_ads=coaching_ads, search=search)

@app.route('/admin/coaching/add', methods=['POST'])
def add_coaching_ad():
    if not session.get('is_admin') and not session.get('is_owner'):
        return redirect(url_for('admin_login'))
    
    admin_id = session.get('admin_id')
    
    coaching_ad = CoachingAd(
        title=request.form.get('title'),
        description=request.form.get('description'),
        location=request.form.get('location'),
        state=request.form.get('state'),
        city=request.form.get('city'),
        area=request.form.get('area'),
        contact_info=request.form.get('contact_info'),
        coupon_code=request.form.get('coupon_code'),
        discount_percentage=int(request.form.get('discount_percentage')) if request.form.get('discount_percentage') else None,
        price=float(request.form.get('price')) if request.form.get('price') else None,
        created_by=admin_id
    )
    
    db.session.add(coaching_ad)
    db.session.commit()
    flash('Coaching ad added successfully!')
    return redirect(url_for('manage_coaching'))

@app.route('/admin/coaching/delete/<int:ad_id>', methods=['POST'])
def delete_coaching_ad(ad_id):
    if not session.get('is_admin') and not session.get('is_owner'):
        return redirect(url_for('admin_login'))
    
    ad = CoachingAd.query.get_or_404(ad_id)
    delete_password = request.form.get('delete_password')
    
    # Check if user has permission to delete this ad
    if session.get('is_owner') or ad.created_by == session.get('admin_id'):
        # Verify the delete password
        if delete_password == 'deletedata':
            db.session.delete(ad)
            db.session.commit()
            flash('Coaching ad deleted successfully!')
        else:
            flash('Incorrect deletion password. Please try again.', 'danger')
            return redirect(url_for('manage_coaching'))
    else:
        flash('You do not have permission to delete this ad.', 'danger')
    
    return redirect(url_for('manage_coaching'))

@app.route('/admin/matches')
def manage_matches():
    if not session.get('is_admin') and not session.get('is_owner'):
        return redirect(url_for('admin_login'))
    
    admin_id = session.get('admin_id')
    if session.get('is_owner'):
        live_matches = LiveMatch.query.all()
    else:
        live_matches = LiveMatch.query.filter_by(created_by=admin_id).all()
    
    return render_template('manage_matches.html', live_matches=live_matches)

@app.route('/admin/matches/add', methods=['POST'])
def add_live_match():
    if not session.get('is_admin') and not session.get('is_owner'):
        return redirect(url_for('admin_login'))
    
    admin_id = session.get('admin_id')
    
    live_match = LiveMatch(
        title=request.form.get('title'),
        description=request.form.get('description'),
        youtube_url=request.form.get('youtube_url'),
        teams=request.form.get('teams'),
        is_live=bool(request.form.get('is_live')),
        state=request.form.get('state'),
        city=request.form.get('city'),
        area=request.form.get('area'),
        location=request.form.get('location'),
        created_by=admin_id
    )
    
    db.session.add(live_match)
    db.session.commit()
    flash('Live match added successfully!')
    return redirect(url_for('manage_matches'))

@app.route('/admin/matches/delete/<int:match_id>', methods=['POST'])
def delete_live_match(match_id):
    if not session.get('is_admin') and not session.get('is_owner'):
        return redirect(url_for('admin_login'))
    
    match = LiveMatch.query.get_or_404(match_id)
    delete_password = request.form.get('delete_password')
    
    # Check if user has permission to delete this match
    if session.get('is_owner') or match.created_by == session.get('admin_id'):
        # Verify the delete password
        if delete_password == 'deletedata':
            db.session.delete(match)
            db.session.commit()
            flash('Live match deleted successfully!')
        else:
            flash('Incorrect deletion password. Please try again.', 'danger')
            return redirect(url_for('manage_matches'))
    else:
        flash('You do not have permission to delete this match.', 'danger')
    
    return redirect(url_for('manage_matches'))

@app.route('/admin/store')
def manage_store():
    if not session.get('is_admin') and not session.get('is_owner'):
        return redirect(url_for('admin_login'))
    
    admin_id = session.get('admin_id')
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    if session.get('is_owner'):
        query = StoreProduct.query
    else:
        query = StoreProduct.query.filter_by(created_by=admin_id)
    
    if search:
        query = query.filter(
            or_(
                StoreProduct.name.ilike(f'%{search}%'),
                StoreProduct.description.ilike(f'%{search}%')
            )
        )
    
    if category:
        query = query.filter(StoreProduct.category.ilike(f'%{category}%'))
    
    store_products = query.all()
    
    return render_template('manage_store.html', store_products=store_products, search=search, category=category)

@app.route('/admin/store/add', methods=['POST'])
def add_store_product():
    if not session.get('is_admin') and not session.get('is_owner'):
        return redirect(url_for('admin_login'))
    
    admin_id = session.get('admin_id')
    
    store_product = StoreProduct(
        name=request.form.get('name'),
        description=request.form.get('description'),
        price=float(request.form.get('price')) if request.form.get('price') else None,
        category=request.form.get('category'),
        image_url=request.form.get('image_url'),
        product_url=request.form.get('product_url'),
        in_stock=bool(request.form.get('in_stock')),
        created_by=admin_id
    )
    
    db.session.add(store_product)
    db.session.commit()
    flash('Store product added successfully!')
    return redirect(url_for('manage_store'))

@app.route('/admin/store/delete/<int:product_id>', methods=['POST'])
def delete_store_product(product_id):
    if not session.get('is_admin') and not session.get('is_owner'):
        return redirect(url_for('admin_login'))
    
    product = StoreProduct.query.get_or_404(product_id)
    delete_password = request.form.get('delete_password')
    
    # Check if user has permission to delete this product
    if session.get('is_owner') or product.created_by == session.get('admin_id'):
        # Verify the delete password
        if delete_password == 'deletedata':
            db.session.delete(product)
            db.session.commit()
            flash('Store product deleted successfully!')
        else:
            flash('Incorrect deletion password. Please try again.', 'danger')
            return redirect(url_for('manage_store'))
    else:
        flash('You do not have permission to delete this product.', 'danger')
    
    return redirect(url_for('manage_store'))

@app.route('/coaching')
def public_coaching():
    search = request.args.get('search', '')
    location = request.args.get('location', '')
    
    # Only show results if search or location is provided
    coaching_ads = []
    search_performed = False
    
    if search or location:
        search_performed = True
        query = CoachingAd.query
        
        if search:
            query = query.filter(
                or_(
                    CoachingAd.title.ilike(f'%{search}%'),
                    CoachingAd.description.ilike(f'%{search}%')
                )
            )
        
        if location:
            query = query.filter(
                or_(
                    CoachingAd.city.ilike(f'%{location}%'),
                    CoachingAd.state.ilike(f'%{location}%'),
                    CoachingAd.area.ilike(f'%{location}%')
                )
            )
        
        coaching_ads = query.all()
    
    return render_template('public_coaching.html', coaching_ads=coaching_ads, search=search, location=location, search_performed=search_performed)

@app.route('/store')
def public_store():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    # Only show results if search or category is provided
    store_products = []
    search_performed = False
    
    if search or category:
        search_performed = True
        query = StoreProduct.query.filter_by(in_stock=True)
        
        if search:
            query = query.filter(
                or_(
                    StoreProduct.name.ilike(f'%{search}%'),
                    StoreProduct.description.ilike(f'%{search}%')
                )
            )
        
        if category:
            query = query.filter(StoreProduct.category.ilike(f'%{category}%'))
        
        store_products = query.all()
    
    return render_template('public_store.html', store_products=store_products, search=search, category=category, search_performed=search_performed)

@app.route('/owner/manage_users')
def manage_users():
    if not session.get('is_owner'):
        return redirect(url_for('admin_login'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    gender_filter = request.args.get('gender', '')
    role_filter = request.args.get('role', '')
    
    query = User.query
    
    if search:
        query = query.filter(
            or_(
                User.name.ilike(f'%{search}%'),
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.city.ilike(f'%{search}%'),
                User.state.ilike(f'%{search}%')
            )
        )
    
    if gender_filter:
        query = query.filter(User.gender == gender_filter)
    
    if role_filter:
        query = query.filter(User.cricket_role == role_filter)
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    male_users = User.query.filter_by(gender='male').count()
    female_users = User.query.filter_by(gender='female').count()
    
    return render_template('manage_users.html', 
                         users=users,
                         total_users=total_users,
                         active_users=active_users,
                         male_users=male_users,
                         female_users=female_users,
                         search=search,
                         gender_filter=gender_filter,
                         role_filter=role_filter)

@app.route('/owner/user/<int:user_id>')
def view_user_detail(user_id):
    if not session.get('is_owner'):
        return redirect(url_for('admin_login'))
    
    user = User.query.get_or_404(user_id)
    followers_count = user.get_followers_count()
    following_count = user.get_following_count()
    
    return render_template('user_detail_admin.html',
                         user=user,
                         followers_count=followers_count,
                         following_count=following_count)

@app.route('/owner/user/<int:user_id>/toggle_status')
def toggle_user_status(user_id):
    if not session.get('is_owner'):
        return redirect(url_for('admin_login'))
    
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}!')
    return redirect(url_for('view_user_detail', user_id=user_id))



# Helper function to extract YouTube video ID
def get_youtube_video_id(url):
    """Extract YouTube video ID from URL"""
    if 'youtube.com/watch?v=' in url:
        return url.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    return None

@app.template_filter('youtube_embed')
def youtube_embed_filter(url):
    """Convert YouTube URL to embed URL"""
    video_id = get_youtube_video_id(url)
    if video_id:
        return f"https://www.youtube.com/embed/{video_id}"
    return url

@app.template_filter('whatsapp_url')
def whatsapp_url_filter(phone, message=""):
    """Generate WhatsApp URL for contacting a player"""
    if not phone:
        return "#"
    # Remove any non-digit characters from phone
    clean_phone = ''.join(filter(str.isdigit, phone))
    encoded_message = urllib.parse.quote(message)
    return f"https://wa.me/{clean_phone}?text={encoded_message}"

@app.route('/matches')
def public_matches():
    search = request.args.get('search', '')
    state = request.args.get('state', '')
    city = request.args.get('city', '')
    area = request.args.get('area', '')
    
    # Only show results if search, state, city, or area is provided
    live_matches = []
    search_performed = False
    
    if search or state or city or area:
        search_performed = True
        query = LiveMatch.query.filter_by(is_live=True)
        
        if search:
            query = query.filter(
                or_(
                    LiveMatch.title.ilike(f'%{search}%'),
                    LiveMatch.description.ilike(f'%{search}%'),
                    LiveMatch.teams.ilike(f'%{search}%'),
                    LiveMatch.location.ilike(f'%{search}%')
                )
            )
        
        if state:
            query = query.filter(LiveMatch.state.ilike(f'%{state}%'))
        
        if city:
            query = query.filter(LiveMatch.city.ilike(f'%{city}%'))
        
        if area:
            query = query.filter(LiveMatch.area.ilike(f'%{area}%'))
        
        live_matches = query.order_by(LiveMatch.created_at.desc()).all()
    
    return render_template('public_matches.html', live_matches=live_matches, search=search, state=state, city=city, area=area, search_performed=search_performed)
