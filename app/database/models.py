from app.database.database import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    use_login = db.Column(db.String(250), nullable=False)
    use_password = db.Column(db.String(128), nullable=False)
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


class Analytic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ana_cycle = db.Column(db.Date, nullable=False)
    ana_json = db.Column(db.Text, nullable=False)
    ana_status = db.Column(db.Boolean, nullable=False)
    ana_date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ana_date_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ana_date_deleted = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('analytics'))

    def __repr__(self):
        return f"Analytic(id={self.id}, ana_cycle={self.ana_cycle}, user_id={self.user_id})"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cat_name = db.Column(db.String(250), nullable=False)
    cat_slug = db.Column(db.String(250), unique=True, nullable=False)
    cat_status = db.Column(db.Boolean, nullable=False)
    cat_date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cat_date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cat_date_deleted = db.Column(db.DateTime, nullable=True, default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cat_type = db.Column(db.SmallInteger, nullable=False)

    def __repr__(self):
        return '<Category %r>' % self.cat_name


class Financial(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fin_slug = db.Column(db.String(250), unique=True, nullable=False)
    fin_cost_center = db.Column(db.String(250), default=None)
    fin_description = db.Column(db.String(250), default=None)
    fin_bank_name = db.Column(db.String(250), default=None)
    fin_bank_branch = db.Column(db.String(20), default=None)
    fin_bank_account = db.Column(db.String(20), default=None)
    fin_type = db.Column(db.SmallInteger, nullable=False)
    fin_status = db.Column(db.Boolean, nullable=False)
    fin_date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fin_date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fin_date_deleted = db.Column(db.DateTime, nullable=True, default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Financial %r>' % self.fin_slug


class Release(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rel_slug = db.Column(db.String(250), unique=True, nullable=False)
    rel_gen_status = db.Column(db.SmallInteger, nullable=False)
    rel_entry_date = db.Column(db.Date, nullable=False)
    rel_amount = db.Column(db.Numeric(15, 3), nullable=False)
    rel_monthly_balance = db.Column(db.Numeric(15, 3), nullable=False)
    rel_overall_balance = db.Column(db.Numeric(15, 3), nullable=False)
    rel_description = db.Column(db.String(250), default=None)
    rel_sqn = db.Column(db.Integer, nullable=False)
    rel_status = db.Column(db.Boolean, nullable=False)
    rel_date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rel_date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rel_date_deleted = db.Column(db.DateTime, nullable=True, default=None)
    establishment_id = db.Column(db.BigInteger, db.ForeignKey('establishment.id'), default=None)
    financial_account_id = db.Column(db.BigInteger, db.ForeignKey('financial.id'), default=None)
    financial_cost_center_id = db.Column(db.BigInteger, db.ForeignKey('financial.id'), default=None)
    category_id = db.Column(db.BigInteger, db.ForeignKey('category.id'), default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Release %r>' % self.rel_slug


class Establishment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    est_name = db.Column(db.String(250), nullable=False)
    est_status = db.Column(db.Boolean, nullable=False, default=True)
    est_date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    est_date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    est_date_deleted = db.Column(db.DateTime, nullable=True, default=None)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Establishment %r>' % self.est_name
