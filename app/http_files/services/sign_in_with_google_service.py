import requests

from app.exceptions.app_exception import AppException
from app.models.user_model import User


def sign_in(access_token: str) -> 'User':
    response = requests.get(
        'https://www.googleapis.com/userinfo/v2/me',
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=10
    )

    if response.status_code != 200:
        raise AppException('Unsuccessful request to Google API.')

    google_user = response.json()

    user = User.find_or_create({"email": google_user['email']})
    user = user.update({"google_access_token": access_token})

    return user
