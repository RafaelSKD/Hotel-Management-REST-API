"""
User model module.

This module defines the UserModel class responsible for handling
user persistence, authentication-related queries, and email
confirmation functionality within the application.
"""

from sql_alchemy import banco
from flask import request, url_for
from requests import post
import os
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------
# Mail Configuration
# ---------------------------------------------------------------------

MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
"""Mailgun domain used for sending transactional emails."""
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
"""API key used to authenticate requests to the Mailgun service."""

FROM_TITLE = 'NO-REPLY'
"""Display name of the email sender."""

FROM_EMAIL = 'no-reply@panadoshotelapi.com'
"""Sender email address used in outgoing messages."""


# ---------------------------------------------------------------------
# User Model Definition
# ---------------------------------------------------------------------

class UserModel(banco.Model):
    """
    Database model representing a system user.

    This model handles user data persistence, lookup operations,
    account activation status, and email confirmation workflows.
    """

    __tablename__ = 'users'
    """Name of the database table associated with this model."""

    user_id = banco.Column(banco.Integer, primary_key=True, autoincrement=True)
    login = banco.Column(banco.String(40), nullable=False, unique=True)
    senha = banco.Column(banco.String(40))
    email = banco.Column(banco.String(80), nullable=False, unique=True)
    ativado = banco.Column(banco.Boolean, default=False)

    def __init__(self, login, senha, email, ativado):
        """
        Initialize a new UserModel instance.

        Parameters
        ----------
        login : str
            Unique username used for authentication.
        senha : str
            User password.
        email : str
            Unique email address associated with the user.
        ativado : bool
            Indicates whether the user account is activated.
        """
        self.login = login
        self.senha = senha
        self.email = email
        self.ativado = ativado

    def json(self):
        """
        Serialize the user object to a dictionary.

        Returns
        -------
        dict
            A dictionary representation of the user model.
        """
        return {
            'user_id': self.user_id,
            'login': self.login,
            'email': self.email,
            'ativado': self.ativado
        }

    def send_confirmation_email(self):
        """
        Send an account confirmation email to the user.

        This method generates a confirmation link and sends it
        using the Mailgun API.

        Returns
        -------
        Response
            The HTTP response object returned by the Mailgun API request.
        """
        link = request.url_root[:-1] + url_for('userconfirm', user_id=self.user_id)

        return post(
            'https://api.mailgun.net/v3/{}/messages'.format(MAILGUN_DOMAIN),
            auth=('api', MAILGUN_API_KEY),
            data={
                'from': '{} <{}>'.format(FROM_TITLE, FROM_EMAIL),
                'to': self.email,
                'subject': 'Confirmação de Cadastro',
                'text': 'Clique no link para confirmar seu cadastro: {}'.format(link),
                'html': '<p>Clique no link para confirmar seu cadastro: '
                        '<a href="{}">Confirmar Cadastro</a></p>'.format(link)
            }
        )

    @classmethod
    def find_by_login(cls, login):
        """
        Retrieve a user by login.

        Parameters
        ----------
        login : str
            The login identifier.

        Returns
        -------
        UserModel or None
            The matching user instance if found; otherwise, None.
        """
        user = cls.query.filter_by(login=login).first()
        if user:
            return user
        return None

    @classmethod
    def find_by_email(cls, email):
        """
        Retrieve a user by email address.

        Parameters
        ----------
        email : str
            The user's email address.

        Returns
        -------
        UserModel or None
            The matching user instance if found; otherwise, None.
        """
        user = cls.query.filter_by(email=email).first()
        if user:
            return user
        return None

    @classmethod
    def find_user(cls, user_id):
        """
        Retrieve a user by unique identifier.

        Parameters
        ----------
        user_id : int
            The unique user identifier.

        Returns
        -------
        UserModel or None
            The matching user instance if found; otherwise, None.
        """
        user = cls.query.filter_by(user_id=user_id).first()
        if user:
            return user
        return None

    def save_user(self):
        """
        Persist the current user instance to the database.

        This method adds the user to the session and commits
        the transaction.
        """
        banco.session.add(self)
        banco.session.commit()

    def delete_user(self):
        """
        Remove the current user instance from the database.

        This method deletes the user from the session and commits
        the transaction.
        """
        banco.session.delete(self)
        banco.session.commit()