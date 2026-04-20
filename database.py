from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This is the address to your database. 
# 'postgresql' is the type, 'localhost' means your Mac.
# 'streakify_db' is the name required by your assignment[cite: 106].
SQLALCHEMY_DATABASE_URL = "postgresql://postgres@localhost/streakify_db"

# The engine is what actually executes the SQL commands
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal is what we use to actually talk to the DB in our code
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is what our database tables will inherit from
Base = declarative_base()

# This function opens a connection, does work, then closes it automatically
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()