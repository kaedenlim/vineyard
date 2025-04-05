'use client'
 import React, { useState, useEffect } from "react";
 import { MyInsights } from "./MyInsights";
 import { RecentActivity } from "./RecentActivity";
 import MyProductsPage from "./MyProducts";
 import { testDashboardInsightData, testRecentActivityData, testDashboardProductData } from "@/testdata";
 import { ProductActivityResponse, DashboardProductCard, RecentActivityInfo } from "@/types";
 import { getMyProductsAndActivity } from "@/services/dashboardAPI";
 import LoadingOverlay from "@/components/LoadingOverlay";
 
 export default function Page() {
    // call axios endpoint here, get {products, activities} and put it into recentactivity and products
    const [productData, setProductData] = useState<DashboardProductCard[]>([]);
    const [activityData, setActivityData] = useState<RecentActivityInfo[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function fetchDashboardData() {
        try {
            const data = await getMyProductsAndActivity("some-id");
            const {products,activities} = data;
            setProductData(products);
            setActivityData(activities);
        } catch (err) {
            console.error(err);
            setError("Failed to load dashboard data");
        } finally {
            setLoading(false);
        }
        }
        fetchDashboardData();
    }, []);
     return (
         <div>
            {loading && (<LoadingOverlay text="Retrieving your profile..." />)}
             <div className="px-12 py-6 font-bold text-xl">My Dashboard</div>
             <div className="px-16 py-6 text-lg font-semibold">My Products:</div>
             <div className="max-w-[90%] px-12 ml-12">
                 <MyProductsPage products={productData} />
             </div>
             <div className="grid grid-cols-2 gap-8 px-12 py-6 w-[95%] max-h-[40%]">
                 <MyInsights data={testDashboardInsightData} />
                 <RecentActivity data={activityData} />
             </div>
         </div>
     )
 }