/**
 * API Client Configuration
 */

const API_BASE_URL = 'http://localhost:8000';
const WS_BASE_URL = 'ws://localhost:8000';

export const apiClient = {
    baseUrl: API_BASE_URL,
    wsUrl: WS_BASE_URL,

    async get<T>(endpoint: string): Promise<T> {
        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        return response.json();
    },

    async post<T>(endpoint: string, data?: any): Promise<T> {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: data ? JSON.stringify(data) : undefined
        });
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        return response.json();
    }
};

export default apiClient;
