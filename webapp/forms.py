# webapp/forms.py
from cryptography.hazmat.primitives.asymmetric.padding import _Auto
from flask_wtf.file import FileField, FileAllowed
from wtforms import TextAreaField, DecimalField, IntegerField
from wtforms.validators import NumberRange, Optional, DataRequired, Length, Regexp, InputRequired
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class ProductForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        """Fix initialization to properly inherit FlaskForm behavior."""
        super(ProductForm, self).__init__(*args, **kwargs)
        self.image_url = None

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
        InputRequired(),
        NumberRange(min=0)
    ])

    # ✅ Fix: Allow selection of existing S3 images instead of only file uploads
    image_url = StringField('Image URL', validators=[Optional()])
    image = FileField('Upload Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only image files are allowed!')
    ])

class PaymentForm(FlaskForm):
    card_number = StringField(
        'Card Number',
        validators=[
            DataRequired(),
            Length(min=19, max=19, message="Card number must be in format XXXX XXXX XXXX XXXX"),
            Regexp(r'^\d{4} \d{4} \d{4} \d{4}$', message="Invalid card format. Use XXXX XXXX XXXX XXXX")
        ]
    )

    exp_date = StringField(
        'Expiration Date',
        validators=[
            DataRequired(),
            Length(min=5, max=5, message="Expiration date must be MM/YY"),
            Regexp(r'^(0[1-9]|1[0-2])/\d{2}$', message="Invalid format. Use MM/YY")
        ]
    )

    cvc = StringField(
        'CVC',
        validators=[
            DataRequired(),
            Length(min=3, max=3, message="CVC must be exactly 3 digits"),
            Regexp(r'^\d{3}$', message="CVC must contain only digits")
        ]
    )

    submit = SubmitField('Pay Now')


