from . import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    user_niche = db.Column(db.String(50))
    is_flagged = db.Column(db.Boolean, default=False)
    influencer = relationship("Influencer", backref="user", lazy=True)


class Influencer(db.Model):
    __tablename__ = "influencer"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    user_niche = db.Column(db.String(50))
    bio = db.Column(db.Text, nullable=False)
    followers = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class Campaign(db.Model):
    __tablename__ = "campaign"
    id = db.Column(db.Integer, primary_key=True)
    c_name = db.Column(db.String(50), nullable=False)
    c_desc = db.Column(db.Text, nullable=False)
    c_start_date = db.Column(db.Date, nullable=False)
    c_end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Incomplete")
    c_visibility = db.Column(db.String(10), nullable=False)
    c_niche = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    is_flagged = db.Column(db.Boolean, default=False)
    req_by_inf = db.relationship(
        "Req_by_inf",
        backref="campaign",
        cascade="all, delete-orphan",
    )
    req_by_sponsor = db.relationship(
        "Req_by_sponsor",
        backref="campaign",
        cascade="all, delete-orphan",
    )


class Req_by_sponsor(db.Model):
    __tablename__ = "req_by_sponsor"
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaign.id"), nullable=False)
    influencer_id = db.Column(
        db.Integer, db.ForeignKey("influencer.id"), nullable=False
    )
    requirements = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    request_status = db.Column(db.String(50), nullable=False, default="Pending")
    is_completion_done = db.Column(db.Boolean, nullable=False, default=False)


class Req_by_inf(db.Model):
    __tablename__ = "req_by_inf"
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaign.id"), nullable=False)
    influencer_id = db.Column(
        db.Integer, db.ForeignKey("influencer.id"), nullable=False
    )
    requirements = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    request_status = db.Column(db.String(50), nullable=False, default="Pending")
    is_completion_done = db.Column(db.Boolean, nullable=False, default=False)
