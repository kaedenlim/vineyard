"use client"

import { useState, useEffect } from 'react'
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

interface PriceData {
  date: string
  price: number
}

interface PriceGraphProps {
  data: PriceData[]
  color: string
}

export function PriceGraph({ data, color }: PriceGraphProps) {
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
  }, [])

  if (!isMounted) {
    return (
      <div className="h-[100px] bg-gray-100 flex items-center justify-center">
        Loading chart...
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="h-[100px] bg-gray-100 flex items-center justify-center">
        No data available
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={100}>
      <LineChart data={data}>
        <XAxis
          dataKey="date"
          stroke="#888888"
          fontSize={10}
          tickLine={false}
          axisLine={false}
          tick={false}
        />
        <YAxis
          stroke="#888888"
          fontSize={10}
          tickLine={false}
          axisLine={false}
          domain={['dataMin', 'dataMax']}
          tickFormatter={(value) => `$${value}`}
          width={30}
        />
        <Tooltip
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              return (
                <div className="rounded-lg border bg-background p-2 shadow-sm">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="flex flex-col">
                      <span className="text-[0.65rem] uppercase text-muted-foreground">
                        Date
                      </span>
                      <span className="font-bold text-muted-foreground text-[0.65rem]">
                        {payload[0].payload.date}
                      </span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[0.65rem] uppercase text-muted-foreground">
                        Price
                      </span>
                      <span className="font-bold text-[0.65rem]">
                        ${payload[0].value}
                      </span>
                    </div>
                  </div>
                </div>
              )
            }
            return null
          }}
        />
        <Line
          type="monotone"
          dataKey="price"
          stroke={color}
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
