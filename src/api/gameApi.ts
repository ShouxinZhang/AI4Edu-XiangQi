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
    success?: boolean;
}

/**
 * Request AI to make a move
 */
export async function getAIMove(board: number[][], player: number, difficulty?: number): Promise<MoveResponse> {
    return apiClient.post<MoveResponse>('/api/ai/move', { board, player, difficulty });
}

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

