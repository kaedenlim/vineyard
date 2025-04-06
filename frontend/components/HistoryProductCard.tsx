// components/OnboardProductCard.tsx
'use client'
import React from 'react'
import { HistoryProductCard } from '@/types'
import Image from 'next/image'
import Link from 'next/link'

export default function HistoryProductCardComponent({ title, price, image, link, discount, page_ranking }: HistoryProductCard) {
    // Convert the decimal discount to a percentage string if greater than 0; otherwise "None"
    const discountPercentage = discount && discount > 0 ? `${Math.round(discount * 100)}%` : "None";
  
    return (
      <Link href={link} target="_blank">
        <div className='h-[200px] w-[140px] p-2 rounded-xl bg-[#f8f8f8] hover:shadow-lg transition'>
          <div className='w-full h-[70%]'>
            <Image
              src={image}
              height={1000}
              width={1000}
              alt={title}
              className='w-full h-full object-cover rounded-lg'
            />
          </div>
          <div className='mt-2 grid grid-cols-12 gap-2 text-black'>
            <div className='col-span-8 font-bold line-clamp-2 text-xs'>{title}</div>
            <div className='col-span-4 text-right font-medium text-sm'>${price}</div>
          </div>
          <div className='mt-1 text-[#585858] text-[10px] font-medium flex justify-between items-center w-full'>
            <div className='text-left pr-3'>{page_ranking}</div>
            <div className='text-right'>Discount: 
              { discount && discount > 0 ? (
                <span className="pl-1 text-red-500">{discountPercentage}</span>
              ) : (
                <span className='pl-1'>{discountPercentage}</span>
              )}
            </div>
          </div>
        </div>
      </Link>
    );
  }
