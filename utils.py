from app import bcrypt

# Function to hash a password
def hash_password(password: str) -> str:
    """
    Hashes the provided password using bcrypt.

    Parameters:
    password (str): The plain text password to hash.

    Returns:
    str: The hashed password as a UTF-8 encoded string.
    """
    # Generate a bcrypt hash of the password and decode it to UTF-8 string
    return bcrypt.generate_password_hash(password).decode('utf-8')

# Function to check if a given password matches the hashed password
def check_password(password: str, hashed_password: str) -> bool:
    """
    Checks if the provided password matches the hashed password.

    Parameters:
    password (str): The plain text password to check.
    hashed_password (str): The hashed password to compare against.

    Returns:
    bool: True if the password matches the hashed password, False otherwise.
    """
    # Compare the plain password with the hashed password
    return bcrypt.check_password_hash(hashed_password, password)
