import fastapi
import uvicorn
import socket_
from routes import users, chats
from models import database
import auth as auth_tools
import models


app = fastapi.FastAPI(
    debug=True,
    title='Messanger Backend',
)

sio = socket_.get_sio_for_app(app)


async def is_authorized(sid: str, auth: dict = None):
    if not auth:
        user_data = await sio.get_session(sid)
        if not user_data:
            raise ConnectionRefusedError(
                'Пользователь не авторизован!'
            )
        return user_data

    try:
        user = await auth_tools.get_current_user(auth.get('token', None))
        if not user:
            raise ConnectionRefusedError(
                'Пользователь не авторизован'
            )
    except Exception as exception:
        raise ConnectionRefusedError(
            str(exception)
        )

    await sio.save_session(sid=sid, session=user)
    return user


@sio.on('connect')
async def handle_user_connect(sid: str, _, auth: dict):
    user_authorized = await is_authorized(sid, auth)
    chats = user_authorized.chats

    for chat in chats:
        await sio.enter_room(sid, chat.id)

    return {
        'user': user_authorized,
        'authorized': bool(user_authorized),
        'chats': chats,
    }


@sio.on('createChat')
async def handle_create_chat(sid: str, data: dict):
    """
    name,  participants
    """

    user_authorized = await is_authorized(sid)

    chat = await models.Chat.objects.create(
        name=data.get('name')
    )

    await sio.enter_room(sid, chat.id)

    return await sio.emit(
        event='chatCreated',
        data=dict(
            chat=chat,
            user=user_authorized
        ),
        room=chat.id
    )


@sio.on('sendMessage')
async def handle_message_sent(sid: str, data: dict):
    """
    chat_id, text, attachment,
    """

    user_authorized = await is_authorized(sid)
    chat = await models.Chat.objects.get_or_none(
        id=data.get('chat_id')
    )

    if not chat:
        raise Exception('Чат не найден!')

    if user_authorized not in (await chat.participants.all()):
        raise Exception('Вы не находитесь в данном чате!')

    await sio.enter_room(sid, chat.id)

    message_text = data.get('text')
    message = await models.Message.objects.create(
        chat=chat,
        message=message_text,
        from_user=user_authorized,
    )

    return await sio.emit(
        event='messageSent',
        data={
            'message': message.model_dump(
                include={'id', 'from_user__username', 'message', 'type'}
            ),
            'chat': chat.model_dump(
                include={'id', 'name', 'is_user'}
            ),
            'from_user': user_authorized.model_dump(
                include={'id', 'username'}
            )
        },
        room=chat.id,
    )


@sio.on('fetchChat')
async def handle_fetch_chat(sid, data):
    """
    chat_id,
    """

    user_authorized = await is_authorized(sid)
    chat = await models.Chat.objects.get_or_none(
        id=data.get('chat_id')
    )

    if not chat:
        raise Exception('Чат не найден.')

    if user_authorized not in (await chat.participants.all()):
        raise Exception('Вы не находитесь в данном чате.')

    await sio.enter_room(sid, chat.id)

    await sio.emit(
        event='chatFetched',
        data={
            'chat': chat.model_dump(include={'id', 'name'}),
            'messages': [
                message.model_dump(
                    exclude={'chat', 'from_user__date_joined', 'from_user__date_password_changed', 'date_created'}
                )
                for message in (await chat.messages.select_related('from_user').all())
            ],
            'user': user_authorized.model_dump(include={'id', 'username'}),
        },
        to=sid
    )


@sio.on('joinChat')
async def handle_person_joined(sid, data):
    """
    chat_id,
    """

    user_authorized = await is_authorized(sid)
    chat = models.Chat.objects.get_or_none(
        id=data.get('chat_id')
    )

    if not chat:
        raise Exception('Чат не найден.')

    if user_authorized in await chat.participants.all():
        raise Exception('Вы уже находитесь в чате.')

    await sio.enter_room(sid, chat.id)
    await sio.emit(
        event='personJoined',
        data={
            'chat': chat,
            'messages': chat.messages,
            'user': user_authorized,
        },
        room=chat.id,
    )


@sio.on('leaveChat')
async def handle_person_left(sid, data):
    """
    chat_id,
    """

    user_authorized = await is_authorized(sid)
    chat = await models.Chat.objects.get_or_none(
        id=data.get('chat_id')
    )

    if not chat:
        raise Exception('Чат не найден.')

    if user_authorized not in (await chat.participants.all()):
        raise Exception('Вы не находитесь в данном чате.')

    await chat.participants.remove(user_authorized)

    await sio.leave_room(sid, chat.id)
    await sio.emit(
        event='personLeft',
        data={
            'chat': chat.model_dump(
                include={
                    'id', 'name'
                }
            ),
            'user': user_authorized.model_dump(
                include={
                    'id', 'username', 'first_name', 'last_name',
                }
            ),
        },
        room=chat.id,
    )

    await handle_user_fetch(sid)


@sio.on('fetch')
async def handle_user_fetch(sid):
    user_authorized = await is_authorized(sid)

    chats_users = await user_authorized.chats.all()

    return await sio.emit(
        event='fetched',
        data=dict(
            user=user_authorized.model_dump(
                include={
                    'id', 'username', 'first_name', 'last_name',
                }
            ),
            chats=[chat.model_dump(
                include={
                    'id', 'name'
                }
            ) for chat in chats_users],
        ),
        to=sid,
    )


@sio.on('deleteMessage')
async def handle_message_deleted(sid, data):
    """
    chat_id, message_id,
    """

    user_authorized = await is_authorized(sid)
    chat = models.Chat.objects.get_or_none(
        id=data.get('chat_id')
    )
    message = models.Message.objects.get_or_none(
        id=data.get('message_id'),
        chat=chat,
    )

    if not chat:
        raise Exception('Чат не найден!')

    if not message:
        raise Exception('Сообщение не найдено!')

    if user_authorized not in chat.participants:
        raise Exception('Вы не являетесь участником чата.')

    if message.from_user.id != user_authorized.id:
        raise Exception('Вы не можете удалить чужое сообщение.')

    await message.delete()

    return await sio.emit(
        event='chatFetched',
        data={
            'chat': chat.model_dump(include={'id', 'name'}),
            'messages': [
                message.model_dump(
                    exclude={'chat', 'from_user__date_joined', 'from_user__date_password_changed', 'date_created'}
                )
                for message in (await chat.messages.select_related('from_user').all())
            ],
            'user': user_authorized.model_dump(include={'id', 'username'}),
        },
        room=chat.id,
    )


@app.get('/media/')
async def get_media():
    return None


@app.on_event('startup')
async def on_startup():
    await database.connect()


@app.on_event('shutdown')
async def on_shutdown():
    if database.is_connected:
        await database.disconnect()

app.include_router(
    users.router,
)

app.include_router(
    chats.router,
)

if __name__ == '__main__':
    uvicorn.run(
        host='0.0.0.0',
        port=8000,
        app=app,
    )