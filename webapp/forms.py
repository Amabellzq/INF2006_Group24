# webapp/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Optional
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

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




class PaymentForm(FlaskForm):
    card_number = StringField('Card Number',
                              validators=[DataRequired(),
                                          Length(min=16, max=16, message="Card number must be exactly 16 digits"),
                                          Regexp(r'^\d{16}$', message="Card number must contain only digits")])

    exp_date = StringField('Expiration Date',
                           validators=[DataRequired(),
                                       Regexp(r'^(0[1-9]|1[0-2])\/\d{2}$', message="Expiration date must be MM/YY")])

    cvc = StringField('CVC',
                      validators=[DataRequired(),
                                  Length(min=3, max=3, message="CVC must be 3 digits"),
                                  Regexp(r'^\d{3}$', message="CVC must contain only digits")])

    submit = SubmitField('Pay Now')

