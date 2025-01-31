# webapp/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Optional

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    original_price = DecimalField('Original Price', validators=[
        DataRequired(),
        NumberRange(min=0.01)
    ])
    discount_price = DecimalField('Discount Price', validators=[
        Optional(),  # discount_price can be empty
        NumberRange(min=0.01)
    ])
    stock = IntegerField('Stock Quantity', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])

    # New field to handle image uploads
    image = FileField('Product Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only image files are allowed!')
    ])
