from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length

CATEGORY_CHOICES = [
    ("news", "Новина"),
    ("publication", "Публікація"),
    ("tech", "Технології"),
    ("other", "Інше"),
]


class PostForm(FlaskForm):
    title = StringField(
        "Заголовок",
        validators=[DataRequired(message="Вкажіть заголовок"),
                    Length(max=150, message="Не більше 150 символів")],
    )
    content = TextAreaField(
        "Текст",
        render_kw={"rows": 6},
        validators=[DataRequired(message="Вкажіть текст поста")],
    )
    enabled = BooleanField("Показувати на сайті", default=True)
    publish_date = DateTimeLocalField(
        "Дата публікації",
        format=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"],
        default=datetime.now,
        validators=[DataRequired(message="Вкажіть дату й час")],
    )
    category = SelectField("Категорія", choices=CATEGORY_CHOICES, default="other")
    submit = SubmitField("Зберегти")


class DeleteForm(FlaskForm):
    """Порожня форма лише для CSRF-захисту POST-видалення."""
    submit = SubmitField("Так, видалити")
