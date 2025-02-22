'use client'

import React from "react";
import { ProductCardInfo } from "@/types";
import ProductCard from "@/components/ui/ProductCard";
import { testdata } from "@/testdata";
import { useParams } from "next/navigation";

export default function SearchResults() {
    const params = useParams();
    const productQuery = params.product; // Access the [query] parameter
    return (
        <div>
            <div className="w-full h-[50px] p-8 text-lg">Search results for <span className="font-bold">{productQuery}</span>:</div>
            <div className="flex flex-wrap justify-center items-center gap-4">
                {testdata.map((item) => (
                    <ProductCard {...item} />
                ))}
            </div>
        </div>
    )
}