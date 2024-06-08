import flet as ft


class CreateChatModal(ft.AlertDialog):
    def __init__(self, on_create=None, users: list = None, selected_users: list = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._on_create = on_create
        self._users = users or []

        self._selected_users = selected_users or []
        self.modal = True
        self.title = ft.Text('Создание чата')
        self.expand = False

        self.name_input = ft.TextField(
            multiline=False,
            max_lines=1,
            max_length=50,
            autofocus=True,
            label='Название чата',
        )

        self.user_list = ft.ListView(
            spacing=20,
            divider_thickness=1,
            controls=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Checkbox(
                                value=user in self._selected_users,
                                on_change=lambda event, user_=user: self.handle_user_toggle(event, user_),
                            ),
                            ft.Row(
                                [
                                    ft.CircleAvatar(
                                        content=ft.Text(user['username'][0].upper()),
                                        foreground_image_url='',
                                    ),
                                    ft.Text(
                                        value=user['username']
                                    ),
                                ],
                                spacing=20,
                            )
                        ],
                        spacing=20,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    )
                ) for user in self._users
            ]
        )

        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    self.name_input,
                    self.user_list,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            height=600,
        )

        self.actions = [
            ft.ElevatedButton(
                text='Создать',
                icon=ft.icons.CREATE_OUTLINED,
                color=ft.colors.GREEN,
                on_click=self.handle_create,
            ),
            ft.ElevatedButton(
                text='Закрыть',
                icon=ft.icons.CLOSE_OUTLINED,
                color=ft.colors.RED,
                on_click=self.handle_close,
            )
        ]

    @property
    def users(self):
        return []

    @users.setter
    def users(self, value: list):
        self._users = value

        self.user_list.controls = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Checkbox(
                            value=user in self._selected_users,
                            on_change=lambda event, user_=user: self.handle_user_toggle(event, user_),
                        ),
                        ft.CircleAvatar(
                            content=user['username'][0].upper(),
                            foreground_image_url='',
                        ),
                        ft.Text(
                            value=user['username']
                        )
                    ],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ) for user in value
        ]

        self.update()

    def handle_user_toggle(self, event: ft.ControlEvent, user: dict):
        if user not in self._selected_users:
            event.control.value = True
            self.update()
            return self._selected_users.append(user)

        event.control.value = False
        self.update()
        return self._selected_users.remove(user)

    def handle_create(self, _):
        self._on_create and self._on_create(
            self.name_input.value,
            [user['id'] for user in self._selected_users],
        )
        self.handle_close(_)

    def handle_close(self, _):
        self.open = False
        self.update()
