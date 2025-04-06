export type ProductCardInfo = {
    title: string;
    price: number;
    image: string;
    link: string;
};

export type ProfileLinkInfo = {
    shopee_url: string;
    lazada_url: string;
    carousell_url: string;
}

export type ProfileScrapeResponse = {
    shopee: ProductCardInfo[];
    lazada: ProductCardInfo[];
    carousell: ProductCardInfo[];
}

export type ProductInsightData = {
    date: string;
    price: number;
}

export interface DashboardInsightData {
    [product: string]: ProductInsightData[];
}

export type RecentActivityInfo = {
    activity: string;
    date: string;
}

export type DashboardProductCard = {
    title: string;
    price: number;
    image: string;
    link: string;
    site: string;
    created_at: string;
}

export type ProductActivityResponse = {
    products: DashboardProductCard[];
    activities: RecentActivityInfo[];
}

export type HistoryProductCard = {
    title: string;
    price: number;
    image: string;
    link: string;
    discount: number;
    page_ranking: number;
}

export type HistoryProductQuery = {
    product_query: string;
    carousell_average_price: number;
    lazada_average_price: number;
    timestamp: string;
    insights: string;
    lazada_products: HistoryProductCard[];
    carousell_products: HistoryProductCard[];
}

export type HistoryResponse = {
    history: HistoryProductQuery[];
}