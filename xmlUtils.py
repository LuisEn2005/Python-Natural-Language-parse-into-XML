import random
import string

def generate_open_roberta_id(length=20):
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:',.<>?/"
    return ''.join(random.choice(characters) for _ in range(length))