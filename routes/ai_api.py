from flask import Blueprint, request, jsonify, current_app
import os
import uuid
from urllib.parse import urlparse

import requests
from werkzeug.utils import secure_filename

from extensions import db
from models.deal import Deal
from models.store import Store
from models.category import Category


ai_api = Blueprint(
    "ai_api",
    __name__,
    url_prefix="/api/ai"
)


# ==========================================================
# Helpers
# ==========================================================

def _make_unique_slug(base_slug):
    """
    Make sure the deal slug is unique.
    """

    base_slug = (base_slug or "").strip().lower()

    if not base_slug:
        raise ValueError("slug is required")

    slug = base_slug
    counter = 2

    while Deal.query.filter_by(slug=slug).first() is not None:
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


def _find_existing_deal(affiliate_url):
    """
    Find an existing AI deal using its affiliate URL.

    The affiliate URL identifies the actual affiliate offer,
    so publishing the same offer again should not create
    another website deal.
    """

    affiliate_url = (affiliate_url or "").strip()

    if not affiliate_url:
        return None

    return Deal.query.filter_by(
        affiliate_url=affiliate_url
    ).first()


def _is_http_url(value):
    """
    Check whether a value is a safe HTTP/HTTPS URL.
    """

    value = (value or "").strip()

    if not value:
        return False

    try:
        parsed = urlparse(value)
    except Exception:
        return False

    return parsed.scheme.lower() in ("http", "https") and bool(
        parsed.netloc
    )


def _extension_from_content_type(content_type):
    """
    Convert common image content types to file extensions.
    """

    content_type = (
        content_type or ""
    ).split(";")[0].strip().lower()

    mapping = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "image/bmp": ".bmp",
        "image/svg+xml": ".svg",
    }

    return mapping.get(content_type)


def _extension_from_url(image_url):
    """
    Try to detect an image extension from the URL.
    """

    try:
        path = urlparse(image_url).path.lower()
    except Exception:
        return None

    allowed = (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".gif",
        ".bmp",
        ".svg",
    )

    for extension in allowed:
        if path.endswith(extension):
            if extension == ".jpeg":
                return ".jpg"

            return extension

    return None


def _download_image(image_value):
    """
    Download a remote image and save it inside the website's
    configured static/uploads directory.

    Returns the local filename or None if the image cannot
    be downloaded safely.
    """

    image_value = str(
        image_value or ""
    ).strip()

    if not image_value:
        return None

    # ------------------------------------------------------
    # Already-local image
    # ------------------------------------------------------

    if not _is_http_url(image_value):

        # Prevent paths such as:
        # C:\...
        # ../../...
        # file://...
        # etc.

        safe_name = secure_filename(
            os.path.basename(image_value)
        )

        if not safe_name:
            return None

        upload_folder = current_app.config[
            "UPLOAD_FOLDER"
        ]

        local_path = os.path.join(
            upload_folder,
            safe_name
        )

        if os.path.isfile(local_path):
            return safe_name

        return None

    # ------------------------------------------------------
    # Remote HTTP/HTTPS image
    # ------------------------------------------------------

    try:

        response = requests.get(
            image_value,
            timeout=20,
            stream=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(compatible; AI-Affiliate-System/1.0)"
                )
            },
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "Content-Type",
            ""
        )

        extension = _extension_from_content_type(
            content_type
        )

        if extension is None:
            extension = _extension_from_url(
                image_value
            )

        if extension is None:
            extension = ".jpg"

        allowed_extensions = {
            ".jpg",
            ".png",
            ".webp",
            ".gif",
            ".bmp",
            ".svg",
        }

        if extension not in allowed_extensions:
            return None

        # --------------------------------------------------
        # Maximum image size: 10 MB
        # --------------------------------------------------

        max_size = 10 * 1024 * 1024

        content_length = response.headers.get(
            "Content-Length"
        )

        if content_length:

            try:
                if int(content_length) > max_size:
                    return None
            except ValueError:
                pass

        upload_folder = current_app.config[
            "UPLOAD_FOLDER"
        ]

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        # --------------------------------------------------
        # Unique filename
        # --------------------------------------------------

        filename = (
            f"ai_{uuid.uuid4().hex}"
            f"{extension}"
        )

        filepath = os.path.join(
            upload_folder,
            filename
        )

        total_size = 0

        with open(filepath, "wb") as output_file:

            for chunk in response.iter_content(
                chunk_size=64 * 1024
            ):

                if not chunk:
                    continue

                total_size += len(chunk)

                if total_size > max_size:
                    output_file.close()

                    try:
                        os.remove(filepath)
                    except OSError:
                        pass

                    return None

                output_file.write(chunk)

        # --------------------------------------------------
        # Basic verification
        # --------------------------------------------------

        if not os.path.isfile(filepath):
            return None

        if os.path.getsize(filepath) == 0:

            try:
                os.remove(filepath)
            except OSError:
                pass

            return None

        return filename

    except requests.RequestException:
        return None

    except OSError:
        return None

    except Exception:
        return None


