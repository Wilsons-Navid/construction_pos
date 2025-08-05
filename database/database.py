# # database/database.py
# import sqlite3
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, Session
# from .models import Base
# import os

# # Database configuration
# DATABASE_URL = "sqlite:///./construction_pos.db"

# # Create engine
# engine = create_engine(
#     DATABASE_URL,
#     connect_args={"check_same_thread": False}
# )

# # Create session factory
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# class DatabaseManager:
#     def __init__(self):
#         self.engine = engine
#         self.SessionLocal = SessionLocal
        
#     def create_tables(self):
#         """Create all database tables"""
#         Base.metadata.create_all(bind=self.engine)
#         print("Database tables created successfully!")
        
#     def get_session(self) -> Session:
#         """Get database session"""
#         return self.SessionLocal()
        
#     def close_session(self, session: Session):
#         """Close database session"""
#         session.close()
        
#     def backup_database(self, backup_path: str = None):
#         """Create database backup"""
#         if not backup_path:
#             from datetime import datetime
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             backup_path = f"backup_construction_pos_{timestamp}.db"
            
#         # Simple file copy for SQLite
#         import shutil
#         shutil.copy2("construction_pos.db", backup_path)
#         return backup_path

# # Global database manager instance
# db_manager = DatabaseManager()

# # Dependency for getting database session
# def get_db():
#     db = db_manager.get_session()
#     try:
#         yield db
#     finally:
#         db.close()

# # Initialize database
# def init_database():
#     """Initialize database with tables and default data"""
#     db_manager.create_tables()
    
#     # Add default settings
#     session = db_manager.get_session()
#     try:
#         from .models import Setting
        
#         default_settings = [
#             {"key": "shop_name", "value": "Construction Materials Shop", "description": "Shop name"},
#             {"key": "shop_address", "value": "123 Main Street", "description": "Shop address"},
#             {"key": "shop_phone", "value": "+1234567890", "description": "Shop phone"},
#             {"key": "tax_rate", "value": "18.0", "description": "Tax rate percentage"},
#             {"key": "currency", "value": "FCFA", "description": "Currency symbol"},
#             {"key": "receipt_footer", "value": "Thank you for your business!", "description": "Receipt footer text"}
#         ]
        
#         for setting_data in default_settings:
#             existing = session.query(Setting).filter(Setting.key == setting_data["key"]).first()
#             if not existing:
#                 setting = Setting(**setting_data)
#                 session.add(setting)
        
#         session.commit()
#         print("Default settings added!")
        
#     except Exception as e:
#         session.rollback()
#         print(f"Error adding default settings: {e}")
#     finally:
#         session.close()

# # Database utility functions
# class DatabaseUtils:
#     @staticmethod
#     def get_setting_value(key: str, default: str = None) -> str:
#         """Get setting value by key"""
#         session = db_manager.get_session()
#         try:
#             from .models import Setting
#             setting = session.query(Setting).filter(Setting.key == key).first()
#             return setting.value if setting else default
#         finally:
#             session.close()
    
#     @staticmethod
#     def update_setting(key: str, value: str):
#         """Update setting value"""
#         session = db_manager.get_session()
#         try:
#             from .models import Setting
#             setting = session.query(Setting).filter(Setting.key == key).first()
#             if setting:
#                 setting.value = value
#                 session.commit()
#         finally:
#             session.close()
    
#     @staticmethod
#     def generate_sale_number() -> str:
#         """Generate unique sale number"""
#         session = db_manager.get_session()
#         try:
#             from .models import Sale
#             from datetime import datetime
            
#             today = datetime.now().strftime("%Y%m%d")
#             last_sale = session.query(Sale).filter(
#                 Sale.sale_number.like(f"POS{today}%")
#             ).order_by(Sale.id.desc()).first()
            
#             if last_sale:
#                 last_number = int(last_sale.sale_number[-4:])
#                 new_number = last_number + 1
#             else:
#                 new_number = 1
                
#             return f"POS{today}{new_number:04d}"
#         finally:
#             session.close()

# # Initialize on import
# if __name__ == "__main__":
#     init_database()

