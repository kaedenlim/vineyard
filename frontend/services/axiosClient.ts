import axios from "axios"

const axiosClient = axios.create({
    // need change this to env var
    baseURL: 'http://127.0.0.1:8000',
    headers: {
        "Content-Type": "application/json"
    }
})

// Response interceptor for handling errors globally
axiosClient.interceptors.response.use(
    (response) => response,
    async (error) => {
      return Promise.reject(error);
    },
  );
  
  export default axiosClient;