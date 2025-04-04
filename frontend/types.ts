export type ProductCardInfo = {
    title: string;
    price: number;
    image: string;
    link: string;
};

export type ProfileLinkInfo = {
    shopee: string;
    lazada: string;
    carousell: string;
}

export type ProfileScrapeResponse = {
    shopee: ProductCardInfo[];
    lazada: ProductCardInfo[];
    carousell: ProductCardInfo[];
}