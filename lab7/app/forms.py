from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp

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

