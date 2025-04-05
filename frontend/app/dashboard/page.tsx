'use client'
 import React, { useState, useEffect } from "react";
 import { MyInsights } from "./MyInsights";
 import { RecentActivity } from "./RecentActivity";
 import MyProductsPage from "./MyProducts";
 import { testDashboardInsightData, testRecentActivityData, testProfileScrapeResponse } from "@/testdata";
 
 export default function Page() {
     return (
         <div>
             <div className="px-12 py-6 font-bold text-xl">My Dashboard</div>
             <div className="px-16 py-6 text-lg font-semibold">My Products:</div>
             <div className="max-w-[90%] px-12 ml-12">
                 <MyProductsPage products={testProfileScrapeResponse} />
             </div>
             <div className="grid grid-cols-2 gap-8 px-12 py-6 w-[95%] max-h-[40%]">
                 <MyInsights data={testDashboardInsightData} />
                 <RecentActivity data={testRecentActivityData} />
             </div>
         </div>
     )
 }