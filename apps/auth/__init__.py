"""Authentication blueprint for Q-Reserve."""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from . import routes