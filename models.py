import enum
import databases
import sqlalchemy
import ormar
from pydantic import field_serializer
from sqlalchemy_utils import database_exists, create_database, drop_database
from datetime import datetime

DATABASE_URL = 'mysql://root:1234@localhost:3306/chat'

metadata = sqlalchemy.MetaData()
database = databases.Database(DATABASE_URL)

# drop_database(DATABASE_URL)
if not database_exists(DATABASE_URL):
    create_database(DATABASE_URL)

engine = sqlalchemy.create_engine(DATABASE_URL)

ormar_config = ormar.OrmarConfig(
    metadata=metadata,
    database=database,
)


class MediaType(enum.Enum):
    VIDEO = 'video'
    PHOTO = 'photo'
    AUDIO = 'audio'
    DOCUMENT = 'document'

class MessageTypes(enum.Enum):
    SYSTEM = 'system'
    FROM_USER = 'from_user'
    EVENT = 'event'

class Media(ormar.Model):
    ormar_config = ormar_config.copy(
        tablename='media'
    )

    id = ormar.BigInteger(
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )

    media_url = ormar.Text(
        nullable=False,
    )

    type = ormar.String(
        max_length=10,
        choices=list(MediaType),
        default=MediaType.DOCUMENT,
    )


class User(ormar.Model):
    ormar_config = ormar_config.copy(
        tablename='users'
    )

    id = ormar.BigInteger(
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )

    username = ormar.String(
        unique=True,
        nullable=False,
        min_length=3,
        max_length=20,
    )

    first_name = ormar.String(
        nullable=False,
        min_length=1,
        max_length=20,
    )

    last_name = ormar.String(
        nullable=True,
        min_length=1,
        max_length=20,
    )

    password = ormar.String(
        max_length=256,
        nullable=False,
    )

    date_joined = ormar.DateTime(
        default=datetime.now,
        nullable=False,
    )

    date_password_changed = ormar.DateTime(
        default=datetime.now,
        nullable=False,
    )

    @field_serializer('date_joined')
    def serialize_date_joined(self, value: datetime, _):
        return value.timestamp()

    @field_serializer('date_password_changed')
    def serialize_date_password_changed(self, value: datetime, _):
        return value.timestamp()


class UserPhotos(ormar.Model):
    ormar_config = ormar_config.copy(
        tablename='users_photos'
    )

    id = ormar.BigInteger(
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )

    media = ormar.ForeignKey(
        to=Media,
        ondelete=ormar.ReferentialAction.CASCADE,
        onupdate=ormar.ReferentialAction.CASCADE,
        nullable=False,
    )

    user = ormar.ForeignKey(
        to=User,
        nullable=False,
        ondelete=ormar.ReferentialAction.CASCADE,
        onupdate=ormar.ReferentialAction.CASCADE,
    )


class Chat(ormar.Model):
    ormar_config = ormar_config.copy(
        tablename='chats'
    )

    id = ormar.BigInteger(
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )

    name = ormar.String(
        max_length=30,
        nullable=False,
    )

    participants = ormar.ManyToMany(
        to=User,
        ondelete=ormar.ReferentialAction.CASCADE,
        onupdate=ormar.ReferentialAction.CASCADE,
    )

    date_created = ormar.DateTime(
        default=datetime.now,
        nullable=False,
    )

    avatar = ormar.ForeignKey(
        to=Media,
        ondelete=ormar.ReferentialAction.CASCADE,
        onupdate=ormar.ReferentialAction.CASCADE,
        nullable=True,
    )

    is_user = ormar.Boolean(
        nullable=False,
        default=True,
    )

    @field_serializer('date_created')
    def serialize_date_created(self, value: datetime, _):
        return value.timestamp()


class Attachment(ormar.Model):
    ormar_config = ormar_config.copy(
        tablename='attachments'
    )

    id = ormar.BigInteger(
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )

    media = ormar.ForeignKey(
        to=Media,
        ondelete=ormar.ReferentialAction.CASCADE,
        onupdate=ormar.ReferentialAction.CASCADE,
        nullable=False,
    )

    from_user = ormar.ForeignKey(
        to=User,
        ondelete=ormar.ReferentialAction.CASCADE,
        onupdate=ormar.ReferentialAction.CASCADE,
        nullable=False,
    )


class Message(ormar.Model):
    ormar_config = ormar_config.copy(
        tablename='messages'
    )

    id = ormar.BigInteger(
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )

    from_user = ormar.ForeignKey(
        to=User,
        ondelete=ormar.ReferentialAction.SET_NULL,
        onupdate=ormar.ReferentialAction.CASCADE,
        nullable=True,
    )

    chat = ormar.ForeignKey(
        to=Chat,
        ondelete=ormar.ReferentialAction.CASCADE,
        onupdate=ormar.ReferentialAction.CASCADE,
        nullable=False,
    )

    message = ormar.String(
        max_length=256,
        min_length=1,
        nullable=False,
    )

    attachments = ormar.ManyToMany(
        to=Attachment,
        ondelete=ormar.ReferentialAction.SET_NULL,
        onupdate=ormar.ReferentialAction.CASCADE,
    )

    date_created = ormar.DateTime(
        default=datetime.now,
        nullable=False,
    )

    type = ormar.String(
        max_length=50,
        choices=list(MessageTypes),
        default=MessageTypes.FROM_USER,
    )

    @field_serializer('date_created')
    def serialize_date_created(self, value: datetime, _):
        return value.timestamp()


metadata.create_all(bind=engine)
