from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SelectMultipleField, SubmitField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length

from .. import db
from .models import Tag, User

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
    author_id = SelectField("Автор", coerce=int)
    tags = SelectMultipleField("Теги", coerce=int)
    submit = SubmitField("Зберегти")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Списки вибору беруться з БД (синтаксис SQLAlchemy 2.0)
        users = db.session.scalars(db.select(User).order_by(User.id))
        self.author_id.choices = [(u.id, u.username) for u in users]
        tags = db.session.scalars(db.select(Tag).order_by(Tag.name))
        self.tags.choices = [(t.id, t.name) for t in tags]


class DeleteForm(FlaskForm):
    """Порожня форма лише для CSRF-захисту POST-видалення."""
    submit = SubmitField("Так, видалити")
