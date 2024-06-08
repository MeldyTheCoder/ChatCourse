import flet as ft


class SignUpForm(ft.UserControl):
    title_form: ft.Text
    text_user: ft.TextField
    text_password: ft.TextField
    text_signup: ft.ElevatedButton
    text_signin: ft.Row

    def __init__(self, submit_values, btn_signin):
        super().__init__()
        self.submit_values = submit_values
        self.btn_signin = btn_signin

    def btn_signup(self, _):
        if not self.text_user.value:  
            self.text_user.error_text = "Поле имени не может быть пустым!"
            self.text_user.update()
        if not self.text_password.value:
            self.text_password.error_text = "Поле пароля не может быть пустым!"
            self.text_password.update()
        else:
            self.submit_values(self.text_user.value, self.text_password.value)

    def build(self):
        self.title_form = ft.Text(value="Регистрация",text_align=ft.TextAlign.CENTER,size=30, )
        self.text_user = ft.TextField(label="Имя пользователя")
        self.text_password = ft.TextField(
            label="Пароль", password=True, can_reveal_password=True
        )
        self.text_signup = ft.ElevatedButton(
            text="Регистрация",
            color=ft.colors.WHITE,
            width=150,
            height=50,
            on_click=self.btn_signup
        )
        self.text_signin = ft.Row(
            controls=[
                ft.Text(value="Уже есть аккаунт?"),
                ft.TextButton(text="Войдите", on_click=self.btn_signin)
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        return ft.Container(
            width=500,
            height=560,
            bgcolor=ft.colors.TEAL_800,
            padding=30,
            border_radius=10,
            alignment=ft.alignment.center,
            content=ft.Column(
                [
                    self.title_form,
                    ft.Container(height=30),
                    self.text_user,
                    self.text_password,
                    ft.Container(height=10),
                    self.text_signup,
                    ft.Container(height=20),
                    self.text_signin,
                    
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
       
