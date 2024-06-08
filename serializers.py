import models
import pydantic

UserLoginSerializer = models.User.get_pydantic(
    include={
        'username',
        'password',
    }
)

UserRegistrationSerializer = models.User.get_pydantic(
    include={
        'username',
        'password',
        'first_name',
        'last_name',
    }
)

_ChatCreateSerializer = models.Chat.get_pydantic(
    include={
        'is_user',
        'name',
    }
)


class ChatCreateSerializer(_ChatCreateSerializer):
    participants: list[int]
