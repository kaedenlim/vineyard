'use client'

import React from 'react';
import { ProductCardInfo } from '@/types';
import Image from 'next/image';

export default function ProductCard(data:ProductCardInfo) {
    return (
        <div className='h-[360px] w-[280px] p-3 rounded-xl bg-[#f8f8f8]'>
            <div className='w-full h-[80%]'>
                <Image src={data.image} height={1000} width={1000} alt={data.title}
                    className='w-full h-full object-fill rounded-lg' />
            </div>
            <div className='mt-3 grid grid-cols-12 gap-4 text-black'>
                <div className='col-span-7 font-bold line-clamp-2'>{data.title}</div>
                <div className='col-span-5 text-right font-medium text-2xl'>${data.price}</div>
            </div>
        </div>
    )
} 