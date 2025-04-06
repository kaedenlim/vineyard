"use client";
 
 import React, { FC } from "react";
 import {
   LineChart,
   ResponsiveContainer,
   Tooltip,
   XAxis,
   YAxis,
   Legend,
   Line,
 } from "recharts";
 
 interface PriceData {
   date: string;
   price: number;
 }
 
 interface InsightsData {
   [product: string]: PriceData[];
 }
 
 interface MyInsightsProps {
   data: InsightsData;
 }
 
 // Define a color palette for the lines.
 const COLORS = ["#ff5722", "#2196f3", "#4caf50", "#9c27b0", "#ff9800", "#00bcd4"];
 
 /**
  * Merges an object of product price data arrays into one array.
  * Each element corresponds to a date and contains fields for each product's price.
  */
 function mergeData(data: InsightsData): any[] {
   const merged: Record<string, any> = {};
 
   for (const product in data) {
     data[product].forEach((entry) => {
       if (!merged[entry.date]) {
         merged[entry.date] = { date: entry.date };
       }
       merged[entry.date][product] = entry.price;
     });
   }
 
   return Object.values(merged).sort(
     (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
   );
 }
 
 export const MyInsights: FC<MyInsightsProps> = ({ data }) => {
   const mergedData = mergeData(data);
   const productKeys = Object.keys(data);
 
   return (
     <div className="max-w-full max-h-[30vh]">
         <div className="p-4 text-lg font-semibold">Insights</div>
         <div style={{ width: "100%", height: 300 }}>
             <ResponsiveContainer width="100%" height="100%">
                 <LineChart data={mergedData}>
                 <XAxis dataKey="date" />
                 <YAxis tickFormatter={(value) => `$${value}`} />
                 <Tooltip formatter={(value) => `$${value}`} />
                 <Legend />
                 {productKeys.map((product, index) => (
                     <Line
                     key={product}
                     type="monotone"
                     dataKey={product}
                     stroke={COLORS[index % COLORS.length]}
                     strokeWidth={2}
                     dot={false}
                     />
                 ))}
                 </LineChart>
             </ResponsiveContainer>
         </div>
     </div>
   );
 };