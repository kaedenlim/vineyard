import axiosClient from "./axiosClient";

export interface ScrapeProduct {
  title: string;
  price: string;
  image?: string;
  link?: string;
}

export interface ScrapeResults {
  scraped_data: ScrapeProduct[];
  timestamp: string;
  average_price: string;
  product_type_image?: string;
}

export interface AllScrapeResults {
  lazada_results: ScrapeResults;
  carousell_results: ScrapeResults;
}

export const scrape = async (product_name: string): Promise<AllScrapeResults> => {
  try {
    const response = await axiosClient.post<AllScrapeResults>(
      `/scrape/${product_name}`
    );
    return response.data;
  } catch (error) {
    console.error("Error scraping", error);
    throw error;
  }
};
