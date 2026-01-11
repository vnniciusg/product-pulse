import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { Product } from "@/types"
import { ExternalLink, ShoppingCart, Star } from "lucide-react"

export const ProductCard: React.FC<{
    product: Product
}> = ({ product }) => {
    return (
        <Card className="group h-full flex flex-col overflow-hidden hover:shadow-lg transition-all duration-300 border-border/60 bg-card/90 backdrop-blur-sm p-0 gap-0">
            <a href={product.url} target="_blank" rel="noopener noreferrer" className="block h-full flex flex-col">
                <div className="relative aspect-square bg-white overflow-hidden shrink-0 p-2">
                    {product.images && product.images.length > 0 ? (
                        <img
                            src={product.images[0] || "/placeholder.svg"}
                            alt={product.name}
                            className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
                        />
                    ) : (
                        <div className="w-full h-full flex items-center justify-center">
                            <ShoppingCart className="w-12 h-12 text-muted-foreground/30" />
                        </div>
                    )}

                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300 flex items-center justify-center">
                        <ExternalLink className="w-6 h-6 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    </div>
                </div>

                <div className="p-3 flex flex-col flex-1 gap-1.5">
                    <div className="space-y-1">
                        <h4 className="font-semibold text-sm line-clamp-2 leading-tight text-foreground group-hover:text-primary transition-colors">
                            {product.name}
                        </h4>

                        {product.brand && <p className="text-xs text-muted-foreground line-clamp-1">{product.brand}</p>}
                    </div>

                    {product.average_rating && (
                        <div className="flex items-center gap-2 mt-auto pt-2">
                            <div className="flex items-center gap-1">
                                <Star className="w-3 h-3 fill-yellow-500 text-yellow-500" />
                                <span className="text-xs font-medium">{product.average_rating.toFixed(1)}</span>
                            </div>
                            {product.total_reviews && (
                                <span className="text-xs text-muted-foreground">({product.total_reviews.toLocaleString()})</span>
                            )}
                        </div>
                    )}

                    <div className="flex items-start justify-between pt-2 border-t border-border/40 mt-auto gap-2">
                        {product.price ? (
                            <span className="text-base font-bold text-primary">{product.price}</span>
                        ) : (
                            <span className="text-sm text-muted-foreground">Ver preço</span>
                        )}

                        {product.availability && (
                            <span
                                className={cn(
                                    "text-[10px] leading-tight font-medium px-2 py-1 rounded-md text-right",
                                    product.availability.toLowerCase().includes("stock")
                                        ? "bg-green-500/10 text-green-600 dark:text-green-400"
                                        : "bg-red-500/10 text-red-600 dark:text-red-400",
                                )}
                            >
                                {product.availability}
                            </span>
                        )}
                    </div>
                </div>
            </a>
        </Card>
    )
}