from flask import Blueprint, render_template, flash, redirect, url_for
from . import db
from flask_login import login_required, current_user
from .models import *
from sqlalchemy import func, or_

admin = Blueprint("admin", __name__)


@admin.route("/home")
@login_required
def dashboard():
    no_of_sponsors = User.query.filter_by(role="Sponsor").count()
    no_of_campaigns = Campaign.query.count()
    no_of_users = User.query.count()
    no_of_influencers = Influencer.query.count()
    no_of_req_sent_by_influencer = Req_by_inf.query.count()
    no_of_req_sent_by_sponsor = Req_by_inf.query.count()
    total_req_sent = no_of_req_sent_by_influencer + no_of_req_sent_by_sponsor
    completed_campaigns = Campaign.query.filter_by(status="Completed").count()
    incomplete_campaigns = Campaign.query.filter_by(status="Incomplete").count()
    completed_requests_1 = Req_by_inf.query.filter_by(is_completion_done=True).count()
    completed_requests_2 = Req_by_sponsor.query.filter_by(
        is_completion_done=True
    ).count()
    completed_requests = completed_requests_1 + completed_requests_2
    incomplete_requests_1 = Req_by_inf.query.filter_by(is_completion_done=False).count()
    incomplete_requests_2 = Req_by_sponsor.query.filter_by(
        is_completion_done=False
    ).count()
    incomplete_requests = incomplete_requests_1 + incomplete_requests_2
    total_campaign_budget = db.session.query(func.sum(Campaign.budget)).scalar()

    return render_template(
        "admin/dashboard.html",
        user=current_user,
        no_of_users=no_of_users,
        no_of_sponsors=no_of_sponsors,
        no_of_campaigns=no_of_campaigns,
        no_of_influencers=no_of_influencers,
        no_of_req_sent_by_influencer=no_of_req_sent_by_influencer,
        no_of_req_sent_by_sponsor=no_of_req_sent_by_sponsor,
        total_req_sent=total_req_sent,
        completed_campaigns=completed_campaigns,
        incomplete_campaigns=incomplete_campaigns,
        completed_requests=completed_requests,
        incomplete_requests=incomplete_requests,
        total_campaign_budget=total_campaign_budget,
    )


# view campaigns
@admin.route("/view_campaigns", methods=["GET", "POST"])
def view_campaigns():
    campaigns = Campaign.query.filter_by(is_flagged=False).all()
    return render_template(
        "admin/view_campaigns.html", user=current_user, campaigns=campaigns
    )


# view flagged campaigns
@admin.route("/flagged_campaigns", methods=["GET", "POST"])
def flagged_campaigns():
    campaigns = Campaign.query.filter_by(is_flagged=True).all()
    return render_template(
        "admin/flagged_campaigns.html", user=current_user, campaigns=campaigns
    )


# flag campaign
@admin.route("/flag_campaign/<int:campaign_id>", methods=["POST"])
def flag_campaign(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    campaign.is_flagged = True
    db.session.commit()
    flash("Campaign Flagged Successfully")
    return redirect(url_for("admin.view_campaigns"))


# unflag campaign
@admin.route("/unflag_campaign/<int:campaign_id>", methods=["POST"])
def unflag_campaign(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    campaign.is_flagged = False
    db.session.commit()
    flash("Campaign Unflagged Successfully")
    return redirect(url_for("admin.flagged_campaigns"))


# view users
@admin.route("/view_users", methods=["GET", "POST"])
def view_users():
    users = (
        User.query.filter(or_(User.role == "Influencer", User.role == "Sponsor"))
        .filter_by(is_flagged=False)
        .all()
    )
    print(users)
    return render_template("admin/view_users.html", user=current_user, users=users)


# view flagged users
@admin.route("/flagged_users", methods=["GET", "POST"])
def flagged_users():
    users = User.query.filter_by(is_flagged=True).all()
    return render_template("admin/flagged_users.html", user=current_user, users=users)


# flag user
@admin.route("/flag_user/<int:user_id>", methods=["POST"])
def flag_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    user.is_flagged = True
    db.session.commit()
    flash("User Flagged Successfully")
    return redirect(url_for("admin.view_users"))


# unflag user
@admin.route("/unflag_user/<int:user_id>", methods=["POST"])
def unflag_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    user.is_flagged = False
    db.session.commit()
    flash("User Unflagged Successfully")
    return redirect(url_for("admin.view_users"))
