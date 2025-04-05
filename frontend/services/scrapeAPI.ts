import axiosClient from "./axiosClient";

export interface ScrapeProduct {
  title: string;
  price: number;
  image?: string;
  link?: string;
  discount: number;
  page_ranking: number;
}

export interface ScrapeResults {
  scraped_data: ScrapeProduct[];
  timestamp: string;
  average_price: string;
  product_type_image?: string;
}

export interface InsightsData {
  carousell_average_price: number
  carousell_top_listings: ScrapeProduct[];
}

export interface AllScrapeResults {
  lazada_results: ScrapeResults;
  carousell_results: ScrapeResults;
  insights_data: InsightsData;
}

export const scrape = async (product_name: string): Promise<AllScrapeResults> => {
  try {
    const response = await axiosClient.post<AllScrapeResults>(
      `/scrape`, { product: product_name }
    );
    return response.data;
  } catch (error) {
    console.error("Error scraping", error);
    throw error;
  }
};
