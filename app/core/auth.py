from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.exc import SQLAlchemyError
from starlette.status import HTTP_401_UNAUTHORIZED

from app.core.logger import log_error
from app.core.security import SECRET_KEY, ALGORITHM
from app.db import crud
from app.db.base import AsyncSessionLocal
from app.schemas.token import TokenData

# Initialize OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Validate the access token and return the current user.

    This function is used as a dependency to protect routes that require authentication.
    It decodes the JWT token, extracts the username, and fetches the corresponding user from the database.

    Args:
        token (str): The JWT token provided in the request header.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: If the token is invalid or the user doesn't exist.
    """
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        log_error(f"JWT decoding error: {str(e)}")
        raise credentials_exception

    try:
        async with AsyncSessionLocal() as db:
            user = await crud.get_user(db, username=token_data.username)
            if user is None:
                log_error(f"User not found: {token_data.username}")
                raise credentials_exception
            return user
    except SQLAlchemyError as e:
        log_error(f"Database error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An error occurred while authenticating the user"
        )


async def get_optional_user(token: str = Depends(oauth2_scheme)):
    """
    Similar to get_current_user, but returns None if the token is invalid
    instead of raising an exception. This can be used for endpoints that
    have optional authentication.
    """
    try:
        return await get_current_user(token)
    except HTTPException:
        return None
