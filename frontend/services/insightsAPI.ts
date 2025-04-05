import axiosClient from "./axiosClient";
import { AllScrapeResults } from "./scrapeAPI";

interface InsightsResponse {
  insights: string;
}

export const getInsights = async (
  product_name: string,
  scrapedData: AllScrapeResults
): Promise<InsightsResponse> => {
  try {
    const response = await axiosClient.post<InsightsResponse>(
      `/insights`,
      {
        product_name: product_name,
        insights_data: scrapedData.insights_data,
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching insights", error);
    throw error;
  }
};
