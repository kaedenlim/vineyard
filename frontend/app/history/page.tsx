'use client'
import React, { useState, useEffect } from "react";
import { HistoryProductQuery, HistoryResponse } from "@/types";
import { getMyHistory } from "@/services/historyAPI";
import LoadingOverlay from "@/components/LoadingOverlay";
import { useUser } from "@clerk/nextjs";
import HistoryQueryBlock from "./HistoryQuery";
import { testHistoryData } from "@/testdata";

export default function Page() {
  // Initialize state as an object with an empty history array
  const [historyData, setHistoryData] = useState<HistoryResponse>({ history: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { user } = useUser();
  const currentUsername = user?.username ?? "";

  useEffect(() => {
    async function fetchHistoryData() {
      try {
        const data = await getMyHistory(currentUsername);
        setHistoryData(data);
        //uncomment below to test
        // setHistoryData(testHistoryData); 
      } catch (err) {
        console.error(err);
        setError("Failed to load history data");
      } finally {
        setLoading(false);
      }
    }
    fetchHistoryData();
  }, [currentUsername]);

  if (loading) {
    return <LoadingOverlay text="Retrieving your history..." />;
  }

  if (error) {
    return <div className="px-12 py-6 text-red-500">{error}</div>;
  }

  return (
    <div>
      <div className="px-12 py-6 font-bold text-xl">My History</div>
      <div className="max-w-[90%] px-12 ml-12">
        {historyData.history.map((query: HistoryProductQuery, index: number) => (
          <HistoryQueryBlock key={index} query={query} />
        ))}
      </div>
    </div>
  );
}
