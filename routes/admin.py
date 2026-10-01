import os
from datetime import datetime
from services.product_fetcher import ProductFetcher
from services.ai_import_service import generate_ai_deal

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    current_app,
    flash
)

from werkzeug.utils import secure_filename

from extensions import db
from models.store import Store
from models.category import Category
from models.deal import Deal
from models.blog import Blog
from services.ai_importer import import_from_ai
from services.ai_import_service import generate_ai_deal
from services.queue_service import QueueService
from services.publish_service import publish_next_product



admin = Blueprint("admin", __name__, url_prefix="/admin")


# =====================================================
# Dashboard
# =====================================================

@admin.route("/")
def dashboard():

    total_deals = Deal.query.count()
    total_blogs = Blog.query.count()
    total_categories = Category.query.count()
    total_stores = Store.query.count()

    latest_deals = Deal.query.order_by(
        Deal.created_at.desc()
    ).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_deals=total_deals,
        total_blogs=total_blogs,
        total_categories=total_categories,
        total_stores=total_stores,
        latest_deals=latest_deals
    )

# =====================================================
# Stores List
# =====================================================

@admin.route("/stores")
def stores():

    stores = Store.query.order_by(Store.id.desc()).all()

    return render_template(
        "admin/stores.html",
        stores=stores
    )


# =====================================================
# Add Store
# =====================================================

@admin.route("/stores/add", methods=["GET", "POST"])
def add_store():

    if request.method == "POST":

        upload_folder = os.path.join(
            current_app.static_folder,
            "logos"
        )

        os.makedirs(upload_folder, exist_ok=True)

        logo_name = ""

        logo = request.files.get("logo")

        if logo and logo.filename:

            logo_name = secure_filename(logo.filename)

            logo.save(
                os.path.join(upload_folder, logo_name)
            )

        store = Store(

            name=request.form.get("name"),
            website=request.form.get("website"),
            logo=logo_name

        )

        db.session.add(store)
        db.session.commit()

        flash("Store added successfully.", "success")

        return redirect(url_for("admin.stores"))

    return render_template("admin/add_store.html")
# =====================================================
# Categories
# =====================================================

@admin.route("/categories")
def categories():

    categories = Category.query.all()

    return render_template(
        "admin/categories.html",
        categories=categories
    )


@admin.route("/categories/add", methods=["GET", "POST"])
def add_category():

    if request.method == "POST":

        category = Category(

            name=request.form["name"],

            slug=request.form["slug"]

        )

        db.session.add(category)
        db.session.commit()

        return redirect(url_for("admin.categories"))

    return render_template("admin/add_category.html")


# =====================================================
# Deals List
# =====================================================

@admin.route("/deals")
def deals():

    deals = Deal.query.order_by(
        Deal.id.desc()
    ).all()

    return render_template(
        "admin/deals.html",
        deals=deals
    )


# =====================================================
# Add Deal
# =====================================================

# =====================================================
# Add Deal
# =====================================================

@admin.route("/deals/add", methods=["GET", "POST"])
def add_deal():

    stores = Store.query.all()
    categories = Category.query.all()
    if store is None:
        return {
            "status": "error",
            "message": "Amazon store not found"
        }, 404

    if category is None:
        return {
            "status": "error",
            "message": "Computers category not found"
        }, 404

    if request.method == "POST":

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        # ==========================================
        # Product Image Upload
        # ==========================================

        filename = ""

        image = request.files.get("image")

        if image and image.filename:

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(upload_folder, filename)
            )

        # ==========================================
        # Program Logo Upload
        # ==========================================

        program_logo = ""

        logo = request.files.get("program_logo")

        if logo and logo.filename:

            program_logo = secure_filename(logo.filename)

            logo.save(
                os.path.join(upload_folder, program_logo)
            )

        # ==========================================
        # Form Data
        # ==========================================

        title = (request.form.get("title") or "").strip()

        slug = (request.form.get("slug") or "").strip().lower()

        short_description = request.form.get("short_description")

        affiliate_url = request.form.get("affiliate_url")

        old_price = float(request.form.get("old_price") or 0)

        new_price = float(request.form.get("new_price") or 0)

        discount = int(request.form.get("discount") or 0)

        button_text = request.form.get("button_text") or "View Deal"

        badge = request.form.get("badge")

        store = request.form.get("store")

        category = request.form.get("category")

        featured = "featured" in request.form

        # ==========================================
        # Validation
        # ==========================================

        if not title:

            flash("Product title is required.", "danger")

            return redirect(
                url_for("admin.add_deal")
            )

        if not slug:

            flash("Slug is required.", "danger")

            return redirect(
                url_for("admin.add_deal")
            )

        if not store:

            flash("Please select a store.", "danger")

            return redirect(
                url_for("admin.add_deal")
            )

        if not category:

            flash("Please select a category.", "danger")

            return redirect(
                url_for("admin.add_deal")
            )

        if old_price < 0 or new_price < 0:

            flash("Price cannot be negative.", "danger")

            return redirect(
                url_for("admin.add_deal")
            )

        # ==========================================
        # Slug Check
        # ==========================================

        existing = Deal.query.filter_by(
            slug=slug
        ).first()

        if existing:

            flash(
                "This slug already exists. Please choose another slug.",
                "danger"
            )

            return redirect(
                url_for("admin.add_deal")
            )

        # ==========================================
        # Create Deal
        # ==========================================

        deal = Deal(

            title=title,

            slug=slug,

            short_description=short_description,

            image=filename,

            program_logo=program_logo,

            affiliate_url=affiliate_url,

            old_price=old_price,

            new_price=new_price,

            discount=discount,

            button_text=button_text,

            badge=badge,

            featured=featured,

            store_id=int(store),

            category_id=int(category)

        )

        # ==========================================
        # Save
        # ==========================================

        db.session.add(deal)

        db.session.commit()

        flash(
            "Deal added successfully.",
            "success"
        )

        return redirect(
            url_for("admin.deals")
        )

    return render_template(

        "admin/add_deal.html",

        stores=stores,

        categories=categories

    )



