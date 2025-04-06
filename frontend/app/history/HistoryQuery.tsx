import React from "react";
import HistoryProductCardComponent from "@/components/HistoryProductCard";
import { HistoryProductQuery } from "@/types";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";

interface HistoryQueryBlockProps {
  query: HistoryProductQuery;
}

export default function HistoryQueryBlock({ query }: HistoryQueryBlockProps) {
  const {
    product_query,
    carousell_average_price,
    lazada_average_price,
    timestamp,
    insights,
    lazada_products,
    carousell_products,
  } = query;

  return (
    <div className="max-w-[70vw] grid grid-cols-12 gap-12 max-h-[450px] bg-[#fcfcfc] rounded-lg">
      <div className="col-span-5 p-4">
        <h3 className="text-lg font-bold mb-2">{product_query}</h3>
        <p className="text-sm text-gray-600 mb-1">
          <span className="font-semibold">Carousell Avg Price:</span> $
          {carousell_average_price.toFixed(2)}
        </p>
        <p className="text-sm text-gray-600 mb-1">
          <span className="font-semibold">Lazada Avg Price:</span> $
          {lazada_average_price.toFixed(2)}
        </p>
        <p className="text-xs text-gray-500 mb-2">{timestamp}</p>
        <div className="text-sm text-gray-700">
          <strong>Insights:</strong>
          <div className="mt-1 whitespace-pre-wrap max-h-[300px] overflow-y-auto border p-2 rounded">
            {insights}
          </div>
        </div>
      </div>

      <div className="col-span-7 space-y-1">
        <div className="text-sm font-semibold">Lazada</div>
        <section>
          <Carousel orientation="horizontal">
            <CarouselContent>
              {lazada_products.map((product, index) => (
                <CarouselItem key={`lazada-${index}`} className="basis-1/8">
                  <HistoryProductCardComponent {...product} />
                </CarouselItem>
              ))}
              {lazada_products.length === 0 && (
                <div className="w-full bg-[#f7f7f7] text-md h-[120px] text-center py-12 rounded-lg ml-4 text-gray-400">
                  No listings found for this platform
                </div>
              )}
            </CarouselContent>
            <CarouselPrevious />
            <CarouselNext />
          </Carousel>
        </section>
        <div className="text-sm font-semibold">Carousell</div>
        <section>
          <Carousel orientation="horizontal">
            <CarouselContent>
              {carousell_products.map((product, index) => (
                <CarouselItem key={`carousell-${index}`} className="basis-1/8">
                  <HistoryProductCardComponent {...product} />
                </CarouselItem>
              ))}
              {carousell_products.length === 0 && (
                <div className="w-full bg-[#f7f7f7] text-md h-[120px] text-center py-12 rounded-lg ml-4 text-gray-400">
                  No listings found for this platform
                </div>
              )}
            </CarouselContent>
            <CarouselPrevious />
            <CarouselNext />
          </Carousel>
        </section>
      </div>
    </div>
  );
}