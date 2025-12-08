/**
 * Unified API Types
 * These types should match the backend Pydantic models in backend/schemas/game_schemas.py
 */

// ========== AI Move API ==========

export interface AIMoveRequest {
    board: number[][];
    player: number;  // 1 = Red, -1 = Black
    difficulty?: number;  // 1-4 for Classic, undefined for AlphaZero
}

export interface AIMoveProgressResponse {
    type: 'progress';
    percent: number;
    eta_seconds: number;
}

export interface AIMoveResultResponse {
    type: 'result';
    start: [number, number];
    end: [number, number];
}

export type AIMoveStreamResponse = AIMoveProgressResponse | AIMoveResultResponse;

// ========== Game API ==========

export interface SaveGameRequest {
    mode: 'pvp' | 'pve' | 'training';
    winner: number;  // 1 = Red, -1 = Black, 0 = Draw
    moves: { from: { row: number; col: number }; to: { row: number; col: number } }[];
    timestamp?: number;
}

export interface SaveGameResponse {
    status: 'ok';
    game_id: string;
}

// ========== Training API ==========

export interface TrainingState {
    iteration: number;
    episode: number;
    total_episodes: number;
    step: number;
    games_completed: number;
    status: 'idle' | 'starting' | 'running' | 'stopped';
    history: GameHistoryItem[];
    evalHistory: EvaluationPoint[];
}

export interface GameHistoryItem {
    game_id: string;
    winner: number;
    moves: any[];
    timestamp: number;
    source?: string;
}

export interface EvaluationPoint {
    iteration: number;
    vsLevel1: number;
    vsLevel2: number;
    vsLevel3: number;
}

export interface TrainingConfig {
    max_steps: number;
    workers: number;
    mode: 'single' | 'parallel';
    num_mcts_sims: number;
    num_episodes?: number;
}

// ========== System Stats ==========

export interface GPUStats {
    gpu_utilization: number;
    memory_used_mb: number;
    memory_total_mb: number;
    temperature_c: number;
}

export interface CPUStats {
    cpu_utilization: number;
    memory_used_mb: number;
    memory_total_mb: number;
    memory_percent: number;
}
