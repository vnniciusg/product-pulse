export interface Product {
    name: string
    brand: string
    price: string | null
    availability: string | null
    average_rating: number | null
    total_reviews: number | null
    images: string[]
    url: string
}

export interface Message {
    role: "user" | "assistant"
    content: string
    timestamp: Date
    products?: Product[]
}