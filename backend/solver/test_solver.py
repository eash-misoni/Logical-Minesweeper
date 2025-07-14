"""
テスト用の簡単なソルバー実行スクリプト
キューベース論理解法の動作確認に使用
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from minesweeper import MinesweeperBoard
from solver.solver_manager import SolverManager

def test_solver():
    """ソルバーの基本的な動作テスト"""
    # 小さな盤面でテスト
    board = MinesweeperBoard(height=9, width=9, mine_count=10)
    solver_manager = SolverManager()

    print("=== Logical Minesweeper Solver Test (Queue-based) ===")
    print(f"盤面サイズ: {board.height}x{board.width}")
    print(f"地雷数: {board.mine_count}")

    # 最初の一手（手動）
    print("\n1. 最初の一手を実行...")
    board.dig(4, 4)  # 中央を掘る

    # 盤面分析
    print("\n2. 盤面分析...")
    solver_manager.analyze_board(board)
    queue_info = solver_manager.get_queue_info()
    print(f"キューサイズ: {queue_info['queue_size']}")
    print(f"論理的確定手あり: {queue_info['has_moves']}")

    # 1手実行テスト
    if queue_info['has_moves']:
        print("\n3. 1手実行テスト...")
        success, move = solver_manager.execute_logical_step(board)
        if success:
            print(f"実行: ({move.row}, {move.col}) - {move.action.value}")
        else:
            print("実行失敗")

    # 論理解法を最後まで実行
    print("\n4. 論理解法を最後まで実行...")
    executed_moves = solver_manager.solve_until_manual_needed(board)
    print(f"実行した手数: {len(executed_moves)}")

    for i, move in enumerate(executed_moves, 1):
        print(f"  {i}. ({move.row}, {move.col}) - {move.action.value}")

    # 最終状態
    print(f"\n5. 最終状態")
    print(f"ゲーム状態: {board.get_game_state().name}")
    print(f"残り地雷数: {board.get_remaining_mines()}")

    final_queue_info = solver_manager.get_queue_info()
    print(f"最終キューサイズ: {final_queue_info['queue_size']}")

    if not final_queue_info['has_moves'] and not board.is_game_over():
        print("→ 手動操作が必要です")

    # 統計
    stats = solver_manager.get_statistics()
    print(f"\n6. 統計")
    print(f"総手数: {stats['total_moves']}")
    print(f"安全掘削: {stats['safe_digs']}")
    print(f"確定フラグ: {stats['certain_flags']}")

def test_step_by_step():
    """ステップバイステップのテスト"""
    print("\n\n=== Step by Step Test ===")

    board = MinesweeperBoard(height=9, width=9, mine_count=10)
    solver_manager = SolverManager()

    # 最初の一手
    board.dig(4, 4)

    step = 1
    while not board.is_game_over():
        print(f"\n--- Step {step} ---")

        # 分析
        solver_manager.analyze_board(board)
        queue_info = solver_manager.get_queue_info()
        print(f"キューサイズ: {queue_info['queue_size']}")

        if not queue_info['has_moves']:
            print("論理的確定手なし → 手動操作が必要")
            break

        # 1手実行
        success, move = solver_manager.execute_logical_step(board)
        if success:
            print(f"実行: ({move.row}, {move.col}) - {move.action.value}")
        else:
            print("実行失敗")
            break

        step += 1
        if step > 50:  # 無限ループ防止
            print("制限に達しました")
            break

if __name__ == "__main__":
    test_solver()
    test_step_by_step()
