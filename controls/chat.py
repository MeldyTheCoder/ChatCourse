import flet as ft
from .chat_message import ChatMessage, Message
from typing import Any


class Chat(ft.UserControl):
    def __init__(
            self,
            user,
            chat=None,
            messages=None,
            on_message_send=None,
            on_message_delete=None,
            on_create_chat=None,
            on_chat_menu_open=None,
            *args,
            **kwargs
    ):
        super().__init__(self, *args, **kwargs)
        self.on_message_send = on_message_send
        self.expand = True
        self.spacing = 10
        self.auto_scroll = True

        self.user = user
        self._chat = chat or None
        self.messages = messages or None
        self.on_chat_menu_open = on_chat_menu_open
        self.on_create_chat = on_create_chat
        self.on_message_delete = on_message_delete

        self._chat_list = ft.ListView(
            expand=True,
            spacing=10,
            auto_scroll=True,
        )

        self.emoji_list = ft.Dropdown(
            on_change=self.dropdown_changed,
            options=[
                ft.dropdown.Option("😃"),
                ft.dropdown.Option("😊"),
                ft.dropdown.Option("😂"),
                ft.dropdown.Option("🤔"),
                ft.dropdown.Option("😭"),
                ft.dropdown.Option("😉"),
                ft.dropdown.Option("🤩"),
                ft.dropdown.Option("🥰"),
                ft.dropdown.Option("😎"),
                ft.dropdown.Option("❤️"),
                ft.dropdown.Option("🔥"),
                ft.dropdown.Option("✅"),
                ft.dropdown.Option("✨"),
                ft.dropdown.Option("👍"),
                ft.dropdown.Option("🎉"),
                ft.dropdown.Option("👉"),
                ft.dropdown.Option("⭐"),
                ft.dropdown.Option("☀️"),
                ft.dropdown.Option("👀"),
                ft.dropdown.Option("👇"),
                ft.dropdown.Option("🚀"),
                ft.dropdown.Option("🎂"),
                ft.dropdown.Option("💕"),
                ft.dropdown.Option("🏡"),
                ft.dropdown.Option("🍎"),
                ft.dropdown.Option("🎁"),
                ft.dropdown.Option("💯"),
                ft.dropdown.Option("💤"),
            ],
            width=50,
            value="😃",
            alignment=ft.alignment.center,
            border_color=ft.colors.AMBER,
            color=ft.colors.AMBER,
        )

        self.new_message = ft.TextField(
            hint_text="Ваше сообщение...",
            autofocus=True,
            shift_enter=True,
            min_lines=1,
            max_lines=5,
            filled=True,
            expand=True,
            on_submit=self._send_message_click,
        )

    def _send_message_click(self, _):
        if not self._chat:
            return

        message_text = self.new_message.value
        from_user = self.user
        message_type = 'from_user'

        self.new_message.value = ''
        self.update()

        self.on_message_send and self.on_message_send(
            message=message_text,
            from_user=from_user,
            type=message_type,
            chat=self._chat
        )

    def set_for_chat(self, chat, messages):
        self._chat = chat
        self.messages = messages

        self._chat_list.controls.clear()

        for message in messages:
            self.add_message_interface(
                user=message.get('from_user', {}),
                message_type=message.get('type'),
                text=message.get('message'),
            )

        self.update()

    def add_message_interface(self, text: str, user: Any, message_type: str):
        if not self._chat:
            return

        self._chat_list.controls.append(
            ChatMessage(
                Message(
                    user=user.get('username', 'Аноним'),
                    message_type=message_type,
                    text=text,
                ),
                on_delete=self.on_message_delete,
                from_self=True,
            )
        )

        self.update()

    def add_message(self, text: str, user: Any, message_type: str, send_request: bool = True):
        if not self._chat:
            return

        self.add_message_interface(text, user, message_type)

        self.on_message_send and send_request and self.on_message_send(
            message=text,
            from_user=user,
            type=message_type,
            chat=self._chat
        )

        self.update()

    @property
    def chat(self):
        return self._chat

    @chat.setter
    def chat(self, value: dict):
        self._chat = value
        self.update()

    def dropdown_changed(self, _):
        self.new_message.value = self.new_message.value + self.emoji_list.value
        self.update()

    def build(self):
        content = self._chat_list if self.chat else ft.Row(
            [
                ft.Text('Выберите чат для общения.'),
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        return ft.Column(
            controls=[
                ft.Row(
                    [
                        ft.Badge(
                            content=ft.IconButton(
                                icon=ft.icons.MENU_OPEN,
                                on_click=self.on_chat_menu_open,
                            ),
                            text='10',
                        ),
                        ft.Row(
                            controls=[
                                ft.CircleAvatar(
                                    content=ft.Text(self._chat['name'][0].upper()),
                                    foreground_image_url='',
                                ) if self._chat else ft.Container(),
                                ft.Text(
                                    value=self._chat['name'],
                                    scale=1.2,
                                ) if self._chat else ft.Container(),
                                ft.IconButton(
                                    icon=ft.icons.SETTINGS,
                                    on_click=print,
                                ) if self._chat else ft.Container(),
                            ],
                            spacing=20,
                        ),
                        ft.ElevatedButton(
                            text="Выход",
                            bgcolor=ft.colors.RED_800,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(
                    content=content,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=5,
                    padding=10,
                    expand=True,
                ),
                ft.Row(
                    controls=[
                        self.emoji_list,
                        self.new_message,
                        ft.IconButton(
                            icon=ft.icons.SEND_ROUNDED,
                            tooltip="Отправить сообщение",
                            on_click=self._send_message_click,
                            disabled=not self._chat,
                        ),
                    ],
                )
            ]
        )