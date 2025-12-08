/**
 * API Endpoint Constants
 * Centralized location for all backend API URLs.
 */

export const API_ENDPOINTS = {
    // AI Move
    AI_MOVE: '/api/ai/move',

    // Game
    SAVE_GAME: '/api/games/save',
    HISTORY: '/api/history',

    // Evolution (RL Training Games)
    EVOLUTION_GAMES: '/api/evolution/games',
    EVOLUTION_ITERATIONS: '/api/evolution/iterations',

    // Training Control
    TRAINING_STATE: '/api/training/state',
    TRAINING_START: '/api/training/start',
    TRAINING_STOP: '/api/training/stop',
    TRAINING_RESET: '/api/training/reset',
    TRAINING_CONFIG: '/api/training/config',

    // System Stats
    GPU_STATS: '/api/gpu/stats',
    CPU_STATS: '/api/cpu/stats',

    // Health
    HEALTH: '/health',

    // WebSocket
    WS_TRAINING: '/ws/training',
} as const;

export type APIEndpoint = keyof typeof API_ENDPOINTS;
