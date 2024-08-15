import os

from flask import Blueprint, send_from_directory

env = os.getenv('ENVIRONMENT', '')
static_bp = Blueprint('static', __name__, url_prefix=f'/{os.getenv("ENVIRONMENT", "")}/static')


@static_bp.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)
