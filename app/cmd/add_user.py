from app.config.config import load_env
from app.models.user_model import User
from app.utils.auth_utils import hash_password

load_env()

if __name__ == '__main__':
    email = input('Email: ')
    password = input('Password: ')
    user = User.create({'email': email, 'password': hash_password(password), 'has_access': True})
    print(user.dict())