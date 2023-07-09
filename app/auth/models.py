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
