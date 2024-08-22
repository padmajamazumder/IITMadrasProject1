from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from flask_login import current_user, login_required
from .models import *

influencer = Blueprint("influencer", __name__)


@influencer.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if not current_user.influencer:
        if request.method == "POST":
            name = request.form.get("name")
            bio = request.form.get("bio")
            followers = request.form.get("followers")

            new_influencer = Influencer(
                name=name,
                bio=bio,
                followers=followers,
                user_id=current_user.id,
            )
            db.session.add(new_influencer)
            db.session.commit()
            flash("Influencer Created Successfully")
            return redirect(url_for("influencer.dashboard"))
        return render_template("influencer/dashboard.html", user=current_user)

    if current_user.influencer:
        influencer = Influencer.query.filter_by(user_id=current_user.id).first()
        req_sent_by_sponsor = (
            Req_by_sponsor.query.filter_by(influencer_id=influencer.id)
            .order_by(Req_by_sponsor.id.desc())
            .all()
        )
        req_sent_by_sponsor_list = []
        for req_sent_by_sponsor in req_sent_by_sponsor:
            campaign = Campaign.query.filter_by(
                id=req_sent_by_sponsor.campaign_id
            ).first()
            sponsor = User.query.filter_by(id=campaign.user_id).first()
            req_sent_by_sponsor_list.append(
                {
                    "campaign_name": campaign.c_name,
                    "sponsor_name": sponsor.name,
                    "req_sent_by_sponsor": req_sent_by_sponsor,
                }
            )
        req_sent_by_influencer = (
            Req_by_inf.query.filter_by(influencer_id=influencer.id)
            .order_by(Req_by_inf.id.desc())
            .all()
        )
        req_sent_by_influencer_list = []
        for req_sent_by_influencer in req_sent_by_influencer:
            campaign = Campaign.query.filter_by(
                id=req_sent_by_influencer.campaign_id
            ).first()
            influencer = User.query.filter_by(id=campaign.user_id).first()
            req_sent_by_influencer_list.append(
                {
                    "campaign_name": campaign.c_name,
                    "influencer_name": influencer.name,
                    "req_sent_by_influencer": req_sent_by_influencer,
                }
            )

    return render_template(
        "influencer/dashboard.html",
        user=current_user,
        req_sent_by_sponsor=req_sent_by_sponsor_list,
        req_sent_by_influencer=req_sent_by_influencer_list,
    )


@influencer.route("/view_campaigns", methods=["GET", "POST"])
@login_required
def view_campaigns():
    # to get the influencer's niche
    influencer = current_user.influencer[0]
    user = User.query.filter_by(id=influencer.user_id).first()
    influencer_niche = user.user_niche

    # for searching campaigns and filtering them
    if request.method == "POST" and "viewAll" in request.form:
        search_query = ""
    else:
        search_query = request.form.get("search", "")

    if search_query:
        campaigns = (
            Campaign.query.filter(Campaign.c_name.ilike(f"%{search_query}%"))
            .filter(Campaign.is_flagged == False, Campaign.status == "Incomplete")
            .all()
        )
    else:
        campaigns = Campaign.query.filter(
            Campaign.is_flagged == False, Campaign.status == "Incomplete"
        ).all()

    return render_template(
        "influencer/view_campaigns.html",
        user=current_user,
        campaigns=campaigns,
        influencer_niche=influencer_niche,
        search_query=search_query,
    )


@influencer.route(
    "/view_campaigns/<int:campaign_id>/send_request", methods=["GET", "POST"]
)
@login_required
def send_request(campaign_id):

    campaign = Campaign.query.filter_by(id=campaign_id).first()

    if request.method == "POST":

        requirements = request.form.get("requirements")
        amount = request.form.get("amount")

        # to get the influencer's id
        influencer = current_user.influencer[0]
        influencer_id = influencer.id

        new_req_sent_by_influencer = Req_by_inf(
            campaign_id=campaign_id,
            influencer_id=influencer_id,
            requirements=requirements,
            amount=amount,
        )
        db.session.add(new_req_sent_by_influencer)
        db.session.commit()
        flash("Request Sent Successfully")
        return redirect(url_for("influencer.dashboard"))
    return render_template("influencer/send_req.html", campaign=campaign)


