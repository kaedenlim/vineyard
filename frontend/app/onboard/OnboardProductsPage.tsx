// app/page.tsx
'use client'
import React from "react"
import { ProfileScrapeResponse } from "@/types"
import OnboardProductCard from "@/components/OnboardProductCard"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel"

interface OnboardFormPageProps {
  products: ProfileScrapeResponse
}

export default function OnboardProductsPage({ products }: OnboardFormPageProps) {
  const { shopee, lazada, carousell } = products;
  const router = useRouter();

  return (
    <div className="space-y-1 max-w-[80%]">
        <div className="flex justify-between items-center">
            <div className="text-xl font-semibold">Here are your listings we found:</div>
            <Button onClick={() => router.push("/search")}>Go to Dashboard</Button>
        </div>
      {/* Shopee Carousel */}
      <section >
        <h2 className="text-lg font-semibold mb-2">Shopee</h2>
        <Carousel orientation="horizontal">
          <CarouselContent>
            {/* {shopee.map((product, index) => (
              <CarouselItem key={`shopee-${index}`} className="basis-1/8">
                <OnboardProductCard {...product} />
              </CarouselItem>
            ))} */}
          </CarouselContent>
          <CarouselPrevious />
          <CarouselNext />
        </Carousel>
      </section>

      {/* Lazada Carousel */}
      <section>
        <h2 className="text-lg font-semibold mb-2">Lazada</h2>
        <Carousel orientation="horizontal">
          <CarouselContent>
            {lazada.map((product, index) => (
              <CarouselItem key={`lazada-${index}`} className="basis-1/8">
                <OnboardProductCard {...product} />
              </CarouselItem>
            ))}
          </CarouselContent>
          <CarouselPrevious />
          <CarouselNext />
        </Carousel>
      </section>

      {/* Carousell Carousel */}
      <section>
        <h2 className="text-lg font-semibold mb-2">Carousell</h2>
        <Carousel orientation="horizontal">
          <CarouselContent>
            {carousell.map((product, index) => (
              <CarouselItem key={`carousell-${index}`} className="basis-1/8">
                <OnboardProductCard {...product} />
              </CarouselItem>
            ))}
          </CarouselContent>
          <CarouselPrevious />
          <CarouselNext />
        </Carousel>
      </section>
    </div>
  )
}
