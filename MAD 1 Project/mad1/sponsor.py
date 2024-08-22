from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from flask_login import current_user, login_required
from .models import *
from datetime import datetime

sponsor = Blueprint("sponsor", __name__)


@sponsor.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():

    def get_campaigns_by_user(user_id):
        return Campaign.query.filter_by(user_id=user_id).all()

    def get_influencer_requests_for_campaigns(campaign_ids):
        return (
            db.session.query(Req_by_inf, Campaign.c_name, User.name)
            .join(Campaign, Req_by_inf.campaign_id == Campaign.id)
            .join(Influencer, Req_by_inf.influencer_id == Influencer.id)
            .join(User, Influencer.user_id == User.id)
            .filter(Req_by_inf.campaign_id.in_(campaign_ids))
            .all()
        )

    campaigns = get_campaigns_by_user(current_user.id)
    campaign_ids = [campaign.id for campaign in campaigns]
    influencer_requests = get_influencer_requests_for_campaigns(campaign_ids)

    return render_template(
        "sponsor/dashboard.html",
        user=current_user,
        campaigns=campaigns,
        influencer_requests=influencer_requests,
    )


# edit the profile of the sponsor
@sponsor.route("/edit_profile/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_profile(user_id):
    user = User.query.filter_by(id=user_id).first()
    if request.method == "POST":
        user.name = request.form.get("name")
        user.email = request.form.get("email")
        user.user_niche = request.form.get("user_niche")
        if user.user_niche == "":
            flash("Please select a niche", "error")
            return redirect(url_for("sponsor.edit_profile", user_id=user_id))
        db.session.commit()
        flash("Profile Updated Successfully")
        return redirect(url_for("sponsor.dashboard"))
    return render_template("sponsor/edit_profile.html", user=user)


# view all the campaigns
@sponsor.route("/campaigns", methods=["GET", "POST"])
@login_required
def campaigns():
    # only those campaigns whose status is incomplete
    campaigns = Campaign.query.filter_by(
        user_id=current_user.id, status="Incomplete"
    ).all()

    return render_template(
        "sponsor/campaigns.html", user=current_user, campaigns=campaigns
    )


# create a new campaign
@sponsor.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        c_name = request.form.get("c_name")
        c_desc = request.form.get("c_desc")
        budget = request.form.get("budget")
        c_start_date = request.form.get("c_start_date")
        c_end_date = request.form.get("c_end_date")
        c_visibility = request.form.get("c_visibility")
        c_niche = request.form.get("c_niche")

        if c_visibility == "Private" and c_niche == "All":
            flash("Private campaigns cannot be of All niche", "error")
            return redirect(url_for("sponsor.create"))

        if c_visibility == "Public" and c_niche != "All":
            flash("Public campaigns can only be of All niche", "error")
            return redirect(url_for("sponsor.create"))

        if not c_desc:
            flash("Campaign description is required", "error")
            return redirect(url_for("sponsor.create"))

        new_campaign = Campaign(
            c_name=c_name,
            c_desc=c_desc,
            budget=budget,
            c_start_date=datetime.strptime(c_start_date, "%Y-%m-%d"),
            c_end_date=datetime.strptime(c_end_date, "%Y-%m-%d"),
            c_visibility=c_visibility,
            c_niche=c_niche,
            user_id=current_user.id,
        )

        db.session.add(new_campaign)
        db.session.commit()
        flash("Campaign Created Successfully")
        return redirect(url_for("sponsor.campaigns"))
    return render_template("sponsor/new_campaign.html", user=current_user)


# edit the details of the campaign
@sponsor.route("/edit_campaign/<int:campaign_id>", methods=["GET", "POST"])
@login_required
def edit_campaign(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    if request.method == "POST":
        c_name = request.form.get("c_name")
        c_desc = request.form.get("c_desc")
        budget = request.form.get("budget")
        c_visibility = request.form.get("c_visibility")
        c_niche = request.form.get("c_niche")
        c_start_date = request.form.get("c_start_date")
        c_end_date = request.form.get("c_end_date")

        if c_visibility == "Private" and c_niche == "All":
            flash("Private campaigns cannot be of All niche", "error")
            return redirect(url_for("sponsor.create"))

        if c_visibility == "Public" and c_niche != "All":
            flash("Public campaigns can only be of All niche", "error")
            return redirect(url_for("sponsor.create"))

        campaign.c_name = c_name
        campaign.c_desc = c_desc
        campaign.budget = budget
        campaign.c_visibility = c_visibility
        campaign.c_niche = c_niche
        campaign.c_start_date = datetime.strptime(c_start_date, "%Y-%m-%d")
        campaign.c_end_date = datetime.strptime(c_end_date, "%Y-%m-%d")
        db.session.commit()
        flash("Campaign Updated Successfully")
        return redirect(url_for("sponsor.campaigns"))
    return render_template("sponsor/edit_campaign.html", campaign=campaign)


# view the details of the campaign
@sponsor.route("/view_campaign/<int:campaign_id>")
@login_required
def view_campaign(campaign_id):
    # retrieve the campaign from the database
    campaign = Campaign.query.filter_by(id=campaign_id).first()

    # sent requests
    requests = (
        Req_by_sponsor.query.filter_by(campaign_id=campaign_id)
        .order_by(Req_by_sponsor.id.desc())
        .all()
    )
    sent_requests = []
    for request in requests:
        influencer = Influencer.query.filter_by(id=request.influencer_id).first()
        user = User.query.filter_by(id=influencer.user_id).first()
        influencer_name = user.name
        sent_requests.append(
            {
                "influencer_name": influencer_name,
                "influencer": influencer,
                "request": request,
            }
        )

    # received requests
    received_requests = (
        Req_by_inf.query.filter_by(campaign_id=campaign_id)
        .order_by(Req_by_inf.id.desc())
        .all()
    )
    received_requests_list = []
    for request in received_requests:
        influencer = Influencer.query.filter_by(id=request.influencer_id).first()
        user = User.query.filter_by(id=influencer.user_id).first()
        influencer_name = user.name
        received_requests_list.append(
            {
                "influencer_name": influencer_name,
                "influencer": influencer,
                "request": request,
            }
        )

    return render_template(
        "sponsor/view_campaign.html",
        user=current_user,
        campaign=campaign,
        req_sent=sent_requests,
        received_req=received_requests_list,
    )


# delete the campaign
@sponsor.route("/delete_campaign/<int:campaign_id>", methods=["POST"])
@login_required
def delete_campaign(campaign_id):
    # retrieve the campaign from the database
    campaign = Campaign.query.filter_by(id=campaign_id).first()

    db.session.delete(campaign)
    db.session.commit()
    flash("Campaign Deleted Successfully")
    return redirect(url_for("sponsor.campaigns"))


# view all completed campaigns
@sponsor.route("/completed_campaigns", methods=["GET", "POST"])
@login_required
def completed_campaigns():
    campaigns = Campaign.query.filter_by(status="Completed").all()
    return render_template(
        "sponsor/completed_campaigns.html", user=current_user, campaigns=campaigns
    )


# mark campaign as completed
@sponsor.route("/mark_complete/<int:campaign_id>", methods=["GET", "POST"])
@login_required
def mark_complete(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    if campaign.status == "Incomplete":
        campaign.status = "Completed"
        db.session.commit()
        flash("Campaign Marked Completed Successfully")
        return redirect(url_for("sponsor.campaigns"))


@sponsor.route(
    "/campaign/<int:campaign_id>/browse_influencers", methods=["GET", "POST"]
)
@login_required
def browse_influencers(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    # search query
    if request.method == "POST" and "viewAll" in request.form:
        search_query = ""
    else:
        search_query = request.form.get("search", "")

    if search_query:
        # Find influencers based on the search query
        user_ids = (
            User.query.filter(User.name.ilike(f"%{search_query}%"))
            .filter(User.is_flagged == False)
            .all()
        )
        influencer_ids = [user.id for user in user_ids]

        # Get all the matching influencers
        influencers = Influencer.query.filter(
            Influencer.user_id.in_(influencer_ids)
        ).all()
    else:
        user_ids = User.query.filter(User.is_flagged == False).all()
        influencer_ids = [user.id for user in user_ids]

        # Get all influencers if no search query is provided
        influencers = Influencer.query.filter(
            Influencer.user_id.in_(influencer_ids)
        ).all()

    influencer_details = []
    for influencer in influencers:
        user_id = influencer.user_id
        user = User.query.filter_by(id=user_id).first()
        influencer_details.append(
            {
                "influencer": influencer,
                "user_id": user.id,
                "username": user.name,
                "niche": user.user_niche,
                "email": user.email,
            }
        )

    return render_template(
        "sponsor/view_influencers.html",
        user=current_user,
        influencers=influencer_details,
        campaign=campaign,
        search_query=search_query,
    )


# create a new request sent by sponsor
@sponsor.route(
    "/campaign/<int:campaign_id>/new_request_by_sponsor/<int:influencer_id>",
    methods=["GET", "POST"],
)
@login_required
def new_request_by_sponsor(campaign_id, influencer_id):
    if request.method == "POST":
        requirements = request.form.get("requirements")
        amount = request.form.get("amount")

        new_request_by_sponsor = Req_by_sponsor(
            campaign_id=campaign_id,
            influencer_id=influencer_id,
            requirements=requirements,
            amount=amount,
        )

        db.session.add(new_request_by_sponsor)
        db.session.commit()
        flash("Request Sent Successfully")
        return redirect(url_for("sponsor.view_campaign", campaign_id=campaign_id))

    return render_template(
        "sponsor/new_req.html",
    )


# accept the request sent by influencer
@sponsor.route("accept_request/<int:request_id>", methods=["GET", "POST"])
@login_required
def accept_request(request_id):
    req_by_inf = Req_by_inf.query.filter_by(id=request_id).first()
    req_by_inf.request_status = "Accepted"
    db.session.commit()
    flash("Request Accepted Successfully")
    return redirect(
        url_for("sponsor.view_campaign", campaign_id=req_by_inf.campaign_id)
    )


# accept the request sent by influencer from the dashboard
@sponsor.route(
    "accept_request_from_dashboard/<int:request_id>", methods=["GET", "POST"]
)
@login_required
def accept_request_from_dashboard(request_id):
    req_by_inf = Req_by_inf.query.filter_by(id=request_id).first()
    req_by_inf.request_status = "Accepted"
    db.session.commit()
    flash("Request Accepted Successfully")
    return redirect(url_for("sponsor.dashboard"))


# reject the request sent by influencer
@sponsor.route("reject_request/<int:request_id>", methods=["GET", "POST"])
@login_required
def reject_request(request_id):
    req_by_inf = Req_by_inf.query.filter_by(id=request_id).first()
    req_by_inf.request_status = "Rejected"
    db.session.commit()
    flash("Request Rejected Successfully")
    return redirect(
        url_for("sponsor.view_campaign", campaign_id=req_by_inf.campaign_id)
    )


# delete the request sent by sponsor
@sponsor.route("delete_sponsor_request/<int:request_id>", methods=["POST"])
@login_required
def delete_sponsor_request(request_id):

    # retrieve the request sent by sponsor
    req_by_sponsor = Req_by_sponsor.query.filter_by(id=request_id).first()

    # delete the request if it is pending or rejected
    if (
        req_by_sponsor.request_status == "Pending"
        or req_by_sponsor.request_status == "Rejected"
    ):
        db.session.delete(req_by_sponsor)
        db.session.commit()
        flash("Request Deleted Successfully")
    return redirect(
        url_for("sponsor.view_campaign", campaign_id=req_by_sponsor.campaign_id)
    )


@sponsor.route("delete_influencer_request/<int:request_id>", methods=["POST"])
@login_required
def delete_influencer_request(request_id):

    # retrieve the request sent by influencer
    req_sent_by_influencer = Req_by_inf.query.filter_by(id=request_id).first()

    # delete the request if it is rejected
    if req_sent_by_influencer.request_status == "Rejected":
        db.session.delete(req_sent_by_influencer)
        db.session.commit()
        flash("Request Deleted Successfully")
    return redirect(
        url_for("sponsor.view_campaign", campaign_id=req_sent_by_influencer.campaign_id)
    )


# edit Req_sent_by_sponsor
@sponsor.route("/edit_req_sent_by_sponsor/<int:request_id>", methods=["GET", "POST"])
@login_required
def edit_req_sent_by_sponsor(request_id):
    req_sent_by_sponsor = Req_by_sponsor.query.filter_by(id=request_id).first()
    if request.method == "POST":
        req_sent_by_sponsor.requirements = request.form.get("requirements")
        req_sent_by_sponsor.amount = request.form.get("amount")
        db.session.commit()
        flash("Request Updated Successfully")
        return redirect(
            url_for(
                "sponsor.view_campaign", campaign_id=req_sent_by_sponsor.campaign_id
            )
        )
    return render_template(
        "sponsor/edit_req_sent.html", req_sent_by_sponsor=req_sent_by_sponsor
    )
