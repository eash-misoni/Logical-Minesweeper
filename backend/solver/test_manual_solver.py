"""
手動ソルバーのテスト
"""

import sys
import os

# 親ディレクトリのminesweeperモジュールをインポートするための設定
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from minesweeper import MinesweeperBoard, GameState
from solver.solver_manager import SolverManager
from solver.manual_solver import ManualSolver
from solver.solver_command import SolverAction


def test_manual_solver():
    print("=== 手動ソルバーテスト ===")

    # 小さな盤面でテスト
    board = MinesweeperBoard(6, 5, 4)
    manual_solver = ManualSolver()
    manager = SolverManager(manual_solver)

    print("盤面を初期化しました (6x5, 地雷4個)")

    # 最初の一手（安全な位置を掘る）
    board.dig(2, 2)
    print("中央 (2,2) を最初に掘りました")

    while not board.is_game_over():
        print(f"\n現在のゲーム状態: {board.get_game_state().name}")
        print(f"残り地雷数: {board.get_remaining_mines()}")

        # 手動ソルバーでは先にanalyze_boardを呼んでユーザー入力を受け取る
        manager.analyze_board(board)

        # キューにコマンドがあるかチェック
        if not manager.has_moves():
            print("操作が終了されました")
            break

        # 手動で一手実行
        success, command = manager.execute_step(board)

        if not success:
            if command.action == SolverAction.QUIT:
                print("ゲームを終了します")
                break
            elif command.action == SolverAction.NO_MOVE:
                print(f"操作に失敗しました。コマンド: {command.action.value}")
                if hasattr(command, 'row') and hasattr(command, 'col'):
                    print(f"座標: ({command.row}, {command.col})")
                break
            elif board.get_game_state() == GameState.LOST:
                print("💥 地雷を踏みました...")
                break

        print(f"実行されました: {command.action.value} ({command.row}, {command.col})")

        if board.get_game_state() == GameState.WON:
            print("🎉 ゲームクリア！")
            break
        elif board.get_game_state() == GameState.LOST:
            print("💥 地雷を踏みました...")
            break

    print("\nゲーム終了")


if __name__ == "__main__":
    test_manual_solver()
