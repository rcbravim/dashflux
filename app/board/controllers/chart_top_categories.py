from collections import defaultdict
from datetime import datetime, timedelta

from flask import request, session, jsonify
from sqlalchemy import extract

from app.database.models import Category, CreditCardTransaction
from app.database.database import db


def chart_top_categories_controller():
    user_id = session.get('user_id')
    now = datetime.utcnow()
    month = int(request.json.get('month', now.month))
    year = int(request.args.get('year', now.year))
    three_months_ago = (now - timedelta(days=90)).date()
    quantity_categories = int(request.args.get('qnt_top_cat', 15))

    transactions = db.session.query(
        CreditCardTransaction
    ).filter(
        CreditCardTransaction.cct_status == True,
        CreditCardTransaction.user_id == user_id,
        extract('month', CreditCardTransaction.cct_due_date) == month,
        extract('year', CreditCardTransaction.cct_due_date) == year
    ).all()

    aggregated_data = defaultdict(lambda: {'total_spent': 0, 'goal_amount': 0, 'avg_last_3_months': []})

    for transaction in transactions:
        category_ids = transaction.category_ids.split(',')
        for category_id in category_ids:
            category = db.session.query(Category).filter_by(id=int(category_id)).first()
            if category:
                aggregated_data[category.cat_name]['total_spent'] += transaction.cct_amount
                aggregated_data[category.cat_name]['goal_amount'] = category.cat_goal or 0
                if transaction.cct_due_date >= three_months_ago:
                    aggregated_data[category.cat_name]['avg_last_3_months'].append(transaction.cct_amount)

    # Convertendo os dados agregados para o formato necessário
    results = [
        {
            "category": category_name,
            "amount": round(data['total_spent'] * -1, 2),
            "goal": data['goal_amount'],
            "avgLast3Months": round(sum(data['avg_last_3_months']) / len(data['avg_last_3_months']) * -1, 2) if data[
                'avg_last_3_months'] else 0.0
        }
        for category_name, data in aggregated_data.items()
    ]

    # Ordenando os resultados e limitando o número de categorias
    results = sorted(results, key=lambda x: x['amount'], reverse=True)[:quantity_categories]

    return jsonify(results)
