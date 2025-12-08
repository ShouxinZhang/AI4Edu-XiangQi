/**
 * API Client Configuration
 */

const API_BASE_URL = 'http://localhost:8000';
const WS_BASE_URL = 'ws://localhost:8000';

export const apiClient = {
    baseUrl: API_BASE_URL,
    wsUrl: WS_BASE_URL,

    async get<T>(endpoint: string, signal?: AbortSignal): Promise<T> {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { signal });
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        return response.json();
    },

    async post<T>(endpoint: string, data?: any, signal?: AbortSignal): Promise<T> {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: data ? JSON.stringify(data) : undefined,
            signal
        });
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        return response.json();
    },

    async *streamPost<T>(endpoint: string, data?: any, signal?: AbortSignal): AsyncGenerator<T, void, unknown> {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: data ? JSON.stringify(data) : undefined,
            signal
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        if (!response.body) throw new Error('No response body');

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');

                // Keep the last partial line in the buffer
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.trim()) {
                        try {
                            yield JSON.parse(line);
                        } catch (e) {
                            console.warn('Error parsing JSON stream line:', line);
                        }
                    }
                }
            }
        } finally {
            reader.releaseLock();
        }
    }
};

export default apiClient;
