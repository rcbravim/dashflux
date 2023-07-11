import math
import os

from flask import request, render_template, session, redirect, url_for

from app.database.models import Category
from app.database.database import db
from app.library.helper import paginator

PG_LIMIT = int(os.getenv('PG_LIMIT', 25))


def financial_form_controller():
    success = session.pop('success', None)

    context = {
        'labels': [],
        'categories': [],
        'filter': {
            'type': request.form.get('type', ''),
            'search': request.form.get('search', ''),
            'label': request.form.get('label', '')
        },
        'pages': {
            'pg': [],
            'total_pg': [],
            'pg_range': [],
        }
    }

    return render_template('board/pages/financial_form.html', context=context)
