import axiosClient from "./axiosClient";
import { ScrapeProduct, ScrapeResults, AllScrapeResults } from "./scrapeAPI";

interface InsightsResponse {
  insights: string;
}

export const getInsights = async (
  product_name: string,
  scrapedData: AllScrapeResults
): Promise<InsightsResponse> => {
  try {
    const allScrapedData = {
      lazada_data: scrapedData.lazada_results.scraped_data,
      carousell_data: scrapedData.carousell_results.scraped_data,
    };
    const response = await axiosClient.post<InsightsResponse>(
      `/insights/${product_name}`,
      {
        product_name: product_name,
        all_scraped_data: allScrapedData,
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching insights", error);
    throw error;
  }
};