# ==========================================================
# AI Deal API
# ==========================================================

@ai_api.route("/deals", methods=["POST"])
def create_ai_deal():
    """
    Receive a completed product/article from AI Affiliate System
    and create or reuse a Deal on the website.
    """

    # ------------------------------------------------------
    # API authentication
    # ------------------------------------------------------

    expected_token = current_app.config.get(
        "AI_WEBSITE_API_TOKEN",
        ""
    ).strip()

    received_token = request.headers.get(
        "X-AI-API-TOKEN",
        ""
    ).strip()

    if not expected_token:

        return jsonify({
            "status": "error",
            "message": (
                "AI website API token is not configured."
            )
        }), 500

    if received_token != expected_token:

        return jsonify({
            "status": "error",
            "message": "Unauthorized."
        }), 401

    # ------------------------------------------------------
    # JSON payload
    # ------------------------------------------------------

    data = request.get_json(
        silent=True
    )

    if not isinstance(data, dict):

        return jsonify({
            "status": "error",
            "message": "JSON body is required."
        }), 400

    # ------------------------------------------------------
    # Required fields
    # ------------------------------------------------------

    required_fields = [
        "title",
        "slug",
        "summary",
        "affiliate_url",
        "store_name",
        "category_name",
    ]

    missing = [
        field
        for field in required_fields
        if not str(
            data.get(field, "")
        ).strip()
    ]

    if missing:

        return jsonify({
            "status": "error",
            "message": "Missing required fields.",
            "missing": missing,
        }), 400

    affiliate_url = str(
        data.get(
            "affiliate_url",
            ""
        )
    ).strip()

    # ------------------------------------------------------
    # Duplicate / idempotency protection
    # ------------------------------------------------------

    existing_deal = _find_existing_deal(
        affiliate_url
    )

    if existing_deal is not None:

        return jsonify({
            "status": "success",
            "message": "AI deal already exists.",
            "duplicate": True,
            "deal": {
                "id": existing_deal.id,
                "title": existing_deal.title,
                "slug": existing_deal.slug,
                "url": (
                    f"/deal/{existing_deal.slug}"
                ),
            }
        }), 200

    # ------------------------------------------------------
    # Store
    # ------------------------------------------------------

    store = Store.query.filter_by(
        name=data["store_name"].strip()
    ).first()

    if store is None:

        return jsonify({
            "status": "error",
            "message": "Store not found.",
            "store_name": data["store_name"],
        }), 400

    # ------------------------------------------------------
    # Category
    # ------------------------------------------------------

    category = Category.query.filter_by(
        name=data["category_name"].strip()
    ).first()

    if category is None:

        return jsonify({
            "status": "error",
            "message": "Category not found.",
            "category_name": data["category_name"],
        }), 400

    # ------------------------------------------------------
    # Slug
    # ------------------------------------------------------

    slug = _make_unique_slug(
        data["slug"]
    )

    # ------------------------------------------------------
    # Image
    # ------------------------------------------------------

    image_filename = _download_image(
        data.get("image")
    )

    # ------------------------------------------------------
    # Prices
    # ------------------------------------------------------

    try:
        old_price = float(
            data.get("old_price") or 0
        )
    except (TypeError, ValueError):
        old_price = 0.0

    try:
        new_price = float(
            data.get("price") or 0
        )
    except (TypeError, ValueError):
        new_price = 0.0

    try:
        discount = int(
            float(
                data.get("discount") or 0
            )
        )
    except (TypeError, ValueError):
        discount = 0

    # ------------------------------------------------------
    # Create Deal
    # ------------------------------------------------------

    deal = Deal(
        title=str(
            data["title"]
        ).strip(),

        slug=slug,

        short_description=str(
            data.get(
                "summary",
                ""
            )
        ).strip(),

        meta_description=str(
            data.get(
                "meta_description",
                ""
            )
        ).strip(),

        review=str(
            data.get(
                "review",
                ""
            )
        ).strip(),

        buying_guide=str(
            data.get(
                "buying_guide",
                ""
            )
        ).strip(),

        ai_generated=True,

        image=image_filename,

        program_logo=store.logo,

        affiliate_url=affiliate_url,

        old_price=old_price,

        new_price=new_price,

        discount=discount,

        button_text="View Deal",

        badge="AI Deal",

        featured=False,

        store_id=store.id,

        category_id=category.id,
    )

    db.session.add(deal)
    db.session.commit()

    # ------------------------------------------------------
    # Response
    # ------------------------------------------------------

    return jsonify({
        "status": "success",
        "message": "AI deal created successfully.",
        "duplicate": False,
        "image_saved": bool(image_filename),
        "image": image_filename,
        "deal": {
            "id": deal.id,
            "title": deal.title,
            "slug": deal.slug,
            "url": (
                f"/deal/{deal.slug}"
            ),
        }
    }), 201



