import json
import os


def authenticate(token: str, user_data: dict):
    os.environ['token'] = token
    os.environ['user'] = json.dumps(user_data)
    return token


def logout():
    token_deleted = os.environ.pop('token', None)
    return bool(token_deleted)


def get_auth_credentials():
    token = os.environ.get('token')
    user = json.loads(os.environ.get('user')) if os.environ.get('user') else None
    return bool(token), token, user


def is_authenticated():
    token = os.environ.get('token')
    return bool(token)
