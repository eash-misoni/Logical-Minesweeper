// Logical Minesweeper JavaScript

class WebMinesweeper {
    constructor() {
        this.gameId = null;
        this.timer = 0;
        this.timerInterval = null;
        this.gameStarted = false;
        this.gameState = 'PLAYING'; // ゲーム状態を追跡

        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // 難易度選択
        document.getElementById('difficulty').addEventListener('change', (e) => {
            const customSettings = document.getElementById('custom-settings');
            if (e.target.value === 'custom') {
                customSettings.style.display = 'flex';
            } else {
                customSettings.style.display = 'none';
            }
        });

        // 新しいゲームボタン
        document.getElementById('new-game').addEventListener('click', () => {
            this.startNewGame();
        });
    }

    async startNewGame() {
        const difficulty = document.getElementById('difficulty').value;
        let settings;

        switch (difficulty) {
            case 'beginner':
                settings = { height: 9, width: 9, mines: 10 };
                break;
            case 'intermediate':
                settings = { height: 16, width: 16, mines: 40 };
                break;
            case 'expert':
                settings = { height: 20, width: 24, mines: 99 };
                break;
            case 'custom':
                settings = {
                    height: parseInt(document.getElementById('height').value),
                    width: parseInt(document.getElementById('width').value),
                    mines: parseInt(document.getElementById('mines').value)
                };
                break;
        }

        try {
            const response = await fetch('/api/new-game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings)
            });

            const data = await response.json();
            this.gameId = data.game_id;
            this.gameState = 'PLAYING'; // ゲーム状態をリセット
            this.renderBoard(data.board_data);
            this.updateGameInfo(data);
            this.resetTimer();
            this.gameStarted = false;

            document.getElementById('game-status').textContent = 'ゲーム開始！クリックして掘ってみよう';
            document.getElementById('game-status').className = 'game-status playing';

        } catch (error) {
            console.error('Error starting new game:', error);
            alert('ゲームの開始に失敗しました');
        }
    }

    renderBoard(boardData) {
        const gameBoard = document.getElementById('game-board');
        gameBoard.innerHTML = '';

        for (let row = 0; row < boardData.length; row++) {
            const rowDiv = document.createElement('div');
            rowDiv.className = 'board-row';

            for (let col = 0; col < boardData[row].length; col++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.row = row;
                cell.dataset.col = col;

                const cellData = boardData[row][col];
                this.updateCellDisplay(cell, cellData);

                // イベントリスナー
                cell.addEventListener('click', (e) => this.handleCellClick(e));
                cell.addEventListener('contextmenu', (e) => this.handleRightClick(e));

                rowDiv.appendChild(cell);
            }

            gameBoard.appendChild(rowDiv);
        }
    }

    updateCellDisplay(cell, cellData) {
        cell.className = 'cell';
        cell.textContent = '';

        if (cellData.flagged) {
            cell.classList.add('flagged');
            cell.textContent = '🚩';
        } else if (cellData.revealed) {
            cell.classList.add('revealed');
            if (cellData.mine) {
                cell.classList.add('mine');
                cell.textContent = '💣';
            } else if (cellData.number > 0) {
                cell.classList.add(`number-${cellData.number}`);
                cell.textContent = cellData.number;
            }
        }
    }

    async handleCellClick(event) {
        if (!this.gameId || this.gameState !== 'PLAYING') return; // ゲーム終了後はクリック無効

        const cell = event.target;
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);

        if (!this.gameStarted) {
            this.startTimer();
            this.gameStarted = true;
        }

        try {
            const response = await fetch('/api/dig', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    game_id: this.gameId,
                    row: row,
                    col: col
                })
            });

            const data = await response.json();
            this.renderBoard(data.board_data);
            this.updateGameInfo(data);
            this.updateGameStatus(data);

        } catch (error) {
            console.error('Error digging cell:', error);
        }
    }

    async handleRightClick(event) {
        event.preventDefault();

        if (!this.gameId || this.gameState !== 'PLAYING') return; // ゲーム終了後はクリック無効

        const cell = event.target;
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);

        try {
            const response = await fetch('/api/flag', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    game_id: this.gameId,
                    row: row,
                    col: col
                })
            });

            const data = await response.json();
            this.renderBoard(data.board_data);
            this.updateGameInfo(data);

        } catch (error) {
            console.error('Error flagging cell:', error);
        }
    }

    updateGameInfo(data) {
        document.getElementById('mine-count').textContent = data.remaining_mines;
    }

    updateGameStatus(data) {
        const statusDiv = document.getElementById('game-status');
        
        // ゲーム状態を更新
        this.gameState = data.game_state;

        if (data.game_state === 'WON') {
            statusDiv.textContent = '🎉 おめでとうございます！勝利しました！ 🎉';
            statusDiv.className = 'game-status won';
            this.stopTimer();
        } else if (data.game_state === 'LOST') {
            statusDiv.textContent = '💀 残念...敗北しました 💀';
            statusDiv.className = 'game-status lost';
            this.stopTimer();
        } else {
            statusDiv.textContent = data.message || 'ゲーム進行中...';
            statusDiv.className = 'game-status playing';
        }
    }

    startTimer() {
        this.timer = 0;
        this.timerInterval = setInterval(() => {
            this.timer++;
            this.updateTimerDisplay();
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    resetTimer() {
        this.stopTimer();
        this.timer = 0;
        this.updateTimerDisplay();
    }

    updateTimerDisplay() {
        const minutes = Math.floor(this.timer / 60);
        const seconds = this.timer % 60;
        document.getElementById('timer').textContent =
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}

// ゲーム初期化
document.addEventListener('DOMContentLoaded', () => {
    const game = new WebMinesweeper();
    console.log('Logical Minesweeper loaded!');
});
