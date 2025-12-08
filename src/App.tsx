import React from 'react';
import { GameProvider, useGame } from './store/GameContext';
import { MainLayout } from './components/layout/MainLayout';
import { GameMode } from './types';

// Modules
import { PVPGame } from './modules/pvp/PVPGame';
import { PVEGame } from './modules/pve/PVEGame';
import { TrainingModule } from './modules/training/TrainingModule';
import { ReplayModule } from './modules/replay/ReplayModule';

const AppContent: React.FC = () => {
    const { state, setMode } = useGame();

    const renderModule = () => {
        switch (state.gameMode) {
            case GameMode.PVP:
                return <PVPGame />;
            case GameMode.PVE:
                return <PVEGame />;
            case GameMode.TRAINING:
                return <TrainingModule />;
            case GameMode.REPLAY:
                return <ReplayModule />;
            default:
                return <PVPGame />;
        }
    };

    return (
        <MainLayout currentMode={state.gameMode} onModeChange={setMode}>
            {renderModule()}
        </MainLayout>
    );
};

const App: React.FC = () => {
    return (
        <GameProvider>
            <AppContent />
        </GameProvider>
    );
};

export default App;
