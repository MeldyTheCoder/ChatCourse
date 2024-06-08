import flet as ft
from typing import Any


class Message:
    def __init__(self, user: str, text: str, message_type: str):
        self.user = user
        self.text = text
        self.message_type = message_type


class ChatMessage(ft.UserControl):
    def __init__(self, message: Message, on_delete: Any = None, from_self: bool = True):
        super().__init__()
        self.message = message
        self.on_delete = on_delete
        self.from_self = from_self
        self.controls = [
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.CircleAvatar(
                            content=ft.Text(self.get_initials(message.user)),
                            color=ft.colors.WHITE,
                            bgcolor=self.get_avatar_color(message.user),
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    message.user,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    message.text,
                                ),
                            ],
                            tight=True,
                            spacing=5,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                on_hover=on_delete,
            )

        ]

    def handle_message_delete(self, _):
        if self.from_self and self.on_delete:
            print(self.message.text)
            return self.on_delete(self.message.text)

    def get_initials(self, user: str):
        return user[:1].capitalize()

    def get_avatar_color(self, user: str):
        colors_lookup = [
            ft.colors.AMBER,
            ft.colors.BLUE,
            ft.colors.BROWN,
            ft.colors.CYAN,
            ft.colors.GREEN,
            ft.colors.INDIGO,
            ft.colors.LIME,
            ft.colors.ORANGE,
            ft.colors.PINK,
            ft.colors.PURPLE,
            ft.colors.RED,
            ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user) % len(colors_lookup)]



