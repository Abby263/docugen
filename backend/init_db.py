"""
Initialize database with all tables
Run this script to create all database tables
"""

from backend.database import Base, engine

def init_database():
    """Create all database tables"""
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    init_database()

