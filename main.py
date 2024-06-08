import flet as ft
import api
import auth
from controls.signin_form import SignInForm
from controls.signup_form import SignUpForm
from controls.chat import Chat
from controls.chat_list import ChatListDrawer
from controls.create_chat_modal import CreateChatModal

api_controller = api.ApiController()
ws_controller = api.SocketControl()


def main(page: ft.Page):
    page.title = "Chat Flet Messenger"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    @ws_controller.sio.on('messageDeleted')
    def handle_message_deleted(data):
        message_id, user = (
            data['message']['id'],
            data['user']
        )

        return open_dlg(
            message=f'{user.username} удалил сообщение!',
            type='success',
        )

    @ws_controller.sio.on('personJoined')
    def handleParticipantJoined(data):
        user, chat = (
            data['user'],
            data['chat'],
        )

    def open_drawer(_):
        def on_chat_click(chat_id: int):
            return chat_view(chat_id)

        def on_chat_remove(chat_id: int):
            ws_controller.connect(wait=True)
            ws_controller.leave_chat(chat_id)

        def on_chat_create():
            return create_chat_view()

        def on_load_chats():
            ws_controller.connect(wait=True)
            ws_controller.request_fetch()

        drawer = ChatListDrawer(
            on_chat_click=on_chat_click,
            on_chat_create=on_chat_create,
            on_chat_delete=on_chat_remove,
            on_load_chats=on_load_chats,
        )

        @ws_controller.sio.on('fetched')
        def handle_fetched_chats(data):
            drawer.chats = data['chats']

        page.drawer = drawer
        page.drawer.open = True
        page.update()

    def open_dlg(message: str, type: str = 'success'):
        icon = ft.icons.CHECK_CIRCLE_OUTLINED if type == 'success' else ft.icons.ERROR_OUTLINED
        icon_color = ft.colors.GREEN if type == 'success' else ft.colors.RED

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Container(
                content=ft.Icon(
                    name=icon, color=icon_color, size=100
                ),
                width=120,
                height=120,
            ),
            content=ft.Text(
                value=message,
                text_align=ft.TextAlign.CENTER,
            ),
            actions=[
                ft.ElevatedButton(
                    text="Продолжить", color=ft.colors.WHITE, on_click=close_dlg
                )
            ],
            actions_alignment="center",
            on_dismiss=None,
        )

        page.dialog = dlg
        dlg.open = True
        page.update()

    def close_dlg(_):
        page.dialog.open = False
        page.route = "/"
        page.update()

    def create_chat_view(_=None):
        page.title = 'Создание чата'

        def on_chat_create(name: str, users_list: list[int]):
            data, is_created, error_creating = api_controller.create_chat(
                name,
                None,
                True,
                users_list,
            )
            if not is_created:
                return open_dlg(
                    error_creating,
                    type='error',
                )

            ws_controller.connect(wait=True)
            ws_controller.request_fetch()

        users, is_success, error = api_controller.get_users()
        page.dialog = CreateChatModal(
            on_create=on_chat_create,
            users=users if is_success else [],
            selected_users=[],
        )
        page.dialog.open = True
        page.update()
        return

    def chat_view(chat_id: int = None):
        page.title = 'Чат'
        is_authenticated, _, user, = auth.get_auth_credentials()
        chat_widget = None

        is_connected, _ = ws_controller.connect()

        if not is_authenticated:
            page.route = '/'
            open_dlg('Вы не авторизованы.', type='error')
            return page.update()

        if not chat_id:
            page.clean()
            page.add(
                chat_widget := Chat(
                    user=user,
                    chat=None,
                    on_chat_menu_open=open_drawer,
                    on_create_chat=create_chat_view,
                )
            )
            return page.update()

        chat, is_success, error = api_controller.get_chat(chat_id)
        if not is_success:
            page.route = '/'
            page.update()
            return open_dlg(error, type='error')

        @ws_controller.sio.on('messageSent')
        def handle_message_sent(data):
            text, user, message_type, chat_to = (
                data['message']['message'],
                data['from_user'],
                data['message']['type'],
                data['chat']
            )

            chat_widget and chat_widget.chat.get('id') == chat_to.get('id') and chat_widget.add_message_interface(
                text=text,
                user=user,
                message_type=message_type,
            )

        @ws_controller.sio.on('chatFetched')
        def handle_chat_fetched(data):
            user, messages, chat_to = (
                data['user'],
                data['messages'],
                data['chat'],
            )

            chat_widget and chat_widget.chat.get('id') == chat_to.get('id') and chat_widget.set_for_chat(
                chat=chat_to,
                messages=messages,
            )

        def on_message_send(**kwargs):
            return ws_controller.send_message(
                message_text=kwargs.get('message'),
                chat_id=chat_id
            )

        if is_connected:
            ws_controller.chat_fetch(chat_id)

        page.drawer.open = False
        page.clean()
        page.add(
            chat_widget := Chat(
                user=user,
                chat=chat,
                on_message_send=on_message_send,
                on_chat_menu_open=open_drawer,
                on_create_chat=create_chat_view,
            )
        )
        page.update()

    def sign_in(user: str, password: str):
        response_data, is_success, error = api_controller.authorize(
            username=user,
            password=password,
        )

        if not is_success:
            return open_dlg(f'Ошибка авторизации: {error}', type='error')

        page.route = "/chat"
        return page.update()

    def sign_up(username: str, password: str):
        data, is_success, error = api_controller.registration(
            username=username,
            password=password,
            first_name='Кирилл',
            last_name='Грошелев',
        )
        if is_success:
            return open_dlg('Ура, вы успешно зарегистрировались. Теперь выполните вход в аккаунт.')

        open_dlg(f'Ошибка регистрации. {error}', type='error')

    def btn_signin(e):
        page.route = "/"
        page.update()

    def btn_signup(e):
        page.route = "/signup"
        page.update()

    principal_content = ft.Column(
        [
            ft.Icon(ft.icons.WECHAT, size=200, color=ft.colors.BLUE),
            ft.Text(value="Chat Flet Messenger", size=50, color=ft.colors.WHITE),
        ],
        height=400,
        width=600,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    signin_UI = SignInForm(sign_in, btn_signup)
    signup_UI = SignUpForm(sign_up, btn_signin)

    def route_change(route):
        if page.route == "/":
            authorized, _, user = auth.get_auth_credentials()
            if authorized:
                page.route = '/chat'
                return page.update()

            ws_controller.disconnect()
            page.clean()
            page.add(
                ft.Row(
                    [principal_content, signin_UI],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )

        if page.route == "/signup":
            ws_controller.disconnect()
            page.clean()
            page.add(
                ft.Row(
                    [principal_content, signup_UI],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )

        elif page.route == '/chat':
            chat_view()

    page.on_route_change = route_change
    page.add(
        ft.Row([principal_content, signin_UI], alignment=ft.MainAxisAlignment.CENTER)
    )


ft.app(target=main)
