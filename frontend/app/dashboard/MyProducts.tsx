// app/page.tsx
'use client'
import React from "react"
import { DashboardProductCard } from "@/types"
import DashboardProductCardComponent from "@/components/DashboardProductCard"
import { useRouter } from "next/navigation"
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel"

interface MyProductsPageProps {
  products: DashboardProductCard[]
}

export default function MyProductsPage({ products }: MyProductsPageProps) {
  const router = useRouter();

  return (
    <div className="space-y-1 max-w-[70vw]">
        <section>
            <Carousel orientation="horizontal">
            <CarouselContent>
                {products.map((product, index) => (
                  <CarouselItem key={`carousell-${index}`} className="basis-1/8">
                      <DashboardProductCardComponent {...product} />
                  </CarouselItem>
                ))}
                {products.length == 0 && (
                    <div className="w-full bg-[#f7f7f7] text-md h-[120px] text-center py-12 rounded-lg ml-4 text-gray-400">No listings found for this platform</div>
                )}
            </CarouselContent>
            <CarouselPrevious />
            <CarouselNext />
            </Carousel>
        </section>
    </div>
  )
}