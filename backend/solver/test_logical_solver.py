"""
論理ソルバーのテスト
"""

import sys
import os

# 親ディレクトリのminesweeperモジュールをインポートするための設定
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from minesweeper import MinesweeperBoard, GameState
from solver.solver_manager import SolverManager
from solver.logical_solver import LogicalSolver
from solver.solver_command import SolverAction


def test_logical_solver():
    print("=== 論理ソルバーテスト ===")

    # 小さな盤面でテスト
    board = MinesweeperBoard(6, 6, 5)
    print(f"盤面を初期化しました (6x6, 地雷5個)")

    # 論理ソルバーを使用
    solver = LogicalSolver()
    manager = SolverManager(solver)

    # 最初の安全な場所を掘る（中央あたり）
    board.dig(2, 2)
    print("最初のセル (2,2) を掘りました")

    print(f"現在のゲーム状態: {board.get_game_state()}")
    print(f"残り地雷数: {board.get_remaining_mines()}")

    step_count = 0
    max_steps = 50  # 無限ループ防止

    while step_count < max_steps:
        print(f"\n--- ステップ {step_count + 1} ---")

        # 現在の盤面を表示
        display_board(board)

        # 論理解法で確定手を分析
        manager.analyze_board(board)

        # キューにコマンドがあるかチェック
        if not manager.has_moves():
            print("論理的に確定する手がありません")
            break

        # 論理解法で一手実行
        success, command = manager.execute_step(board)

        if not success:
            if command.action == SolverAction.QUIT:
                print("ゲームを終了します")
                break
            elif command.action == SolverAction.NO_MOVE:
                print("論理的に確定する手がありません")
                break
            else:
                print(f"操作に失敗しました。コマンド: {command.action.value}")
                if hasattr(command, 'row') and hasattr(command, 'col'):
                    print(f"座標: ({command.row}, {command.col})")
                break

        print(f"実行されました: {command.action.value} ({command.row}, {command.col})")

        # ゲーム状態をチェック
        if board.get_game_state() == GameState.WON:
            print("🎉 ゲームクリア！")
            break
        elif board.get_game_state() == GameState.LOST:
            print("💥 地雷を踏みました...")
            break

        step_count += 1

    print(f"\n最終盤面(実際の地雷位置):")
    display_board(board, show_mines=True)
    print("ゲーム終了")


def display_board(board: MinesweeperBoard, show_mines: bool = False):
    """盤面を表示（CLI用）"""
    height, width = board.height, board.width

    # ヘッダー行
    print("    ", end="")
    for col in range(width):
        print(f"{col:2}", end=" ")
    print()

    # 各行を表示
    for row in range(height):
        print(f"{row:2}: ", end="")
        for col in range(width):
            cell_info = board.get_cell_info(row, col)
            char = get_cell_display_char(cell_info, show_mines)
            print(f"{char:2}", end=" ")
        print()


def get_cell_display_char(cell_info, show_mines: bool = False):
    """セルの表示文字を取得"""
    if not cell_info:
        return "?"

    if show_mines and cell_info['is_mine']:
        return "*"

    if cell_info['is_flagged']:
        return "F"
    elif cell_info['is_hidden']:
        return "."
    elif cell_info['is_revealed']:
        if cell_info['is_mine']:
            return "*"
        elif cell_info['mine_number'] == 0:
            return " "
        else:
            return str(cell_info['mine_number'])

    return "?"


if __name__ == "__main__":
    test_logical_solver()
