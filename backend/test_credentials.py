import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Generate working test passwords
print("Test passwords for database:")
print("="*50)

users_passwords = {
    "admin@eir.com": "password123",
    "john.doe@email.com": "password123", 
    "jane.smith@email.com": "password123",
    "anonymous@temp.com": "password123"
}

# Generate hashes
for email, password in users_passwords.items():
    hashed = hash_password(password)
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Hash: {hashed}")
    print(f"Verification: {verify_password(password, hashed)}")
    print("-" * 30)

# Test a known working hash for "password123"
working_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p02c5kJRmcHW7Wy8C29Rju.O"
print(f"\nTesting known working hash:")
print(f"Testing 'password123' against hash: {verify_password('password123', working_hash)}")
