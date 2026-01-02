from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator


class CustomerReviewStat(BaseModel):
    ratings_count: int | None = Field(default=None)
    stars: float


class SentimentDetail(BaseModel):
    total: int
    positive: int
    negative: int


class CustomersSay(BaseModel):
    summary: str
    select_to_learn_more: dict[str, SentimentDetail] = Field(default_factory=dict)


class Review(BaseModel):
    stars: int
    date: str
    verified_purchase: bool
    manufacturer_replied: bool
    username: str
    user_url: HttpUrl | None = None
    title: str
    review: str
    review_url: HttpUrl | None = None
    total_found_helpful: int | None = None
    images: list[str] = Field(default_factory=list)
    variation: dict[str, Any] = Field(default_factory=dict)


class ProductInformation(BaseModel):
    publisher: str | None = None
    publication_date: str | None = None
    edition: str | None = None
    language: str | None = None
    print_length: str | None = None
    isbn_10: str | None = Field(None, alias="isbn_10")
    isbn_13: str | None = Field(None, alias="isbn_13")
    item_weight: str | None = None
    dimensions: str | None = None
    best_sellers_rank: list[str] = Field(default_factory=list)
    customer_reviews: CustomerReviewStat | None = None

    class Config:
        populate_by_name = True


class AmazonProductDetails(BaseModel):
    name: str
    product_information: ProductInformation
    brand: str
    brand_url: HttpUrl | None = None
    full_description: str
    pricing: str
    list_price: str | None = None
    shipping_price: str | None = None
    shipping_time: str | None = None
    shipping_condition: str | None = None
    availability_status: str
    is_coupon_exists: bool
    images: list[str] = Field(default_factory=list)
    high_res_images: list[HttpUrl] = Field(default_factory=list)
    product_category: str
    average_rating: float
    total_reviews: int
    sold_by: str
    aplus_present: bool
    customers_say: CustomersSay | None = Field(default=None)
    total_ratings: int
    five_star_percentage: int = Field(alias="5_star_percentage")
    four_star_percentage: int = Field(alias="4_star_percentage")
    three_star_percentage: int = Field(alias="3_star_percentage")
    two_star_percentage: int = Field(alias="2_star_percentage")
    one_star_percentage: int = Field(alias="1_star_percentage")
    reviews: list[Review] = Field(default_factory=list)

    class Config:
        populate_by_name = True

    @field_validator("pricing", "list_price")
    @classmethod
    def parse_price(cls, v: str | None) -> str | None:
        if v:
            return v.strip()

        return v

    @field_validator("average_rating")
    @classmethod
    def validate_rating(cls, v: float) -> float:
        if not 0 <= v <= 5:
            raise ValueError("Rating must be between 0 and 5")

        return v
