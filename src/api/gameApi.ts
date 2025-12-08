/**
 * Game API - AI move requests
 */
import apiClient from './client';

export interface MoveRequest {
    board: number[][];
    player: number;
}

export interface MoveResponse {
    start: [number, number];
    end: [number, number];
}


interface ProgressUpdate {
    type: 'progress';
    percent: number;
    eta_seconds: number;
}

interface ResultUpdate {
    type: 'result';
    start: [number, number];
    end: [number, number];
}

type AIResponse = ProgressUpdate | ResultUpdate;

export const getAIMove = async (
    board: number[][],
    player: number,
    difficulty?: number,
    signal?: AbortSignal,
    onProgress?: (percent: number, eta: number) => void
): Promise<{ start: [number, number], end: [number, number] }> => {

    // Convert 2D array to format expected by backend if needed, or pass as is
    // Backend expects { board: number[][], player: number, difficulty?: number }

    // We use streamPost to get progress updates
    const stream = apiClient.streamPost<AIResponse>('/api/ai/move', {
        board,
        player,
        difficulty
    }, signal);

    let finalResult: { start: [number, number], end: [number, number] } | null = null;

    for await (const update of stream) {
        if (update.type === 'progress') {
            if (onProgress) {
                onProgress(update.percent, update.eta_seconds);
            }
        } else if (update.type === 'result') {
            finalResult = { start: update.start, end: update.end };
        }
    }

    if (!finalResult) {
        throw new Error('AI stream ended without result');
    }

    return finalResult;
};

/**
 * Get game history list
 */
export async function getGameHistory(mode: string = 'training', limit: number = 50) {
    return apiClient.get<any[]>(`/api/history?mode=${mode}&limit=${limit}`);
}

/**
 * Get a specific game's details for replay
 */
export async function getGameDetail(gameId: string) {
    return apiClient.get<any>(`/api/history/${gameId}`);
}

/**
 * Save a completed game result
 */
export async function saveGameResult(
    mode: 'pvp' | 'pve' | 'training',
    winner: number,
    moves: { from: { row: number; col: number }; to: { row: number; col: number } }[]
) {
    const formattedMoves = moves.map(m => [
        [m.from.col, m.from.row],
        [m.to.col, m.to.row]
    ]);
    return apiClient.post('/api/games/save', {
        mode,
        winner,
        moves: formattedMoves,
        timestamp: Date.now() / 1000
    });
}

/**
 * Get RL evolution games from training
 */
export async function getEvolutionGames(iteration?: number, limit: number = 50) {
    const params = new URLSearchParams();
    if (iteration !== undefined && iteration !== null) {
        params.append('iteration', String(iteration));
    }
    params.append('limit', String(limit));
    return apiClient.get<any[]>(`/api/evolution/games?${params.toString()}`);
}

/**
 * Get available training iterations
 */
export async function getEvolutionIterations(): Promise<number[]> {
    return apiClient.get<number[]>('/api/evolution/iterations');
}

