import os
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlite3 import connect

from src.helpers import get_settings, Settings
from src.logs import log_error, log_warning, log_info
# Configuration
MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DB_PATH = os.path.join(MAIN_DIR, "database/SQLite/user.db")

app_settings: Settings = get_settings()

SECRET_KEY = app_settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# DB connection
conn = connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

from src.logs import log_error, log_warning, log_info

# Create table
try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL
        );
    """)
    conn.commit()
    log_info("Users table ensured in database.")
except Exception as e:
    log_error(f"Error creating users table: {e}")

def init_default_user():
    try:
        cursor.execute("SELECT * FROM users WHERE user = ?", ("xrami92alRashid",))
        if not cursor.fetchone():
            hashed = pwd_context.hash("1OSud&3vTiN=")
            cursor.execute("INSERT INTO users (user, hashed_password) VALUES (?, ?)", ("xrami92alRashid", hashed))
            conn.commit()
            log_info("Default user created: xrami92alRashid")
        else:
            log_info("Default user already exists.")
    except Exception as e:
        log_error(f"Error initializing default user: {e}")

def verify_password(plain_password, hashed_password):
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        log_info("Password verification attempted.")
        return result
    except Exception as e:
        log_error(f"Password verification failed: {e}")
        return False

def get_user(username: str):
    try:
        cursor.execute("SELECT user, hashed_password FROM users WHERE user = ?", (username,))
        row = cursor.fetchone()
        if row:
            log_info(f"User found in DB: {username}")
            return {"username": row[0], "hashed_password": row[1]}
        log_warning(f"User not found in DB: {username}")
        return None
    except Exception as e:
        log_error(f"Error fetching user {username}: {e}")
        return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        log_warning(f"Authentication failed: user '{username}' not found.")
        return False
    if not verify_password(password, user["hashed_password"]):
        log_warning(f"Authentication failed: incorrect password for '{username}'.")
        return False
    log_info(f"User authenticated: {username}")
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "sub": data["sub"]})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


from fastapi import Request

async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        # Try from cookies if token is not in header
        token = request.cookies.get("access_token")
        if token:
            if token.startswith("Bearer "):
                token = token[len("Bearer "):]
            else:
                log_warning("Token doesn't start with Bearer prefix.")
                raise credentials_exception
        else:
            log_warning("No token found in request headers or cookies.")
            raise credentials_exception
    
    try:
        # Decoding the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            log_warning("JWT token missing 'sub' field.")
            raise credentials_exception
        user = get_user(username)
        if user is None:
            log_warning(f"User {username} not found in DB.")
            raise credentials_exception
        log_info(f"User {username} authenticated successfully.")
        return user
    except JWTError as e:
        log_error(f"JWT decoding error: {e}")
        raise credentials_exception


