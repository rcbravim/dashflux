from flask_login import UserMixin
from datetime import datetime

from app.database.database import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    use_login = db.Column(db.String(250), nullable=False, unique=True)
    use_password = db.Column(db.String(250), nullable=False)
    use_status = db.Column(db.Boolean, nullable=False, default=True)
    use_date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    use_date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    use_date_deleted = db.Column(db.DateTime, nullable=True, default=None)
    use_is_valid = db.Column(db.Boolean, nullable=False, default=False)
    use_is_manager = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '<User %r>' % self.use_login


class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    log_user_agent = db.Column(db.String(250), nullable=False)
    log_ip_address = db.Column(db.String(250), nullable=False)
    log_ip_type = db.Column(db.String(4), default=None)
    log_ip_country = db.Column(db.String(250), default=None)
    log_ip_country_flag = db.Column(db.String(64), default=None)
    log_ip_region = db.Column(db.String(250), default=None)
    log_ip_city = db.Column(db.String(250), default=None)
    log_ip_latitude = db.Column(db.Numeric(12, 9), default=None)
    log_ip_longitude = db.Column(db.Numeric(12, 9), default=None)
    log_location = db.Column(db.String(250), default=None)
    log_method = db.Column(db.String(16), default=None)
    log_risk_level = db.Column(db.SmallInteger, nullable=False)
    log_risk_comment = db.Column(db.String(250), default=None)
    log_date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), default=None)

    user = db.relationship('User', backref=db.backref('user_logs'))

    def __repr__(self):
        return f"UserLog(id={self.id}, log_ip_address={self.log_ip_address}, user_id={self.user_id})"


