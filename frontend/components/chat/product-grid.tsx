import {
    Carousel,
    CarouselContent,
    CarouselItem,
    CarouselNext,
    CarouselPrevious,
} from "@/components/ui/carousel"
import { Product } from "@/types"
import { ShoppingCart } from "lucide-react"
import { ProductCard } from "./product-card"

export const ProductGrid: React.FC<{
    products: Product[]
}> = ({ products }) => {
    return (
        <div className="w-full space-y-3">
            <div className="flex items-center gap-2 px-2">
                <ShoppingCart className="w-4 h-4 text-primary" />
                <h3 className="text-sm font-semibold text-foreground">Produtos Encontrados</h3>
                <span className="text-xs text-muted-foreground">({products.length})</span>
            </div>

            <div className="w-full px-12">
                <Carousel
                    opts={{
                        align: "start",
                    }}
                    className="w-full"
                >
                    <CarouselContent className="-ml-3">
                        {products.map((product, index) => (
                            <CarouselItem key={index} className="md:basis-1/2 lg:basis-1/4 pl-3">
                                <div className="h-full">
                                    <ProductCard product={product} />
                                </div>
                            </CarouselItem>
                        ))}
                    </CarouselContent>
                    <CarouselPrevious />
                    <CarouselNext />
                </Carousel>
            </div>
        </div>
    )
}
