from models.deal import Deal


class DealMapper:

    @staticmethod
    def map(article, product, store_id, category_id):

        return Deal(
            title=article.title,
            slug=article.slug,
            short_description=article.summary,
            affiliate_url=product.affiliate_url,

            image=product.image,

            new_price=product.price,

            store_id=store_id,
            category_id=category_id
        )