"""
論理ソルバーのテスト
"""

import sys
import os
import copy

# 親ディレクトリのminesweeperモジュールをインポートするための設定
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from minesweeper import MinesweeperBoard, GameState
from solver.solver_manager import SolverManager
from solver.logical_solver import LogicalSolver
from solver.solver_command import SolverAction


def test_logical_solver():
    print("=== 論理ソルバー実行テスト ===")

    # 小さな盤面でテスト
    h = 20
    w = 20
    m = 180
    board = MinesweeperBoard(h, w, m)
    print(f"盤面を初期化しました ({h}x{w}, 地雷{m}個)")

    # 論理ソルバーを使用
    solver = LogicalSolver()
    manager = SolverManager(solver)

    # 最初の安全な場所を掘る（中央あたり）
    board.dig(2, 2)
    print("最初のセル (2,2) を掘りました")

    # 初手後の盤面をコピーして保存
    initial_board = copy.deepcopy(board)


    print("\n実行前盤面:")
    display_board(board)

    # solve_until_manual_needed()で自動解法を一気に実行
    print("\n論理ソルバーを実行中...")
    executed_commands = manager.solve_until_manual_needed(board)

    if not executed_commands:
        print("論理的に確定する手がありませんでした")
    else:
        print(f"\n{len(executed_commands)} 手実行しました:")
        for i, command in enumerate(executed_commands, 1):
            print(f"  {i}. {command.action.value} ({command.row}, {command.col})")

    print("\n実行後盤面:")
    display_board(board)

    # ゲーム状態をチェック
    if board.get_game_state() == GameState.WON:
        print("\n🎉 ゲームクリア！")
    elif board.get_game_state() == GameState.LOST:
        print("\n💥 地雷を踏みました...")
    else:
        print("\n論理的に確定する手がなくなりました（手動介入が必要）")

    # 盤面復元のテスト
    if executed_commands:
        print("\n=== 盤面復元テスト ===")
        print("初手後の盤面から解法手順を再実行して復元します")

        # 初手後の状態から復元開始
        restored_board = initial_board
        print(f"\n復元開始（初手後）:")
        display_board(restored_board)

        # executed_commandsを順番に実行
        for i, command in enumerate(executed_commands, 1):
            print(f"\n--- ステップ {i}: {command.action.value} ({command.row}, {command.col}) ---")

            if command.action == SolverAction.DIG:
                success = restored_board.dig(command.row, command.col)
                if not success:
                    print(f"掘削失敗: ({command.row}, {command.col})")
                    break
            elif command.action == SolverAction.FLAG:
                restored_board.toggle_flag(command.row, command.col)

            display_board(restored_board)

            # ゲーム終了チェック
            if restored_board.is_game_over():
                break

        # 復元盤面と最終盤面が同じか確認
        if restored_board.get_game_state() == board.get_game_state():
            print("\n復元盤面と最終盤面は一致しました")
        else:
            print("\n復元盤面と最終盤面は一致しませんでした")

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
