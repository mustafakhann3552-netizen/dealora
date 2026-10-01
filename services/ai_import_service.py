from models.deal import Deal
from models.category import Category
from models.store import Store

from extensions import db
from services.ai_importer import import_from_ai


def generate_ai_deal(product):

    # AI API se data lo
    data = import_from_ai(product)

    # Default Category
    category = Category.query.first()

    # Default Store
    store = Store.query.first()

    if not category:
        raise Exception("No category found in database")

    if not store:
        raise Exception("No store found in database")

    # Deal create
    deal = Deal(

        # Basic Information
        title=data["title"],
        slug=data["slug"],
        short_description=data["summary"],
        meta_description=data["meta_description"],
        review=data["review"],
        buying_guide=data["buying_guide"],

        ai_generated=True,

        # Images
        image=data.get("image"),
        program_logo=store.logo,

        # Links
        affiliate_url=data.get("affiliate_url"),

        # Pricing
        new_price=data.get("price", 0),
        old_price=data.get("old_price", 0),
        discount=data.get("discount", 0),

        # Product Card
        button_text="View Deal",
        badge="AI Deal",

        featured=False,

        # Relations
        category_id=category.id,
        store_id=store.id
    )

    db.session.add(deal)
    db.session.commit()

    return deal