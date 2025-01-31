# webapp/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, IntegerField
from wtforms.validators import DataRequired, NumberRange

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    original_price = DecimalField('Original Price', validators=[
        DataRequired(),
        NumberRange(min=0.01)
    ])
    discount_price = DecimalField('Discount Price', validators=[
        NumberRange(min=0.01)
    ])
    stock = IntegerField('Stock Quantity', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])