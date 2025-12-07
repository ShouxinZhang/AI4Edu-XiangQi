/**
 * Training API - Real-time training data
 */
import apiClient from './client';

export interface TrainingState {
    iteration: number;
    episode: number;
    total_episodes: number;
    status: string;
    step?: number;
    history?: any[];
    eval_result?: {
        iteration: number;
        az_wins: number;
        mm_wins: number;
        draws: number;
        win_rate: number;
    };
}

export interface GPUStats {
    gpu_utilization: number;
    memory_used: number;
    memory_total: number;
    temperature: number;
}

/**
 * Get current training state
 */
export async function getTrainingState(): Promise<TrainingState> {
    return apiClient.get<TrainingState>('/api/training/state');
}

/**
 * Get GPU statistics
 */
export async function getGPUStats(): Promise<GPUStats> {
    return apiClient.get<GPUStats>('/api/gpu/stats');
}

/**
 * Subscribe to real-time training updates via WebSocket
 */
export function subscribeToTraining(
    onMessage: (data: any) => void,
    onError?: (error: Event) => void,
    onClose?: () => void
): () => void {
    const ws = new WebSocket(`${apiClient.wsUrl}/ws/training`);

    ws.onopen = () => {
        console.log('[WS] Connected to training stream');
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            onMessage(data);
        } catch (e) {
            console.error('[WS] Failed to parse message:', e);
        }
    };

    ws.onerror = (error) => {
        console.error('[WS] Error:', error);
        onError?.(error);
    };

    ws.onclose = () => {
        console.log('[WS] Connection closed');
        onClose?.();
    };

    // Return cleanup function
    return () => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.close();
        }
    };
}
