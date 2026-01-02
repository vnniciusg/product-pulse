from typing import Any

from pydantic import AnyHttpUrl, BaseModel, Field, HttpUrl


class PriceInfo(BaseModel):
    price_string: str
    price_symbol: str
    price: float


class SearchProduct(BaseModel):
    type: str
    position: int
    asin: str
    name: str
    image: HttpUrl
    has_prime: bool
    is_best_seller: bool
    is_amazon_choice: bool
    is_limited_deal: bool
    stars: float
    url: AnyHttpUrl
    price_string: str | None = Field(default=None)
    price_symbol: str | None = Field(default=None)
    price: float | None = Field(default=None)
    original_price: PriceInfo | None = Field(default=None)
    availability_quantity: int | None = Field(default=None)
    purchase_history_message: str | None = Field(default=None)

    @property
    def discount_percentage(self) -> float | None:
        if self.original_price and self.original_price.price > 0:
            discount = (
                (self.original_price.price - self.price) / self.original_price.price
            ) * 100
            return round(discount, 2)

        return None

    @property
    def is_on_sale(self) -> bool:
        return (
            self.original_price is not None and self.price < self.original_price.price
        )


class AmazonSearchResult(BaseModel):
    results: list[SearchProduct] = Field(default_factory=list)
    explore_more_items: list[dict[str, Any]] = Field(default_factory=list)
    next_pages: list[HttpUrl] = Field(default_factory=list)

    @property
    def total_results(self) -> int:
        return len(self.results)

    @property
    def products_on_sale(self) -> list[SearchProduct]:
        return [product for product in self.results if product.is_on_sale]

    @property
    def prime_products(self) -> list[SearchProduct]:
        return [product for product in self.results if product.has_prime]

    @property
    def best_sellers(self) -> list[SearchProduct]:
        return [product for product in self.results if product.is_best_seller]

    @property
    def amazon_choice(self) -> list[SearchProduct]:
        return [product for product in self.results if product.is_amazon_choice]

    def filter_by_rating(self, min_rating: float = 4.5) -> list[SearchProduct]:
        return [product for product in self.results if product.stars >= min_rating]

    def filter_by_price_range(
        self, min_price: float = 0, max_price: float = float("inf")
    ) -> list[SearchProduct]:
        return [
            product
            for product in self.results
            if min_price <= product.price <= max_price
        ]

    def sort_by_price(self, ascending: bool = True) -> list[SearchProduct]:
        return sorted(self.results, key=lambda x: x.price, reverse=not ascending)

    def sort_by_rating(self, ascending: bool = False) -> list[SearchProduct]:
        return sorted(self.results, key=lambda x: x.stars, reverse=not ascending)
