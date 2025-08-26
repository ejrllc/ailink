# Import the engine and Base from your database setup
from ailink_at.db.database import engine, Base

# Import your models so that Base knows about them
from ailink_at.db.models import User

def main():
    """
    A simple script to create the database tables.
    """
    print("Creating database tables...")
    
    # This line reads all the models that inherit from Base
    # and creates the corresponding tables in the database.
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully!")

if __name__ == "__main__":
    main()