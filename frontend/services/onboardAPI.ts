import axiosClient from './axiosClient'
import { ProfileLinkInfo, ProfileScrapeResponse } from '@/types';

export const getProfileProducts = async (profile_links : ProfileLinkInfo):Promise<ProfileScrapeResponse> => {
    try {
        console.log(profile_links);
        const response = await axiosClient.post<ProfileScrapeResponse>(`/onboard`, profile_links);
        console.log(response.data);
        return response.data;
    } catch (error) {
        console.error("Error getting profile products", error);
        throw error;
    }
}