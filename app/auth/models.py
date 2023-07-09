from app.db.database import db
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