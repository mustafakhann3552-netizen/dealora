from flask import Blueprint, render_template, request, abort, jsonify, flash, redirect, url_for
from sqlalchemy import desc


from models.deal import Deal
from models.category import Category
from models.store import Store
from models.blog import Blog
from flask_mail import Message
from extensions import mail

main = Blueprint("main", __name__)


# =====================================================
# Global Template Data
# =====================================================

@main.app_context_processor
def inject_global_data():

    return {

        "categories": Category.query.order_by(
            Category.name
        ).all(),

        "stores": Store.query.order_by(
            Store.name
        ).all()

    }


@main.route("/")
def home():

    q = request.args.get("q", "")
    category = request.args.get("category", type=int)
    store = request.args.get("store", type=int)
    sort = request.args.get("sort", "latest")
    page = request.args.get("page", 1, type=int)

    query = Deal.query

    # Search
    if q:
        query = query.filter(Deal.title.ilike(f"%{q}%"))

    # Category
    if category:
        query = query.filter(Deal.category_id == category)

    # Store
    if store:
        query = query.filter(Deal.store_id == store)

    # Sorting
    if sort == "price_low":
        query = query.order_by(Deal.new_price.asc())

    elif sort == "price_high":
        query = query.order_by(Deal.new_price.desc())

    elif sort == "discount":
        query = query.order_by(Deal.discount.desc())

    else:
        query = query.order_by(Deal.created_at.desc())

    # Pagination
    deals = query.paginate(
        page=page,
        per_page=12,
        error_out=False
    )

    # Featured Deals
    featured_deals = Deal.query.filter_by(featured=True).order_by(
        Deal.created_at.desc()
    ).limit(8).all()

    # Latest Blogs
    blogs = Blog.query.order_by(
        Blog.created_at.desc()
    ).limit(6).all()

    categories = Category.query.order_by(Category.name).all()
    stores = Store.query.order_by(Store.name).all()

    return render_template(
        "home.html",
        deals=deals,
        featured_deals=featured_deals,
        blogs=blogs,
        categories=categories,
        stores=stores
    )

# =====================================================
# Deal Detail
# =====================================================
@main.route("/deal/<slug>")
def deal_detail(slug):

    # ===============================
    # Get Current Deal
    # ===============================

    deal = Deal.query.filter_by(
        slug=slug
    ).first()

    if not deal:
        abort(404)

    # ===============================
    # Related Deals
    # ===============================

    related_deals = Deal.query.filter(

        Deal.category_id == deal.category_id,

        Deal.id != deal.id

    ).order_by(

        desc(Deal.id)

    ).limit(4).all()

    # ===============================
    # Latest Deals
    # ===============================

    latest_deals = Deal.query.order_by(

        desc(Deal.created_at)

    ).limit(6).all()

    # ===============================
    # Featured Deals
    # ===============================

    featured_deals = Deal.query.filter_by(

        featured=True

    ).order_by(

        desc(Deal.id)

    ).limit(6).all()

    # ===============================
    # Render
    # ===============================

    return render_template(

        "deal_detail.html",

        deal=deal,

        related_deals=related_deals,

        latest_deals=latest_deals,

        featured_deals=featured_deals

    )

# =====================================================
# About
# =====================================================

@main.route("/about")
def about():

    return render_template("about.html")


@main.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        msg = Message(
            subject=f"Contact Form: {subject}",
            recipients=["mustafakhamm3552@gmail.com"]   # <-- Apna Gmail
        )

        msg.body = f"""
New Contact Form Message

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}
"""

        try:
            mail.send(msg)
            flash("Your message has been sent successfully!", "success")

        except Exception as e:
            print("Mail Error:", e)
            flash("Failed to send message.", "danger")

        return redirect(url_for("main.contact"))

    return render_template("contact.html")

# =====================================================
# Blog List
# =====================================================

@main.route("/blogs")
def blogs():

    blogs = Blog.query.order_by(
        Blog.id.desc()
    ).all()

    return render_template(
        "blogs.html",
        blogs=blogs
    )


# =====================================================
# Blog Detail
# =====================================================

@main.route("/blog/<slug>")
def blog_detail(slug):

    blog = Blog.query.filter_by(
        slug=slug
    ).first_or_404()

    latest_blogs = Blog.query.filter(
        Blog.id != blog.id
    ).order_by(
        Blog.id.desc()
    ).limit(5).all()

    return render_template(
        "blog_detail.html",
        blog=blog,
        latest_blogs=latest_blogs
    )    
# =====================================================
# All Deals
# =====================================================
@main.route("/products")
def products():

    page = request.args.get("page", 1, type=int)

    deals = Deal.query.order_by(
        Deal.created_at.desc()
    ).paginate(page=page, per_page=12)

    return render_template(
        "products.html",
        deals=deals
    )
# =====================================================
# All Stores
# =====================================================

@main.route("/stores")
def stores():

    stores = Store.query.order_by(
        Store.name
    ).all()

    return render_template(
        "stores.html",
        stores=stores
    )


# =====================================================
# All Categories
# =====================================================

@main.route("/categories")
def categories():

    categories = Category.query.order_by(
        Category.name
    ).all()

    return render_template(
        "categories.html",
        categories=categories
    )


# =====================================================
# Category Details
# =====================================================

@main.route("/category/<int:id>")
def category_detail(id):

    category = Category.query.get_or_404(id)

    deals = Deal.query.filter_by(
        category_id=id
    ).order_by(
        Deal.created_at.desc()
    ).all()

    return render_template(
        "category_detail.html",
        category=category,
        deals=deals
    )


# =====================================================
# Store Details
# =====================================================

@main.route("/store/<int:id>")
def store_detail(id):

    store = Store.query.get_or_404(id)

    deals = Deal.query.filter_by(
        store_id=id
    ).order_by(
        Deal.created_at.desc()
    ).all()

    return render_template(
        "store_detail.html",
        store=store,
        deals=deals
    )
# =====================================================
# Live Search API
# =====================================================

@main.route("/search")
def search():

    q = request.args.get("q", "").strip()

    if not q:
        return jsonify([])

    deals = Deal.query.filter(
        Deal.title.ilike(f"%{q}%")
    ).limit(8).all()

    results = []

    for deal in deals:

        results.append({

            "title": deal.title,
            "slug": deal.slug,
            "price": deal.new_price,
            "image": deal.image

        })

    return jsonify(results)




# Privacy Policy
@main.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy_policy.html")


# Terms & Conditions
@main.route("/terms-and-conditions")
def terms_conditions():
    return render_template("terms_conditions.html")


# Affiliate Disclosure
@main.route("/affiliate-disclosure")
def affiliate_disclosure():
    return render_template("affiliate_disclosure.html")


# Disclaimer
@main.route("/disclaimer")
def disclaimer():
    return render_template("disclaimer.html")


# Cookie Policy
@main.route("/cookie-policy")
def cookie_policy():
    return render_template("cookie_policy.html")