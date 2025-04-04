// components/OnboardProductCard.tsx
'use client'
import React from 'react'
import { ProductCardInfo } from '@/types'
import Image from 'next/image'
import Link from 'next/link'

export default function OnboardProductCard({ title, price, image, link }: ProductCardInfo) {
  return (
    <Link href={link} target="_blank">
      <div className='h-[160px] w-[140px] p-2 rounded-xl bg-[#f8f8f8] hover:shadow-lg transition'>
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
      </div>
    </Link>
  )
}
