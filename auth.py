import asyncio
import typing
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, timezone, datetime
import models
import settings
import jwt
import hmac

SECRET = settings.SECRET_KEY
DIGEST = 'sha256'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_user(username: str):
    return await models.User.objects.get_or_none(username=username)


def create_password_hash(password: str):
    secret = SECRET

    if isinstance(secret, str):
        secret = secret.encode('utf-8')

    if isinstance(password, str):
        password = password.encode('utf-8')

    return hmac.new(secret, password, DIGEST).hexdigest()


def verify_password(plain_password: str, hashed_password: str):
    new_hash = create_password_hash(plain_password)
    return hmac.compare_digest(new_hash, hashed_password)


async def authenticate_user(username: str, password: str):
    user = await get_user(username=username)
    if not user:
        return False

    if not verify_password(password, user.password):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось авторизовать пользователя.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

    except jwt.exceptions.PyJWTError as error:
        raise credentials_exception

    user = await get_user(username=username)
    if user is None:
        raise credentials_exception

    return user


def create_token(user: models.User):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub": user.username}
    access_token = create_access_token(
        data=data, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'Bearer'}


UserType = Annotated[models.User, Depends(get_current_user)]
