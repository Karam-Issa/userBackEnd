# Basic Configuration for working with a PostgreSQL database using SQLAlchemy in a FastAPI Application


# Provides the core functionality for interacting with databases using SQLAlchemy
import sqlalchemy as _sql

# Provides a base class for declarative class definitions, allowing you to define database models as classes.
import sqlalchemy.ext.declarative as _declarative

# Provides the Object-Relational Mapping (ORM) functionality for working with database objects
import sqlalchemy.orm as _orm

# It includes the username, password, host, and database name.
DATABASE_URL = "postgresql://myuser:password@localhost/users_database"

# Interface to manage the connections and executes SQL statements.
engine = _sql.create_engine(DATABASE_URL)

 # Session Factory -- It takes the database engine as an argument and returns a callable that can create individual session objects.
SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False,bind=engine)


#ny class that subclasses Base will be considered a SQLAlchemy model
Base = _declarative.declarative_base()