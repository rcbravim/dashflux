from datetime import datetime
from app.db.database import db


class BoardAnalytic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ana_cycle = db.Column(db.Date, nullable=False)
    ana_json = db.Column(db.Text, nullable=False)
    ana_status = db.Column(db.Boolean, nullable=False)
    ana_date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ana_date_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ana_date_deleted = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('board_analytics'))

    def __repr__(self):
        return f"BoardAnalytic(id={self.id}, ana_cycle={self.ana_cycle}, user_id={self.user_id})"


class BoardCategory(db.Model):
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
        return '<BoardCategory %r>' % self.cat_name


class BoardSubcategory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sub_name = db.Column(db.String(250), nullable=False)
    sub_slug = db.Column(db.String(250), unique=True, nullable=False)
    sub_status = db.Column(db.Boolean, nullable=False)
    sub_date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    sub_date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    sub_date_deleted = db.Column(db.DateTime, nullable=True, default=None)
    category_id = db.Column(db.BigInteger, db.ForeignKey('board_category.id'), nullable=False)

    def __repr__(self):
        return '<BoardSubcategory %r>' % self.sub_name


class BoardFinancial(db.Model):
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
        return '<BoardFinancial %r>' % self.fin_slug


class BoardRelease(db.Model):
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
    beneficiary_id = db.Column(db.BigInteger, db.ForeignKey('board_beneficiary.id'), default=None)
    # client_id = db.Column(db.BigInteger, db.ForeignKey('board_client.id'), default=None)
    financial_account_id = db.Column(db.BigInteger, db.ForeignKey('board_financial.id'), default=None)
    financial_cost_center_id = db.Column(db.BigInteger, db.ForeignKey('board_financial.id'), default=None)
    subcategory_id = db.Column(db.BigInteger, db.ForeignKey('board_subcategory.id'), default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<BoardRelease %r>' % self.rel_slug


class BoardBeneficiaryCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cat_description = db.Column(db.String(250), nullable=False)
    cat_status = db.Column(db.Boolean, nullable=False)
    cat_date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cat_date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cat_date_deleted = db.Column(db.DateTime, nullable=True, default=None)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), default=None)
    cat_slug = db.Column(db.String(250), unique=True, nullable=False)

    def __repr__(self):
        return '<BoardBeneficiaryCategory %r>' % self.cat_description


class BoardBeneficiary(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ben_name = db.Column(db.String(250), nullable=False)
    ben_status = db.Column(db.Boolean, nullable=False)
    ben_date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ben_date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ben_date_deleted = db.Column(db.DateTime, nullable=True, default=None)
    beneficiary_category_id = db.Column(db.BigInteger, db.ForeignKey('board_beneficiary_category.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    ben_slug = db.Column(db.String(250), unique=True, nullable=False)

    def __repr__(self):
        return '<BoardBeneficiary %r>' % self.ben_name