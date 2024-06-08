import fastapi

import auth
import models
import serializers

router = fastapi.APIRouter(
    prefix='/chats',
    tags=['Чаты'],
)


CHAT_NOT_FOUND = fastapi.exceptions.HTTPException(
    detail='Запрашиваемый Вами чат не найден.',
    status_code=404,
)


@router.get('/')
async def get_chats(user: auth.UserType):
    return await models.Chat.objects.select_all(False).filter(
        participants__id__contains=user.id,
    ).all()


@router.post('/create/')
async def create_chat(user: auth.UserType, form_data: serializers.ChatCreateSerializer):
    form_data_encoded = form_data.model_dump()
    chat = await models.Chat.objects.create(
        **form_data_encoded
    )
    await chat.participants.add(user)

    for participant in form_data.participants:
        await chat.participants.add(
            await models.User.objects.get(id=participant)
        )
    return chat


@router.get('/{chat_id}/')
async def get_chat(chat_id: int, user: auth.UserType):
    chat = await models.Chat.objects.get_or_none(
        id=chat_id,
        participants__id__contains=user.id,
    )

    if not chat:
        raise CHAT_NOT_FOUND

    return chat

