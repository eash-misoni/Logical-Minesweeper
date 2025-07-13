"""
Logical Minesweeper Web API
FastAPIを使用したマインスイーパーのWeb API実装
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any
import uuid
import os
from pathlib import Path

from minesweeper import MinesweeperBoard, GameState, CellState

app = FastAPI(title="Logical Minesweeper API", version="1.0.0")

# ゲームセッション管理
game_sessions: Dict[str, MinesweeperBoard] = {}

# Pydanticモデル
class GameSettings(BaseModel):
    height: int
    width: int
    mines: int

class DigRequest(BaseModel):
    game_id: str
    row: int
    col: int

class FlagRequest(BaseModel):
    game_id: str
    row: int
    col: int

class GameResponse(BaseModel):
    game_id: str
    board_data: list
    game_state: str
    remaining_mines: int
    message: str = ""

def convert_cell_data_for_api(cell_info: dict) -> dict:
    """MinesweeperBoardのセル情報をAPI用に変換"""
    if not cell_info:
        return None
    
    return {
        'revealed': cell_info['is_revealed'],
        'flagged': cell_info['is_flagged'],
        'mine': cell_info['is_mine'] if cell_info['is_revealed'] else False,  # 発見されてない地雷は隠す
        'number': cell_info['mine_number'] if cell_info['is_revealed'] else 0
    }

def convert_board_data_for_api(board: MinesweeperBoard) -> list:
    """盤面データをAPI用に変換"""
    board_data = []
    raw_data = board.get_board_data()
    
    for row in raw_data:
        row_data = []
        for cell_info in row:
            converted_cell = convert_cell_data_for_api(cell_info)
            row_data.append(converted_cell)
        board_data.append(row_data)
    
    return board_data

@app.post("/api/new-game", response_model=GameResponse)
async def create_new_game(settings: GameSettings):
    """新しいゲームを開始"""
    try:
        # 設定値の検証
        if not (5 <= settings.height <= 50 and 5 <= settings.width <= 50):
            raise HTTPException(status_code=400, detail="盤面サイズは5-50の範囲で指定してください")
        
        max_mines = settings.height * settings.width - 9  # 最初のクリック周辺を除く
        if not (1 <= settings.mines <= max_mines):
            raise HTTPException(status_code=400, detail=f"地雷数は1-{max_mines}の範囲で指定してください")
        
        # 新しいゲームボードを作成
        game_id = str(uuid.uuid4())
        board = MinesweeperBoard(settings.height, settings.width, settings.mines)
        game_sessions[game_id] = board
        
        # レスポンス作成
        return GameResponse(
            game_id=game_id,
            board_data=convert_board_data_for_api(board),
            game_state=board.get_game_state().name,
            remaining_mines=board.get_remaining_mines(),
            message="新しいゲームが開始されました！最初のマスをクリックしてください"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ゲーム作成エラー: {str(e)}")

@app.post("/api/dig", response_model=GameResponse)
async def dig_cell(request: DigRequest):
    """セルを掘る"""
    try:
        # ゲームセッション確認
        if request.game_id not in game_sessions:
            raise HTTPException(status_code=404, detail="ゲームセッションが見つかりません")
        
        board = game_sessions[request.game_id]
        
        # 座標の検証
        if not (0 <= request.row < board.height and 0 <= request.col < board.width):
            raise HTTPException(status_code=400, detail="無効な座標です")
        
        # 掘る
        success = board.dig(request.row, request.col)
        
        # メッセージ生成
        message = ""
        if board.get_game_state() == GameState.WON:
            message = "🎉 おめでとうございます！勝利しました！ 🎉"
        elif board.get_game_state() == GameState.LOST:
            message = "💀 残念...地雷を踏んでしまいました 💀"
        elif success:
            message = f"位置 ({request.row}, {request.col}) を掘りました"
        else:
            message = "何も起こりませんでした"
        
        return GameResponse(
            game_id=request.game_id,
            board_data=convert_board_data_for_api(board),
            game_state=board.get_game_state().name,
            remaining_mines=board.get_remaining_mines(),
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"掘削エラー: {str(e)}")

@app.post("/api/flag", response_model=GameResponse)
async def toggle_flag(request: FlagRequest):
    """フラグを切り替える"""
    try:
        # ゲームセッション確認
        if request.game_id not in game_sessions:
            raise HTTPException(status_code=404, detail="ゲームセッションが見つかりません")
        
        board = game_sessions[request.game_id]
        
        # 座標の検証
        if not (0 <= request.row < board.height and 0 <= request.col < board.width):
            raise HTTPException(status_code=400, detail="無効な座標です")
        
        # フラグ切り替え前の状態確認
        cell_info = board.get_cell_info(request.row, request.col)
        was_flagged = cell_info['is_flagged']
        
        # フラグ切り替え
        board.toggle_flag(request.row, request.col)
        
        # メッセージ生成
        if was_flagged:
            message = f"位置 ({request.row}, {request.col}) のフラグを外しました"
        else:
            message = f"位置 ({request.row}, {request.col}) にフラグを立てました"
        
        return GameResponse(
            game_id=request.game_id,
            board_data=convert_board_data_for_api(board),
            game_state=board.get_game_state().name,
            remaining_mines=board.get_remaining_mines(),
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"フラグ操作エラー: {str(e)}")

@app.get("/api/game/{game_id}", response_model=GameResponse)
async def get_game_state(game_id: str):
    """ゲーム状態を取得"""
    try:
        if game_id not in game_sessions:
            raise HTTPException(status_code=404, detail="ゲームセッションが見つかりません")
        
        board = game_sessions[game_id]
        
        return GameResponse(
            game_id=game_id,
            board_data=convert_board_data_for_api(board),
            game_state=board.get_game_state().name,
            remaining_mines=board.get_remaining_mines(),
            message="ゲーム状態を取得しました"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"状態取得エラー: {str(e)}")

@app.delete("/api/game/{game_id}")
async def delete_game(game_id: str):
    """ゲームセッションを削除"""
    try:
        if game_id not in game_sessions:
            raise HTTPException(status_code=404, detail="ゲームセッションが見つかりません")
        
        del game_sessions[game_id]
        return {"message": "ゲームセッションを削除しました"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"削除エラー: {str(e)}")

# ヘルスチェック
@app.get("/health")
async def health_check():
    """APIの状態確認"""
    return {
        "status": "healthy",
        "active_games": len(game_sessions),
        "message": "Logical Minesweeper API is running!"
    }

# 静的ファイル配信設定（最後に配置）
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    # 静的ファイル（CSS、JS）を直接ルートから配信
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")
else:
    # フロントエンドフォルダが見つからない場合のルート
    @app.get("/")
    async def serve_index():
        """メインページを配信"""
        return {"message": "Logical Minesweeper API", "status": "running", "frontend": "not found"}

if __name__ == "__main__":
    import uvicorn
    
    print("🎮 Logical Minesweeper API を起動中...")
    print("フロントエンド: http://localhost:8000")
    print("API ドキュメント: http://localhost:8000/docs")
    print("ヘルスチェック: http://localhost:8000/health")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
