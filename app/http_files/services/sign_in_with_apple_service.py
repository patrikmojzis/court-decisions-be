import logging
import os
import time
from datetime import datetime

import jwt
import jwt.algorithms
import requests

from app.exceptions.app_exception import AppException
from app.models.user_model import User
from app.utils.cache import Cache


def sign_in(identity_token: str) -> 'User':
    try:
        response = requests.get('https://appleid.apple.com/auth/keys')
        if response.status_code != 200:
            logging.error('Could not communicate with Apple server.')
            raise AppException('Could not communicate with Apple server.')

        keys = response.json()
        Cache.set('apple_auth_keys', keys, 1440)
    except Exception as e:
        if not Cache.exists('apple_auth_keys'):
            raise e
        keys = Cache.get('apple_auth_keys')

    try:
        for key in keys['keys']:
            if key['kid'] == jwt.get_unverified_header(identity_token)['kid']:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                break
        else:
            raise AppException('Public key not found.')

        jwt_decoded = jwt.decode(identity_token, public_key, algorithms=['RS256'], audience=os.getenv("APPLE_CLIENT_ID"))
    except jwt.exceptions.InvalidSignatureError:
        raise AppException('Key invalid.')

    expired_date = datetime.fromtimestamp(jwt_decoded['exp'])
    if expired_date < datetime.now():
        raise AppException('Key expired.')

    # logging.info(jwt_decoded['email'])

    user = User.find_or_create({'email': jwt_decoded['email']})
    user.update({"apple_auth_token": jwt_decoded['sub']})

    return user


def revoke(self, authorisation_code: str) -> None:
    logging.info(authorisation_code)

    token_request = requests.post('https://appleid.apple.com/auth/token', data={
        'client_id': os.getenv("APPLE_CLIENT_ID"),
        'client_secret': self.generate_jwt(),
        'code': authorisation_code,
        'grant_type': 'authorization_code',
    })

    if token_request.status_code != 200:
        logging.error(token_request.text)
        raise AppException('Could not revoke Apple access token.')

    # logging.info(token_request.text)

    token_response = token_request.json()

    revoke_request = requests.post('https://appleid.apple.com/auth/revoke', data={
        'client_id': os.getenv("APPLE_CLIENT_ID"),
        'client_secret': self.generate_jwt(),
        'token': token_response['access_token'],
        'token_type_hint': 'access_token'
    })

    if revoke_request.status_code != 200:
        logging.error(revoke_request.text)
        raise AppException('Could not revoke Apple access token.')

    # logging.info(revoke_request.text)


def generate_jwt(self) -> str:
    payload = {
        'iss': os.getenv("APPLE_TEAM_ID"),
        'iat': int(time.time()) - 10,
        'exp': int(time.time()) + 120,
        'aud': 'https://appleid.apple.com',
        'sub': os.getenv("APPLE_CLIENT_ID")
    }

    with open(os.getenv("PATH_TO_P8_FILE"), 'r') as f:
        private_key = f.read()

    return jwt.encode(
        payload,
        private_key,
        algorithm='ES256',
        headers={'kid': os.getenv("APPLE_KEY_ID")}
    )
