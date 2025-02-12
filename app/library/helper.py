import hashlib

from sqlalchemy import func, extract
from unicodedata import normalize
from typing import List

from app.database.database import db
from app.database.models import Transaction, CreditCardTransaction, Analytic


def paginator(pg: int, pg_total: int) -> List[int]:
    if pg_total > 5:
        if pg > 3:
            pg_init = pg - 2
            if (pg + 1) > pg_total:
                pg_init = pg_init - 2
                pg_end = pg_total
            elif (pg + 2) > pg_total:
                pg_init = pg_init - 1
                pg_end = pg_total
            else:
                pg_init = pg - 2
                pg_end = pg + 2
        else:
            pg_init = 1
            pg_end = 5
    else:
        pg_init = 1
        pg_end = pg_total
    return list(range(pg_init, (pg_end + 1)))


def compare_values(value_1, value_2):
    return normalize_for_match(value_1) == normalize_for_match(value_2)


def normalize_for_match(value):
    # return normalize('NFKD', value).encode('ASCII', 'ignore').decode('ASCII').upper().strip()
    return value.upper().strip()


def generate_hash(value: str) -> str:
    return hashlib.md5(str(value).encode()).hexdigest()


def update_analytic(user_id, cycle_date):

    month = cycle_date.month
    year = cycle_date.year

    incomes_transactions = db.session.query(
        func.coalesce(func.sum(Transaction.tra_amount), 0)
    ).filter(
        Transaction.tra_amount > 0,
        Transaction.user_id == user_id,
        extract('month', Transaction.tra_entry_date) == month,
        extract('year', Transaction.tra_entry_date) == year
    ).scalar()

    incomes_credit_card_transactions = db.session.query(
        func.coalesce(func.sum(CreditCardTransaction.cct_amount), 0)
    ).filter(
        CreditCardTransaction.cct_amount > 0,
        CreditCardTransaction.user_id == user_id,
        extract('month', CreditCardTransaction.cct_due_date) == month,
        extract('year', CreditCardTransaction.cct_due_date) == year
    ).scalar()
    incomes = incomes_transactions + incomes_credit_card_transactions

    expenses_transactions = db.session.query(
        func.coalesce(func.sum(Transaction.tra_amount), 0)
    ).filter(
        Transaction.tra_amount < 0,
        Transaction.user_id == user_id,
        extract('month', Transaction.tra_entry_date) == month,
        extract('year', Transaction.tra_entry_date) == year
    ).scalar()

    expenses_credit_card_transactions = db.session.query(
        func.coalesce(func.sum(CreditCardTransaction.cct_amount), 0)
    ).filter(
        CreditCardTransaction.cct_amount < 0,
        CreditCardTransaction.user_id == user_id,
        extract('month', CreditCardTransaction.cct_due_date) == month,
        extract('year', CreditCardTransaction.cct_due_date) == year
    ).scalar()
    expenses = expenses_transactions + expenses_credit_card_transactions

    updated_analytic = Analytic(
        ana_month=month,
        ana_year=year,
        ana_incomes=incomes,
        ana_expenses=expenses,
        user_id=user_id
    )
    db.session.merge(updated_analytic)
    db.session.commit()
