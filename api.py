import requests
import socketio
import auth
from socketio import exceptions as socket_exceptions

session = requests.session()

NOT_CONNECTED = Exception('Вы не подключены к сессии.')


class ApiController:
    def __init__(self):
        self.default_headers = lambda: {
            'Authorization': f'Bearer {auth.get_auth_credentials()[1]}'
        }

    @staticmethod
    def authorize(username: str, password: str):
        response = session.post(
            url='http://localhost:8000/users/token/',
            json={
                'username': username,
                'password': password,
            },
            headers=None,
        )
        is_success = response.status_code == 200
        response_data = response.json()
        user = response_data.get('user')
        token = response_data.get('token', {}).get('access_token', None)

        error = response_data.get('detail') if not is_success else None
        authorized, _, _ = auth.get_auth_credentials()

        if response_data and not authorized and is_success:
            auth.authenticate(token, user)

        return user, is_success, error

    @staticmethod
    def registration(username: str, password: str, first_name: str = None, last_name: str = None):
        response = session.post(
            url='http://localhost:8000/users/register/',
            json=dict(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
            ),
            headers=None,
        )
        response_data = response.json()
        is_success = response.status_code == 200
        error = response_data.get('detail') if not is_success else None
        return response_data, is_success, error

    def get_chat(self, chat_id: int):
        response = session.get(
            f'http://localhost:8000/chats/{chat_id}/',
            headers=self.default_headers(),
        )
        response_data = response.json()
        is_success = response.status_code == 200
        error = response_data.get('detail') if not is_success else None
        return response_data, is_success, error

    def get_chats(self):
        headers = self.default_headers()
        response = session.get(
            'http://localhost:8000/chats/',
            headers=headers,
        )
        response_data = response.json()
        is_success = response.status_code == 200
        error = response_data.get('detail') if not is_success else None
        return response_data, is_success, error

    def get_users(self):
        headers = self.default_headers()
        response = session.get(
            'http://localhost:8000/users/',
            headers=headers,
        )
        response_data = response.json()
        is_success = response.status_code == 200
        error = response_data.get('detail') if not is_success else None
        return response_data, is_success, error

    def create_chat(self, name, avatar, is_user=True, users: list[int] = None):
        response = session.post(
            'http://localhost:8000/chats/create/',
            headers=self.default_headers(),
            json=dict(
                name=name,
                is_user=is_user,
                participants=users,
            )
        )
        response_data = response.json()
        is_success = response.status_code == 200
        error = response_data.get('detail') if not is_success else None
        return response_data, is_success, error


class SocketControl:
    client_instance: socketio.Client = socketio.Client()
    backend_host: str = 'ws://localhost:8000'

    def connect(self, wait=False):
        try:
            if not self.client_instance.connected:
                self.client_instance.connect(
                    self.backend_host,
                    namespaces='/',
                    wait=wait,
                    auth=dict(
                        token=auth.get_auth_credentials()[1],
                    ),
                    transports=['polling'],
                    retry=True,
                )
            return self.client_instance.connected, self.client_instance.sid
        except socket_exceptions.ConnectionError as error:
            print(f'[!] Ошибка подключения: {error}')
            return False, None

    def disconnect(self):
        if self.client_instance.connected:
            self.client_instance.disconnect()

        return self.client_instance.connected, self.client_instance.sid

    @property
    def sio(self):
        return self.client_instance

    def join_chat(self, chat_id: int):
        if not self.client_instance.connected:
            self.connect(wait=True)

        return self.client_instance.emit(
            event='joinChat',
            data=dict(
                chat_id=chat_id,
            )
        )

    def delete_chat(self, chat_id: int):
        if not self.client_instance.connected:
            self.connect(wait=True)

        return self.client_instance.emit(
            event='deleteChat',
            data=dict(
                chat_id=chat_id,
            )
        )

    def leave_chat(self, chat_id: int):
        if not self.client_instance.connected:
            self.connect(wait=True)

        return self.client_instance.emit(
            event='leaveChat',
            data=dict(
                chat_id=chat_id,
            )
        )

    def send_message(self, chat_id: int, message_text: str):
        if not self.client_instance.connected:
            raise self.connect(wait=True)

        return self.client_instance.emit(
            event='sendMessage',
            data=dict(
                chat_id=chat_id,
                text=message_text,
            ),
            callback=print
        )

    def delete_message(self, chat_id: int, message_id: int):
        if not self.client_instance.connected:
            self.connect(wait=True)

        return self.client_instance.emit(
            event='deleteMessage',
            data=dict(
                chat_id=chat_id,
                message_id=message_id,
            )
        )

    def request_fetch(self):
        if not self.client_instance.connected:
            self.connect(wait=True)

        return self.client_instance.emit(
            event='fetch',
        )

    def chat_fetch(self, chat_id: int):
        if not self.client_instance.connected:
            self.connect(wait=True)

        return self.client_instance.emit(
            event='fetchChat',
            data=dict(
                chat_id=chat_id,
            )
        )

