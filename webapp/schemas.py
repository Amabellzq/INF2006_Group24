# webapp/schemas.py
from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from datetime import datetime


class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=120))
    original_price = fields.Float(
        required=True,
        validate=validate.Range(min=0.01)
    )
    discount_price = fields.Float(
        validate=validate.Range(min=0.01),
        allow_none=True
    )
    stock = fields.Int(
        required=True,
        validate=validate.Range(min=0)
    )
    image_url = fields.Url(allow_none=True)
    is_flash_sale = fields.Bool()
    flash_sale_start = fields.DateTime(allow_none=True)
    flash_sale_end = fields.DateTime(allow_none=True)
    version_id = fields.Int(dump_only=True)

    @validates_schema
    def validate_discount(self, data, **kwargs):
        if data.get('discount_price') and data['discount_price'] >= data.get('original_price', 0):
            raise ValidationError("Discount price must be lower than original price")

        if data.get('flash_sale_start') and data.get('flash_sale_end'):
            if data['flash_sale_start'] >= data['flash_sale_end']:
                raise ValidationError("Flash sale end must be after start time")


class RegisterSchema(Schema):
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=50)
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=128),
        load_only=True
    )
    confirm_password = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=128),
        load_only=True
    )
    role = fields.Str(
        validate=validate.OneOf(['user', 'admin']),
        default='user'
    )
    version_id = fields.Int(dump_only=True)

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        """Ensure password and confirm_password are identical."""
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError("Passwords must match.", field_name="confirm_password")



class LoginSchema(Schema):
    """Schema used exclusively for the login form.
       Only validates that 'email' is a valid email."""
    email = fields.Email(required=True)
    # If you want to include password as well but skip length checks:
    password = fields.Str(required=True, load_only=True)
