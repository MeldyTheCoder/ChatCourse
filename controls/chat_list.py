import flet as ft


class ChatListDrawer(ft.NavigationDrawer):
    def __init__(
            self,
            on_chat_click=None,
            on_chat_delete=None,
            on_chat_create=None,
            on_load_chats=None,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)

        self._on_chat_click = on_chat_click
        self._on_chat_delete = on_chat_delete
        self._on_chat_create = on_chat_create
        self._on_load_chats = on_load_chats

        self.is_loading = True
        self.list_chats = ft.ListView(
            controls=[
                ft.Row(
                    [
                        ft.ProgressRing()
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            adaptive=True,
            spacing=20,
            divider_thickness=1,
        )

        self.controls = [
            ft.Container(
                content=ft.Text(
                    value='Список Ваших чатов:',
                    style=ft.TextStyle(size=20),
                    text_align=ft.TextAlign.CENTER,
                )
            ),

            ft.Divider(),
            self.list_chats,
            ft.Divider(),

            ft.Container(
                content=ft.ElevatedButton(
                    icon=ft.icons.ADD,
                    text='Создать чат',
                    on_click=lambda _: self._on_chat_create(),
                )
            ),
            ft.Container(height=12),
        ]

    @property
    def chats(self):
        return []

    @chats.setter
    def chats(self, value: list):
        self.list_chats.controls = [
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Row(
                            [
                                ft.CircleAvatar(
                                    content=ft.Text(
                                        value=chat['name'][0].upper(),
                                    ),
                                    foreground_image_url='',
                                ),
                                ft.TextButton(
                                    text=chat['name'],
                                    on_click=lambda _, chat_id=chat['id']: self._on_chat_click and self._on_chat_click(chat_id),
                                )
                            ],
                            spacing=20,
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE_OUTLINE,
                            icon_color=ft.colors.RED,
                            on_click=lambda _, chat_id=chat['id']: self._on_chat_delete and self._on_chat_delete(chat_id),
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                margin=ft.Margin(
                    left=10,
                    right=10,
                    top=0,
                    bottom=0,
                ),
                expand=True,
                on_click=lambda _, chat_id=chat['id']: self._on_chat_click and self._on_chat_click(chat_id),
            ) for chat in value
        ]

        self.update()

    def build(self):
        super().build()
        self._on_load_chats()
