"""Dashboard blueprint for Q-Reserve."""

from flask import Blueprint

dashboard_bp = Blueprint('dashboard', __name__)

from . import routes