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
