"""Tickets blueprint for Q-Reserve."""

from flask import Blueprint

tickets_bp = Blueprint('tickets', __name__)

from . import routes