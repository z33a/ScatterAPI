# External imports
import re

def check_password(password):
    # Check if password is at least 8 characters long
    if len(password) < 8:
        return False
    
    # Check if password contains at least one uppercase letter, one lowercase letter, one digit, and one special symbol
    if not re.search(r'[A-Z]', password):  # At least one uppercase letter
        return False
    if not re.search(r'[a-z]', password):  # At least one lowercase letter
        return False
    if not re.search(r'[0-9]', password):  # At least one number
        return False
    if not re.search(r'[\W_]', password):  # At least one special symbol
        return False

    # If all conditions are met
    return True