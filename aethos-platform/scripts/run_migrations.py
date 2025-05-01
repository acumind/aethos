#!/usr/bin/env python
"""
Script to run database migrations using SQLAlchemy.

This script creates all tables defined in app/db/models.py.
"""

from app.db.models import User, Agent, Task, Document
from app.db.database import engine, Base
from sqlalchemy import inspect, text
import os
import sys
import argparse
import logging

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_connection():
    """Check database connection."""
    try:
        # Try a simple query
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False


def create_tables():
    """Create all tables defined in models."""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        sys.exit(1)


def get_tables():
    """Get list of existing tables."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return tables


def main():
    """Main entry point for script."""
    parser = argparse.ArgumentParser(description="Run database migrations")
    parser.add_argument("--check", action="store_true",
                        help="Check database connection only")
    parser.add_argument("--list", action="store_true",
                        help="List existing tables")

    args = parser.parse_args()

    if args.check:
        check_connection()
        sys.exit(0)

    if args.list:
        if check_connection():
            tables = get_tables()
            if tables:
                logger.info("Existing tables:")
                for table in tables:
                    logger.info(f"  - {table}")
            else:
                logger.info("No tables found in database")
        sys.exit(0)

    # Check database connection
    if not check_connection():
        logger.error("Database connection check failed. Aborting.")
        sys.exit(1)

    # Create tables
    create_tables()

    # List created tables
    tables = get_tables()
    logger.info("Tables in database:")
    for table in tables:
        logger.info(f"  - {table}")


if __name__ == "__main__":
    main()
