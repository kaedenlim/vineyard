// app/page.tsx
'use client'
import React from "react"
import { ProfileScrapeResponse } from "@/types"
import OnboardProductCard from "@/components/OnboardProductCard"
import { useRouter } from "next/navigation"
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel"

interface MyProductsPageProps {
  products: ProfileScrapeResponse
}

export default function MyProductsPage({ products }: MyProductsPageProps) {
  const { shopee, lazada, carousell } = products;
  const router = useRouter();

  return (
    <div className="space-y-1 max-w-[70vw]">
        <section>
            <Carousel orientation="horizontal">
            <CarouselContent>
                {carousell.map((product, index) => (
                <CarouselItem key={`carousell-${index}`} className="basis-1/8">
                    <OnboardProductCard {...product} />
                </CarouselItem>
                ))}
                {carousell.length == 0 && (
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