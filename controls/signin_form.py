import flet as ft


# SignIn Form
class SignInForm(ft.UserControl):
    signin_image: ft.Container
    title_form: ft.Text
    text_user: ft.TextField
    text_password: ft.TextField
    text_signin: ft.ElevatedButton
    text_signup: ft.Row

    def __init__(self, submit_values,btn_signup):
        super().__init__()
        self.submit_values = submit_values
        self.btn_signup = btn_signup

    def btn_signin(self, e):
        if not self.text_user.value:  
            self.text_user.error_text = "Поле имени не может быть пустым!"
            self.text_user.update()
        if not self.text_password.value:
            self.text_password.error_text = "Поле пароля не может быть пустым!"
            self.text_password.update()
        else:
            self.submit_values(self.text_user.value,self.text_password.value)

    def build(self):
        self.signin_image = ft.Container(
            content=ft.Icon(
                name=ft.icons.PERSON,
                color=ft.colors.BLUE,
                size=100
            ),
            width=120,
            height=120,
            bgcolor=ft.colors.BLACK45,
            border_radius=10,
        )
        self.title_form = ft.Text(value="Вход",text_align=ft.TextAlign.CENTER,size=30, )
       
        self.text_user = ft.TextField(label="Имя пользователя")
        self.text_password = ft.TextField(
            label="Пароль", password=True, can_reveal_password=True
        )

        self.text_signin = ft.ElevatedButton(
            text="Войти",
            color=ft.colors.WHITE,
            width=150,
            height=50,
            on_click=self.btn_signin
        )

        self.text_signup = ft.Row(
            controls=[
                ft.Text(value="Еще нет аккаунта?"),
                ft.TextButton(text="Зарегистрируйтесь", on_click=self.btn_signup)
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
                    self.signin_image,
                    self.title_form,
                    self.text_user,
                    self.text_password,
                    ft.Container(height=10),
                    self.text_signin,
                    ft.Container(height=20),
                    self.text_signup,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
       
