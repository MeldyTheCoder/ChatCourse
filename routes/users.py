import fastapi
import serializers
import auth
import models
from auth import authenticate_user, create_token, create_password_hash


router = fastapi.APIRouter(
    prefix='/users',
    tags=['Пользователи']
)

USER_ALREADY_REGISTERED_EXCEPTION = fastapi.HTTPException(
    detail='Данный пользователь уже зарегистрирован!',
    status_code=403,
)

USER_IS_NOT_REGISTERED_EXCEPTION = fastapi.HTTPException(
    detail='Данный пользователь не зарегистрирован',
    status_code=403,
)

INCORRECT_LOGIN_DATA_EXCEPTION = fastapi.HTTPException(
    status_code=fastapi.status.HTTP_400_BAD_REQUEST,
    detail='Неверные данные для входа.'
)

INCORRECT_REGISTRATION_DATA_EXCEPTION = fastapi.HTTPException(
    status_code=fastapi.status.HTTP_400_BAD_REQUEST,
    detail='Неверные данные для регистрации.'
)


async def check_for_username_availability(username: str):
    result_check = await models.User.objects.filter(username=username).exists()
    return bool(result_check)


@router.get('/')
async def get_users(user: auth.UserType):
    return await models.User.objects.exclude(id=user.id).all()


@router.get('/me/', name='Получить авторизованного пользователя')
async def get_me(user: auth.UserType):
    return user


@router.post('/token/', name='Получение токена авторизации')
async def get_token_endpoint(form_data: serializers.UserLoginSerializer):
    """
    Генерирует Bearer-токен для авторизации.
    """

    if not form_data:
        raise INCORRECT_LOGIN_DATA_EXCEPTION

    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise INCORRECT_LOGIN_DATA_EXCEPTION

    return {'user': user, 'token': create_token(user)}


@router.post('/register/', name='Регистрация пользователя')
async def register_user_endpoint(form_data: serializers.UserRegistrationSerializer):
    """
    Регистрирует пользователя в БД.
    """

    if not form_data:
        raise INCORRECT_REGISTRATION_DATA_EXCEPTION

    if await check_for_username_availability(form_data.username):
        raise USER_ALREADY_REGISTERED_EXCEPTION

    password = form_data.password
    password_hash = create_password_hash(password)

    created_user = await models.User.objects.create(
        username=form_data.username,
        password=password_hash,
        first_name=form_data.first_name,
        last_name=form_data.last_name,
    )

    return created_user


@router.post('/registration/username/{username}/', name='Проверка username на регистрацию')
async def validate_registration_email_endpoint(username: str):
    """
    Проверка username на его занятость другим пользователем.
    Данная функция нужна для валидации поля username на клиенте.
    """

    if not await check_for_username_availability(username):
        return {'detail': False}

    return {'detail': True}
