import asyncio
import os

from sqlalchemy.exc import IntegrityError

from app.db import crud
from app.db.base import AsyncSessionLocal
from app.schemas.user import UserCreate


async def create_initial_user():
    """
    Asynchronous function to create an initial admin user in the database.
    It uses environment variables for the username and password.
    """
    async with AsyncSessionLocal() as session:
        try:
            # Retrieve username and password from environment variables
            username = os.getenv("INITIAL_ADMIN_USERNAME", "admin")
            password = os.getenv("INITIAL_ADMIN_PASSWORD")

            # Check if password is set
            if not password:
                print("Error: INITIAL_ADMIN_PASSWORD environment variable is not set.")
                return

            # Create user object and add to database
            user = UserCreate(username=username, password=password)
            db_user = await crud.create_user(session, user)
            await session.commit()
            print(f"User created: {db_user.username}")

        except IntegrityError:
            # Handle case where user already exists
            await session.rollback()
            print(f"User {username} already exists.")

        except Exception as e:
            # Handle any other exceptions
            await session.rollback()
            print(f"Error creating user: {str(e)}")


def main():
    """
    Main function to run the create_initial_user function using asyncio.
    """
    asyncio.run(create_initial_user())


if __name__ == "__main__":
    main()
