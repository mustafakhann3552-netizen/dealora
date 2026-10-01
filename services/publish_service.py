from services.queue_service import QueueService
from services.ai_import_service import generate_ai_deal


def publish_next_product():

    queue = QueueService()

    product = queue.peek()

    if product is None:
        return {
            "status": "No Product Found"
        }

    deal = generate_ai_deal(product)

    # Sirf successful publish ke baad remove karo
    queue.remove()

    return {
        "status": "success",
        "id": deal.id,
        "title": deal.title,
        "slug": deal.slug
    }