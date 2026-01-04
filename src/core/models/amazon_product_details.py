from pydantic import BaseModel, Field


class SentimentDetail(BaseModel):
    total: int
    positive: int
    negative: int


class CustomersSay(BaseModel):
    summary: str
    select_to_learn_more: dict[str, SentimentDetail] = Field(default_factory=dict)


class ChatbotReviewSnippet(BaseModel):
    stars: int
    title: str
    review: str
    verified_purchase: bool


class ChatbotProductView(BaseModel):
    name: str
    brand: str | None = Field(default=None)
    price: str | None = Field(default=None)
    availability: str | None = Field(default=None)
    average_rating: float | None = Field(default=None)
    total_reviews: int | None = Field(default=None)
    customers_summary: str | None = Field(default=None)
    sentimental_details: dict[str, dict[str, int]] | None = Field(default_factory=dict)
    images: list[str] = Field(default_factory=list)


class AmazonProductDetails(BaseModel):
    name: str
    brand: str | None = Field(default=None)
    pricing: str | None = Field(default=None)
    availability_status: str | None = Field(default=None)
    average_rating: float | None = Field(default=None)
    total_reviews: int | None = Field(default=None)
    images: list[str] = Field(default_factory=list)
    customers_say: CustomersSay | None = Field(default=None)

    def to_chatbot_view(
        self,
    ) -> ChatbotProductView:
        sentimental_details: dict[str, dict[str, int]] | None = None
        if self.customers_say:
            sentimental_details = {
                k: v.model_dump()
                for k, v in self.customers_say.select_to_learn_more.items()
            }

        return ChatbotProductView(
            name=self.name,
            brand=self.brand,
            price=self.pricing,
            availability=self.availability_status,
            average_rating=self.average_rating,
            total_reviews=self.total_reviews,
            customers_summary=self.customers_say.summary
            if self.customers_say
            else None,
            sentimental_details=sentimental_details,
            images=self.images[:3],
        )
