from decimal import Decimal

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, DecimalField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError

CATEGORIES = [
    ("electronics", "Електроніка"),
    ("home", "Дім"),
    ("clothes", "Одяг"),
    ("books", "Книги"),
    ("other", "Інше"),
]


class ProductForm(FlaskForm):
    name = StringField(
        "Назва",
        validators=[DataRequired(message="Вкажіть назву"), Length(min=3, message="Мінімум 3 символи")],
    )
    content = TextAreaField(
        "Опис",
        render_kw={"rows": 5, "cols": 40},
        validators=[DataRequired(message="Вкажіть опис")],
    )
    price = DecimalField(
        "Ціна",
        places=2,
        rounding=None,
        validators=[DataRequired(message="Вкажіть ціну"), NumberRange(min=Decimal("0.01"), message="Ціна має бути додатною")],
    )
    category = SelectField("Категорія", choices=CATEGORIES, validators=[DataRequired()])
    quantity = IntegerField(
        "Кількість",
        validators=[Optional(), NumberRange(min=0, message="Кількість не може бути від'ємною")],
        default=0,
    )
    image = FileField(
        "Зображення",
        validators=[FileAllowed(["png", "jpg", "jpeg"], "Дозволені лише PNG, JPG, JPEG")],
    )
    submit = SubmitField("Зберегти")

    def validate_price(self, field):
        if field.data is not None and field.data.as_tuple().exponent < -2:
            raise ValidationError("Не більше двох знаків після коми")

    def validate_quantity(self, field):
        if field.data is None:
            raise ValidationError("Вкажіть кількість (0 або більше)")


class DeleteForm(FlaskForm):
    """Порожня форма: потрібна лише для CSRF-захисту POST-видалення."""
    submit = SubmitField("Видалити")
