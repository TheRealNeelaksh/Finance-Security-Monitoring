import axios from 'axios';

// "import.meta.env.VITE_API_URL" allows us to change the URL 
// in the Vercel dashboard without touching the code.
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;