class Category(db.Model):
    __table_args__ = (
        db.UniqueConstraint('id', 'cat_name', 'user_id'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cat_name = db.Column(db.String(250), nullable=False)
    cat_description = db.Column(db.String(250), default=None)
    cat_goal = db.Column(db.Integer, default=0, nullable=True)
    cat_status = db.Column(db.Boolean, nullable=False, default=True)
    cat_date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cat_date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cat_date_deleted = db.Column(db.DateTime, nullable=True, default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Category %r>' % self.cat_name


class Account(db.Model):
    __table_args__ = (
        db.UniqueConstraint('id', 'acc_name', 'user_id'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    acc_name = db.Column(db.String(250), nullable=False)
    acc_description = db.Column(db.String(250), default=None)
    acc_is_bank = db.Column(db.Boolean, default=False)
    acc_bank_name = db.Column(db.String(250), default=None)
    acc_bank_branch = db.Column(db.String(20), default=None)
    acc_bank_account = db.Column(db.String(20), default=None)
    acc_status = db.Column(db.Boolean, nullable=False, default=True)
    acc_date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    acc_date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    acc_date_deleted = db.Column(db.DateTime, nullable=True, default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Account %r>' % self.acc_name


class Establishment(db.Model):
    __table_args__ = (
        db.UniqueConstraint('id', 'est_name', 'user_id'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    est_name = db.Column(db.String(250), nullable=False)
    est_description = db.Column(db.String(250), default=None)
    est_status = db.Column(db.Boolean, nullable=False, default=True)
    est_date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    est_date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    est_date_deleted = db.Column(db.DateTime, nullable=True, default=None)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Establishment %r>' % self.est_name


class CreditCard(db.Model):
    __table_args__ = (
        db.UniqueConstraint('id', 'ccr_name', 'user_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    ccr_name = db.Column(db.String(250), nullable=False)
    ccr_description = db.Column(db.String(250), nullable=True)
    ccr_flag = db.Column(db.String(250), nullable=False)
    ccr_last_digits = db.Column(db.String(4), nullable=True)
    ccr_due_day = db.Column(db.Integer, nullable=False)

    ccr_status = db.Column(db.Boolean, default=True, nullable=False)
    ccr_date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ccr_date_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ccr_date_deleted = db.Column(db.DateTime, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('credit_card'))

    def __repr__(self):
        return f"CreditCard(id={self.id}, ccr_name={self.ccr_name}, user_id={self.user_id})"


class Analytic(db.Model):
    __table_args__ = (
        db.PrimaryKeyConstraint('ana_month', 'ana_year', 'user_id'),
    )

    ana_month = db.Column(db.Integer, db.CheckConstraint('ana_month BETWEEN 1 AND 12'), nullable=False, primary_key=True)
    ana_year = db.Column(db.Integer, nullable=False, primary_key=True)
    ana_incomes = db.Column(db.Numeric(15, 3), nullable=False)
    ana_expenses = db.Column(db.Numeric(15, 3), nullable=False)
    ana_status = db.Column(db.Boolean, nullable=False, default=True)
    ana_date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ana_date_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ana_date_deleted = db.Column(db.DateTime, default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)

    user = db.relationship('User', backref=db.backref('analytics'))

    def __repr__(self):
        return f"Analytic(ana_year={self.ana_year}, ana_month={self.ana_month}, user_id={self.user_id})"


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tra_description = db.Column(db.String(250), nullable=True)
    tra_situation = db.Column(db.Integer, nullable=False)
    tra_amount = db.Column(db.Numeric(15, 3), nullable=False)
    tra_entry_date = db.Column(db.Date, nullable=False)
    tra_bound_hash = db.Column(db.String, nullable=True)

    tra_status = db.Column(db.Boolean, default=True, nullable=False)
    tra_date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tra_date_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tra_date_deleted = db.Column(db.DateTime, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishment.id'), nullable=False)
    category_ids = db.Column(db.String, nullable=False, default='', comment="1,2,3,4,5")
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('transaction'))

    def __repr__(self):
        return f"Transactions(id={self.id}, tra_description={self.tra_description}, user_id={self.user_id})"


class CreditCardTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cct_description = db.Column(db.String(250), nullable=True)
    cct_amount = db.Column(db.Numeric(15, 3), nullable=False)
    cct_entry_date = db.Column(db.Date, nullable=False)
    cct_due_date = db.Column(db.Date, nullable=False)
    cct_bound_hash = db.Column(db.String, nullable=True)

    cct_status = db.Column(db.Boolean, default=True, nullable=False)
    cct_date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cct_date_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cct_date_deleted = db.Column(db.DateTime, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishment.id'), nullable=False)
    category_ids = db.Column(db.String, nullable=False, default='', comment="1,2,3,4,5")
    credit_card_id = db.Column(db.Integer, db.ForeignKey('credit_card.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('credit_card_transaction'))

    def __repr__(self):
        return f"CreditCardTransactions(id={self.id}, description={self.cct_description}, user_id={self.user_id})"


class ChartCategoryMonthYear(db.Model):
    __table_args__ = (
        db.PrimaryKeyConstraint('ccm_month', 'ccm_year', 'user_id'),
    )

    ccm_month = db.Column(db.Integer, db.CheckConstraint('ccm_month BETWEEN 1 AND 12'), nullable=False, primary_key=True)
    ccm_year = db.Column(db.Integer, nullable=False, primary_key=True)
    category_ids = db.Column(db.String, nullable=True, comment="1,2,3,4,5")
    ccm_status = db.Column(db.Boolean, nullable=False, default=True)
    ccm_date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ccm_date_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ccm_date_deleted = db.Column(db.DateTime, default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)

    user = db.relationship('User', backref=db.backref('chart_category_month_year'))

    def __repr__(self):
        return f"ChartCategoryMonthYear(ccm_year={self.ccm_year}, ccm_month={self.ccm_month}, user_id={self.user_id})"


class Envelope(db.Model):

    # todo: analisar se é mais eficientre fazer pk composta, e remover id
    # __table_args__ = (
    #     db.PrimaryKeyConstraint('env_name', 'env_due_day', 'user_id'),
    # )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    env_name = db.Column(db.String(250), nullable=False)
    env_description = db.Column(db.String(250), default=None)
    env_due_day = db.Column(db.Integer, nullable=False)
    env_goal = db.Column(db.Integer, default=0, nullable=True)

    env_status = db.Column(db.Boolean, nullable=False, default=True)
    env_date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    env_date_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    env_date_deleted = db.Column(db.DateTime, default=None)

    category_ids = db.Column(db.String, nullable=True, comment="1,2,3,4,5")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('wrapper'))

    def __repr__(self):
        return '<Wrapper %r>' % self.env_name
