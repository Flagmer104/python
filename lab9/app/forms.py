from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp, ValidationError

TOPIC_CHOICES = [
    ("", "— оберіть тему —"),
    ("question", "Питання"),
    ("feedback", "Відгук"),
    ("bug", "Повідомлення про помилку"),
    ("other", "Інше"),
]


class ContactForm(FlaskForm):
    name = StringField(
        "Ім'я",
        validators=[DataRequired(message="Вкажіть ім'я"), Length(min=2, max=50, message="Ім'я має містити від 2 до 50 символів")],
    )
    email = StringField(
        "Email",
        validators=[DataRequired(message="Вкажіть email"), Email(message="Невірний формат email")],
    )
    phone = StringField(
        "Телефон",
        validators=[Optional(), Regexp(r"^\+?[0-9 \-()]{7,20}$", message="Невірний формат телефону")],
        render_kw={"placeholder": "+380501234567"},
    )
    topic = SelectField("Тема", choices=TOPIC_CHOICES, validators=[DataRequired(message="Оберіть тему")])
    message = TextAreaField(
        "Повідомлення",
        validators=[DataRequired(message="Введіть повідомлення"), Length(min=10, max=1000, message="Повідомлення має містити від 10 до 1000 символів")],
        render_kw={"rows": 5},
    )
    submit = SubmitField("Надіслати")


class RegistrationForm(FlaskForm):
    """Реєстрація: унікальність username та email перевіряється в БД."""

    username = StringField("Ім'я користувача", validators=[
        DataRequired(message="Вкажіть ім'я користувача"),
        Length(min=3, max=20, message="Від 3 до 20 символів"),
    ])
    email = StringField("Email", validators=[
        DataRequired(message="Вкажіть email"),
        Email(message="Невірний формат email"),
    ])
    password = PasswordField("Пароль", validators=[
        DataRequired(message="Вкажіть пароль"),
        Length(min=6, message="Пароль має містити щонайменше 6 символів"),
    ])
    confirm_password = PasswordField("Підтвердіть пароль", validators=[
        DataRequired(message="Підтвердіть пароль"),
        EqualTo("password", message="Паролі не збігаються"),
    ])
    submit = SubmitField("Зареєструватися")

    def validate_username(self, field):
        from . import db
        from .posts.models import User

        if db.session.scalar(db.select(User).where(User.username == field.data)):
            raise ValidationError("Таке ім'я користувача вже зайняте")

    def validate_email(self, field):
        from . import db
        from .posts.models import User

        if db.session.scalar(db.select(User).where(User.email == field.data.lower())):
            raise ValidationError("Користувач з таким email уже існує")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(message="Вкажіть email"), Email(message="Невірний формат email")])
    password = PasswordField("Пароль", validators=[DataRequired(message="Вкажіть пароль")])
    remember = BooleanField("Запам'ятати мене")
    submit = SubmitField("Увійти")
