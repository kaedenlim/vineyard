import axiosClient from './axiosClient'
 import { RecentActivityInfo, DashboardInsightData, ProfileScrapeResponse } from '@/types';
 
 export const getMyProducts = async (id : string):Promise<ProfileScrapeResponse> => {
     try {
         const response = await axiosClient.post<ProfileScrapeResponse>(`/dashboard`, id);
         return response.data;
     } catch (error) {
         console.error("Error getting profile products", error);
         throw error;
     }
 }
 
 export const getMyRecentActivity = async (id : string):Promise<RecentActivityInfo[]> => {
     try {
         const response = await axiosClient.post<RecentActivityInfo[]>(`/dashboard`, id);
         return response.data;
     } catch (error) {
         console.error("Error getting profile products", error);
         throw error;
     }
 }
 
 export const getMyProductInsights = async (id : string):Promise<DashboardInsightData> => {
     try {
         const response = await axiosClient.post<DashboardInsightData>(`/dashboard`, id);
         return response.data;
     } catch (error) {
         console.error("Error getting profile products", error);
         throw error;
     }
 }