# database/database.py - ROBUST VERSION for Desktop App
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base
import os
import sys
import tempfile

# Get the correct application directory for both development and compiled versions
def get_app_dir():
    """Get the application directory, works for both script and compiled exe"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = os.path.dirname(sys.executable)
    else:
        # Running as script - go up one level from database folder
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Ensure the directory is writable
    if not os.access(app_dir, os.W_OK):
        # If app directory is not writable, use user's temp directory
        app_dir = tempfile.gettempdir()
        print(f"Warning: Using temp directory for database: {app_dir}")
    
    return app_dir

# Database configuration with proper path handling and error recovery
def get_database_path():
    """Get database path with fallback options"""
    app_dir = get_app_dir()
    
    # Try different database locations in order of preference
    db_locations = [
        os.path.join(app_dir, "construction_pos.db"),
        os.path.join(os.path.expanduser("~"), "construction_pos.db"),
        os.path.join(tempfile.gettempdir(), "construction_pos.db"),
        ":memory:"  # Last resort - in-memory database
    ]
    
    for db_path in db_locations[:-1]:  # Skip memory DB for now
        try:
            # Test if we can create/write to this location
            test_file = db_path + ".test"
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print(f"Using database location: {db_path}")
            return db_path
        except (PermissionError, OSError) as e:
            print(f"Cannot use {db_path}: {e}")
            continue
    
    # If all file locations fail, use in-memory database
    print("Warning: Using in-memory database (data will not persist)")
    return ":memory:"

# Get database path
db_path = get_database_path()
DATABASE_URL = f"sqlite:///{db_path}"

print(f"Database URL: {DATABASE_URL}")

# Create engine with robust error handling
try:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False  # Set to True for debugging
    )
    # Test the connection
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    print("✅ Database engine created successfully")
except Exception as e:
    print(f"❌ Failed to create database engine: {e}")
    # Create a fallback in-memory database
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    print("✅ Using fallback in-memory database")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DatabaseManager:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        self._initialized = False
        
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            print("✅ Database tables created successfully!")
            self._initialized = True
            return True
        except Exception as e:
            print(f"❌ Failed to create tables: {e}")
            return False
        
    def get_session(self) -> Session:
        """Get database session"""
        try:
            return self.SessionLocal()
        except Exception as e:
            print(f"❌ Failed to create session: {e}")
            return None
        
    def close_session(self, session: Session):
        """Close database session safely"""
        try:
            if session:
                session.close()
        except Exception as e:
            print(f"Warning: Error closing session: {e}")
        
    def backup_database(self, backup_path: str = None):
        """Create database backup"""
        try:
            if db_path == ":memory:":
                raise Exception("Cannot backup in-memory database")
                
            if not backup_path:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                app_dir = get_app_dir()
                backup_path = os.path.join(app_dir, f"backup_construction_pos_{timestamp}.db")
                
            # Simple file copy for SQLite
            import shutil
            if os.path.exists(db_path):
                shutil.copy2(db_path, backup_path)
                return backup_path
            else:
                raise FileNotFoundError("Database file not found")
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            raise
    
    def is_initialized(self):
        """Check if database is properly initialized"""
        return self._initialized

# Global database manager instance
db_manager = DatabaseManager()

# Dependency for getting database session
def get_db():
    db = db_manager.get_session()
    if db is None:
        raise Exception("Failed to create database session")
    try:
        yield db
    finally:
        db_manager.close_session(db)

# Initialize database with comprehensive error handling
def init_database():
    """Initialize database with tables and default data"""
    print("🔄 Initializing database...")
    
    try:
        # Step 1: Create tables
        if not db_manager.create_tables():
            raise Exception("Failed to create database tables")
        
        # Step 2: Add default settings
        session = db_manager.get_session()
        if session is None:
            raise Exception("Failed to create database session")
        
        try:
            from .models import Setting
            
            default_settings = [
                {"key": "shop_name", "value": "Construction Materials Shop", "description": "Shop name"},
                {"key": "shop_address", "value": "123 Main Street", "description": "Shop address"},
                {"key": "shop_phone", "value": "+1234567890", "description": "Shop phone"},
                {"key": "tax_rate", "value": "18.0", "description": "Tax rate percentage"},
                {"key": "currency", "value": "FCFA", "description": "Currency symbol"},
                {"key": "receipt_footer", "value": "Thank you for your business!", "description": "Receipt footer text"}
            ]
            
            settings_added = 0
            for setting_data in default_settings:
                try:
                    existing = session.query(Setting).filter(Setting.key == setting_data["key"]).first()
                    if not existing:
                        setting = Setting(**setting_data)
                        session.add(setting)
                        settings_added += 1
                except Exception as e:
                    print(f"⚠️  Warning: Failed to add setting {setting_data['key']}: {e}")
            
            if settings_added > 0:
                session.commit()
                print(f"✅ Added {settings_added} default settings")
            else:
                print("✅ Default settings already exist")
                
        except Exception as e:
            session.rollback()
            print(f"⚠️  Warning: Error adding default settings: {e}")
        finally:
            db_manager.close_session(session)
        
        print("✅ Database initialization completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("⚠️  The application will continue with limited functionality")
        return False

# Database utility functions with error handling
class DatabaseUtils:
    @staticmethod
    def get_setting_value(key: str, default: str = None) -> str:
        """Get setting value by key"""
        try:
            session = db_manager.get_session()
            if session is None:
                return default
                
            try:
                from .models import Setting
                setting = session.query(Setting).filter(Setting.key == key).first()
                return setting.value if setting else default
            except Exception as e:
                print(f"⚠️  Error getting setting {key}: {e}")
                return default
            finally:
                db_manager.close_session(session)
        except Exception as e:
            print(f"⚠️  Database error getting setting {key}: {e}")
            return default
    
    @staticmethod
    def update_setting(key: str, value: str):
        """Update setting value"""
        try:
            session = db_manager.get_session()
            if session is None:
                return False
                
            try:
                from .models import Setting
                setting = session.query(Setting).filter(Setting.key == key).first()
                if setting:
                    setting.value = value
                    session.commit()
                    return True
                return False
            except Exception as e:
                session.rollback()
                print(f"⚠️  Error updating setting {key}: {e}")
                return False
            finally:
                db_manager.close_session(session)
        except Exception as e:
            print(f"⚠️  Database error updating setting {key}: {e}")
            return False
    
    @staticmethod
    def generate_sale_number() -> str:
        """Generate unique sale number"""
        try:
            session = db_manager.get_session()
            if session is None:
                raise Exception("No database session")
                
            try:
                from .models import Sale
                from datetime import datetime
                
                today = datetime.now().strftime("%Y%m%d")
                last_sale = session.query(Sale).filter(
                    Sale.sale_number.like(f"POS{today}%")
                ).order_by(Sale.id.desc()).first()
                
                if last_sale:
                    last_number = int(last_sale.sale_number[-4:])
                    new_number = last_number + 1
                else:
                    new_number = 1
                    
                return f"POS{today}{new_number:04d}"
                
            finally:
                db_manager.close_session(session)
                
        except Exception as e:
            print(f"⚠️  Error generating sale number: {e}")
            # Return a fallback sale number
            from datetime import datetime
            import random
            return f"POS{datetime.now().strftime('%Y%m%d')}{random.randint(1, 9999):04d}"

    @staticmethod
    def test_database_connection():
        """Test if database is working properly"""
        try:
            session = db_manager.get_session()
            if session is None:
                return False, "Failed to create session"
                
            try:
                # Try to execute a simple query
                result = session.execute("SELECT 1").fetchone()
                if result and result[0] == 1:
                    return True, "Database connection successful"
                else:
                    return False, "Database query failed"
            finally:
                db_manager.close_session(session)
                
        except Exception as e:
            return False, f"Database test failed: {e}"

# Don't initialize automatically - let main.py control this
if __name__ == "__main__":
    try:
        success = init_database()
        if success:
            print("✅ Database initialization test successful")
        else:
            print("❌ Database initialization test failed")
    except Exception as e:
        print(f"❌ Critical database error: {e}")