# =====================================================
# Edit Deal
# =====================================================

@admin.route("/deals/edit/<int:id>", methods=["GET", "POST"])
def edit_deal(id):

    deal = Deal.query.get_or_404(id)

    stores = Store.query.all()
    categories = Category.query.all()

    if request.method == "POST":

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        # Product Image
        image = request.files.get("image")

        if image and image.filename:

            filename = secure_filename(image.filename)
            image.save(os.path.join(upload_folder, filename))
            deal.image = filename

        # Program Logo
        logo = request.files.get("program_logo")

        if logo and logo.filename:

            program_logo = secure_filename(logo.filename)
            logo.save(os.path.join(upload_folder, program_logo))
            deal.program_logo = program_logo

        deal.title = request.form.get("title")
        deal.slug = request.form.get("slug")
        deal.short_description = request.form.get("description")
        deal.affiliate_url = request.form.get("affiliate_url")

        deal.old_price = float(request.form.get("old_price") or 0)
        deal.new_price = float(request.form.get("new_price") or 0)
        deal.discount = int(request.form.get("discount") or 0)

        deal.button_text = request.form.get("button_text")
        deal.badge = request.form.get("badge")

        deal.store_id = int(request.form.get("store"))
        deal.category_id = int(request.form.get("category"))

        deal.featured = "featured" in request.form

        db.session.commit()

        return redirect(url_for("admin.deals"))

    return render_template(
        "admin/edit_deal.html",
        deal=deal,
        stores=stores,
        categories=categories
    )


# =====================================================
# Delete Deal
# =====================================================

@admin.route("/deals/delete/<int:id>", methods=["POST"])
def delete_deal(id):

    deal = Deal.query.get_or_404(id)

    if deal.image:

        image_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            deal.image
        )

        if os.path.exists(image_path):
            os.remove(image_path)

    if deal.program_logo:

        logo_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            deal.program_logo
        )

        if os.path.exists(logo_path):
            os.remove(logo_path)

    db.session.delete(deal)
    db.session.commit()

    return redirect(url_for("admin.deals"))


# =====================================================
# Blogs List
# =====================================================

from models.blog import Blog


@admin.route("/blogs")
def blogs():

    blogs = Blog.query.order_by(
        Blog.id.desc()
    ).all()

    return render_template(
        "admin/blogs.html",
        blogs=blogs
    )


# =====================================================
# Add Blog
# =====================================================

@admin.route("/blogs/add", methods=["GET", "POST"])
def add_blog():

    if request.method == "POST":

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        image_name = ""

        image = request.files.get("image")

        if image and image.filename:

            image_name = secure_filename(image.filename)

            image.save(
                os.path.join(upload_folder, image_name)
            )

        blog = Blog(

            title=request.form.get("title"),

            slug=request.form.get("slug"),

            image=image_name,

            short_description = request.form.get("short_description") or "",

            content=request.form.get("content"),

            featured=("featured" in request.form)

        )

        db.session.add(blog)
        db.session.commit()

        return redirect(url_for("admin.blogs"))

    return render_template("admin/add_blog.html")


# =====================================================
# Edit Blog
# =====================================================

@admin.route("/blogs/edit/<int:id>", methods=["GET", "POST"])
def edit_blog(id):

    blog = Blog.query.get_or_404(id)

    if request.method == "POST":

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        image = request.files.get("image")

        if image and image.filename:

            image_name = secure_filename(image.filename)

            image.save(
                os.path.join(upload_folder, image_name)
            )

            blog.image = image_name

        blog.title = request.form.get("title")
        blog.slug = request.form.get("slug")
        blog.short_description = request.form.get("short_description")
        blog.content = request.form.get("content")
        blog.featured = "featured" in request.form

        db.session.commit()

        return redirect(url_for("admin.blogs"))

    return render_template(
        "admin/edit_blog.html",
        blog=blog
    )


# =====================================================
# Delete Blog
# =====================================================

@admin.route("/blogs/delete/<int:id>")
def delete_blog(id):

    blog = Blog.query.get_or_404(id)

    if blog.image:

        image_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            blog.image
        )

        if os.path.exists(image_path):

            os.remove(image_path)

    db.session.delete(blog)
    db.session.commit()

    return redirect(url_for("admin.blogs"))


@admin.route("/import-ai", methods=["POST"])
def import_ai():

    product = {
        "title": "ASUS TUF Gaming Laptop RTX 4060",
        "brand": "ASUS",
        "price": 299999,
        "description": "Gaming Laptop"
    }

    article = import_from_ai(product)

    store = Store.query.filter_by(name="Amazon").first()
    category = Category.query.filter_by(name="Computers").first()

    deal = Deal(
        title=article["title"],
        slug=article["slug"],
        short_description=article["short_description"],
        meta_description=article["meta_description"],
        review=article["review"],
        buying_guide=article["buying_guide"],
        ai_generated=True,
        store_id=store.id,
        category_id=category.id
    )

    db.session.add(deal)
    db.session.commit()

    return {
        "status": "success",
        "deal_id": deal.id
    }

@admin.route("/generate-ai")
def generate_ai():

    return publish_next_product()