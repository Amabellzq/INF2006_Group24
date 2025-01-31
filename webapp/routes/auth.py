from webbrowser import register

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from webapp.extensions import db
from webapp.models.user import User
from webapp.schemas import RegisterSchema, LoginSchema
from datetime import datetime
from marshmallow import ValidationError

auth_bp = Blueprint('auth', __name__)
register_schema = RegisterSchema()
login_schema = LoginSchema()

import traceback
from marshmallow import ValidationError


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    try:
        data = register_schema.load(request.form)
        if User.query.filter_by(email=data['email']).first():
            return render_template('register.html', error="Email already exists")

        user = User(email=data['email'], role='user')  # Default role is 'user'
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    except ValidationError as e:
        # Print the validation error to the console
        # Optionally, print entire stack trace:
        # traceback.print_exc()
        flash(e.messages, 'error')

        return render_template('login.html', error=e.messages)

    except Exception as e:
        # Roll back the database session
        db.session.rollback()

        # Print the error message and stack trace to console
        print("An unexpected error occurred:")
        traceback.print_exc()

        # Optionally, you could just print the error message:
        # print("Error:", str(e))
        flash(str(e), 'error')
        return render_template('home.html', error=str(e))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    try:
        data = login_schema.load(request.form)
        user = User.query.filter_by(email=data['email']).first()

        if not user or not user.check_password(data['password']):
            flash('Invalid email or password', 'error')
            return render_template('login.html')

        # Log in the user using Flask-Login
        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()

        flash('Logged in successfully!', 'success')

        # Redirect based on role
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('main.home'))

    except ValidationError as e:
        flash(e.messages, 'error')
        return render_template('login.html', error=e.messages)
    except Exception as e:
        flash(str(e), 'error')
        return render_template('login.html', error=str(e))


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('main.home'))