@influencer.route("accept_request/<int:request_id>", methods=["GET", "POST"])
@login_required
def accept_request(request_id):
    # retrieve the request sent by sponsor
    req_sent_by_sponsor = Req_by_sponsor.query.filter_by(id=request_id).first()

    # change the status of the request to accepted
    req_sent_by_sponsor.request_status = "Accepted"
    db.session.commit()
    flash("Request Accepted Successfully")
    return redirect(url_for("influencer.dashboard"))


@influencer.route("reject_request/<int:request_id>", methods=["GET", "POST"])
@login_required
def reject_request(request_id):
    # retrieve the request sent by sponsor
    req_sent_by_sponsor = Req_by_sponsor.query.filter_by(id=request_id).first()

    # change the status of the request to rejected
    req_sent_by_sponsor.request_status = "Rejected"
    db.session.commit()
    flash("Request Rejected Successfully")
    return redirect(url_for("influencer.dashboard"))


@influencer.route("active_requests", methods=["GET", "POST"])
@login_required
def active_requests():
    influencer = current_user.influencer[0]

    # retrieve all the requests sent by influencer
    reqs_by_inf = Req_by_inf.query.filter_by(
        influencer_id=influencer.id, request_status="Accepted"
    ).all()

    # add details of the campaigns to the list
    reqs_by_inf_list = []
    for req_by_inf in reqs_by_inf:
        campaign = Campaign.query.filter_by(id=req_by_inf.campaign_id).first()
        user = User.query.filter_by(id=campaign.user_id).first()
        reqs_by_inf_list.append(
            {
                "campaign_name": campaign.c_name,
                "sponsor_name": user.name,
                "request": req_by_inf,
            }
        )
    reqs_by_sponsor = Req_by_sponsor.query.filter_by(
        influencer_id=influencer.id, request_status="Accepted"
    ).all()
    reqs_by_sponsor_list = []
    for req_by_sponsor in reqs_by_sponsor:
        campaign = Campaign.query.filter_by(id=req_by_sponsor.campaign_id).first()
        sponsor = User.query.filter_by(id=campaign.user_id).first()
        reqs_by_sponsor_list.append(
            {
                "campaign_name": campaign.c_name,
                "sponsor_name": sponsor.name,
                "request": req_by_sponsor,
            }
        )

    return render_template(
        "influencer/active_req.html",
        user=current_user,
        req_sent_by_sponsor=reqs_by_sponsor_list,
        req_sent_by_influencer=reqs_by_inf_list,
    )


@influencer.route("/mark_comp_inf_req/<int:request_id>", methods=["GET", "POST"])
@login_required
def mark_comp_inf_req(request_id):
    # retrieve the request sent by influencer
    req_sent_by_influencer = Req_by_inf.query.filter_by(id=request_id).first()
    # change the status of the request as completed
    req_sent_by_influencer.is_completion_done = True
    db.session.commit()
    flash("Request Marked Completed Successfully")
    return redirect(url_for("influencer.active_req"))


@influencer.route("/mark_comp_spo_req/<int:request_id>", methods=["GET", "POST"])
@login_required
def mark_comp_spo_req(request_id):
    # retrieve the request sent by sponsor
    req_sent_by_sponsor = Req_by_sponsor.query.filter_by(id=request_id).first()
    # change the status of the request as completed
    req_sent_by_sponsor.is_completion_done = True
    db.session.commit()
    flash("Request Marked Completed Successfully")
    return redirect(url_for("influencer.active_req"))


@influencer.route("/edit_request/<int:request_id>", methods=["GET", "POST"])
@login_required
def edit_request(request_id):
    # retrieve the request sent by influencer
    req_by_inf = Req_by_inf.query.filter_by(id=request_id).first()

    # edit details only if the request is pending
    if req_by_inf.request_status == "Pending":
        if request.method == "POST":
            req_by_inf.requirements = request.form.get("requirements")
            req_by_inf.amount = request.form.get("amount")
            db.session.commit()
            flash("Request Edited Successfully")
            return redirect(url_for("influencer.dashboard"))
    return render_template(
        "influencer/edit_req.html", req_sent_by_influencer=req_by_inf
    )
