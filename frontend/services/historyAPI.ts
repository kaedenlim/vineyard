import axiosClient from './axiosClient'
 import { HistoryResponse } from '@/types';
 
 export const getMyHistory = async (username : string):Promise<HistoryResponse> => {
     try {
         const response = await axiosClient.post<HistoryResponse>(`/history`, username);
         return response.data;
     } catch (error) {
         console.error("Error getting history", error);
         throw error;
     }
 }