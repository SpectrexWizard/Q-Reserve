"""Notifications blueprint for Q-Reserve."""

from flask import Blueprint

notifications_bp = Blueprint('notifications', __name__)

from . import routes