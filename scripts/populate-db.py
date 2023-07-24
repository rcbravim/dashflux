import os
import random
import sys
from datetime import timedelta

from flask import Flask
from werkzeug.security import generate_password_hash

from app.database.models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.path.join('sqlite:///' + app.instance_path, 'database.db').replace('\\scripts', '')

# init app with sqlalchemy instance
db.init_app(app)

only_user = True

with app.app_context():
    # Criar usuário
    user = User(
        use_login="dev@dashflux.com.br",
        use_password=generate_password_hash("password"),
        use_is_valid=True
    )
    db.session.add(user)

    if only_user:
        db.session.commit()
        print('user dev cadastrado')
        sys.exit()

    # Criar alguns registros de log fictícios
    for i in range(50):
        log = UserLog(
            log_user_agent=f"User Agent {i}",
            log_ip_address=f"IP Address {i}",
            log_risk_level=random.randint(1, 5),
            log_date_created=datetime.utcnow(),
            user_id=1
        )
        db.session.add(log)

    # Criar algumas transações fictícias
    start_date = datetime(2023, 1, 1).date()
    end_date = datetime(2023, 12, 31).date()
    for i in range(1000):
        random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

        transaction = Transaction(
            tra_description=f"Transaction {i}",
            tra_situation=random.randint(1, 3),
            tra_amount=random.randint(-1000, 1000),
            tra_entry_date=random_date,
            user_id=1,
            establishment_id=random.randint(1, 10),
            category_id=random.randint(1, 10),
            account_id=random.randint(1, 10)
        )
        db.session.add(transaction)

    # Criar alguns registros de analytics fictícios
    for i in range(12):
        analytic = Analytic(
            ana_month=i + 1,
            ana_year=datetime.utcnow().year,
            ana_incomes=random.randint(0, 1000),
            ana_expenses=random.randint(0, 1000),
            user_id=1
        )
        db.session.add(analytic)

    # Criar algumas categorias fictícias
    categories = ["Category A", "Category B", "Category C", "Category D", "Category E"]
    for name in categories:
        category = Category(
            cat_name=name,
            cat_description=f"Description for {name}",
            user_id=1,
            cat_type=random.randint(1, 2)
        )
        db.session.add(category)

    # Criar algumas contas fictícias
    for i in range(10):
        is_bank = random.choice([True, False])
        account = Account(
            acc_name=f"Account {i}",
            acc_description=f"Description for Account {i} " if not is_bank else None,
            acc_is_bank=is_bank,
            acc_bank_name=f"Account {i}" if is_bank else None,
            acc_bank_branch=random.randint(0, 9999) if is_bank else None,
            acc_bank_account=random.randint(0, 99999) if is_bank else None,
            user_id=1
        )
        db.session.add(account)

    # Criar alguns estabelecimentos fictícios
    for i in range(10):
        establishment = Establishment(
            est_name=f"Establishment {i}",
            user_id=1
        )
        db.session.add(establishment)

    # Commit das alterações
    db.session.commit()

    print("Dados fictícios inseridos no banco de dados.")
