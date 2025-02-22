import axiosClient from './axiosClient'

interface ScrapeResults {
    scraped_data: ScrapeProduct[];
    timestamp: string;
    average_price: string;
    product_type_image?: string;
}

interface ScrapeProduct {
    title: string;
    price: string;
    image?: string;
    link?: string;
}

export const scrape = async (product_name : string):Promise<ScrapeResults> => {
    try {
        const response = await axiosClient.get<ScrapeResults>(`/scrape/${product_name}`)
        return response.data
    } catch (error) {
        console.error("Error scraping", error);
        throw error;
    }
}