# ==========================================================
# AI MEDIA UPLOAD API
# ==========================================================

@ai_api.route("/media", methods=["POST"])
def upload_ai_media():
    """
    Receive an image/video from AI Affiliate System and save it
    inside static/uploads so it can be accessed through the
    website's public HTTPS URL.
    """

    # ------------------------------------------------------
    # API authentication
    # ------------------------------------------------------

    expected_token = current_app.config.get(
        "AI_WEBSITE_API_TOKEN",
        ""
    ).strip()

    received_token = request.headers.get(
        "X-AI-API-TOKEN",
        ""
    ).strip()

    if not expected_token:

        return jsonify({
            "status": "error",
            "message": (
                "AI website API token is not configured."
            )
        }), 500

    if received_token != expected_token:

        return jsonify({
            "status": "error",
            "message": "Unauthorized."
        }), 401

    # ------------------------------------------------------
    # File validation
    # ------------------------------------------------------

    if "file" not in request.files:

        return jsonify({
            "status": "error",
            "message": "Media file is required."
        }), 400

    uploaded_file = request.files["file"]

    if not uploaded_file.filename:

        return jsonify({
            "status": "error",
            "message": "Media filename is required."
        }), 400

    # ------------------------------------------------------
    # Allowed media types
    # ------------------------------------------------------

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".gif",
        ".mp4",
        ".mov",
        ".m4v",
        ".webm",
    }

    original_filename = secure_filename(
        uploaded_file.filename
    )

    extension = os.path.splitext(
        original_filename
    )[1].lower()

    if extension == ".jpeg":
        extension = ".jpg"

    if extension not in allowed_extensions:

        return jsonify({
            "status": "error",
            "message": (
                "Unsupported media type."
            ),
            "allowed_extensions": sorted(
                allowed_extensions
            ),
        }), 400

    # ------------------------------------------------------
    # Maximum upload size
    # ------------------------------------------------------

    max_size = 100 * 1024 * 1024

    upload_folder = current_app.config[
        "UPLOAD_FOLDER"
    ]

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    filename = (
        f"ai_social_{uuid.uuid4().hex}"
        f"{extension}"
    )

    filepath = os.path.join(
        upload_folder,
        filename
    )

    # ------------------------------------------------------
    # Save media
    # ------------------------------------------------------

    try:

        uploaded_file.save(filepath)

        if not os.path.isfile(filepath):

            return jsonify({
                "status": "error",
                "message": "Media file was not saved."
            }), 500

        file_size = os.path.getsize(
            filepath
        )

        if file_size <= 0:

            try:
                os.remove(filepath)
            except OSError:
                pass

            return jsonify({
                "status": "error",
                "message": "Uploaded media is empty."
            }), 400

        if file_size > max_size:

            try:
                os.remove(filepath)
            except OSError:
                pass

            return jsonify({
                "status": "error",
                "message": (
                    "Media file exceeds the 100 MB limit."
                ),
            }), 413

    except OSError as exc:

        try:
            if os.path.isfile(filepath):
                os.remove(filepath)
        except OSError:
            pass

        return jsonify({
            "status": "error",
            "message": (
                f"Could not save media: {exc}"
            ),
        }), 500

    # ------------------------------------------------------
    # Public URL
    # ------------------------------------------------------

    public_base_url = os.getenv(
        "WEBSITE_PUBLIC_BASE_URL",
        ""
    ).strip().rstrip("/")

    if not public_base_url:

        public_base_url = request.host_url.rstrip("/")

    public_url = (
        f"{public_base_url}"
        f"/static/uploads/{filename}"
    )

    # ------------------------------------------------------
    # Response
    # ------------------------------------------------------

    return jsonify({
        "status": "success",
        "message": "AI media uploaded successfully.",
        "filename": filename,
        "size": file_size,
        "url": public_url,
    }), 201