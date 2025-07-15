"""
手動入力ソルバー
ユーザーからの入力を受け取って手動操作を提供
"""

from typing import Optional
from collections import deque
from .solver_base import SolverBase
from .solver_command import SolverCommand, SolverAction


class ManualSolver(SolverBase):
    """手動入力によるソルバー"""

    def __init__(self):
        super().__init__()
        self.name = "Manual Input Solver"
        self.command_queue = deque()

    def find_moves(self):
        """
        ユーザーからの入力を受け取ってコマンドキューに追加
        """
        if self.board_view is None:
            raise ValueError("盤面が設定されていません")

        print("\n=== 手動操作入力 ===")
        self._display_board()

        while True:
            try:
                user_input = input("コマンドを入力 (例: d 3 4, f 2 1, q:終了): ").strip().lower()

                if user_input == 'q' or user_input == 'quit':
                    # 終了コマンド
                    self.command_queue.append(SolverCommand(SolverAction.QUIT, 0, 0))
                    break

                parts = user_input.split()
                if len(parts) != 3:
                    print("形式: [d/f] [行] [列] または q で終了")
                    continue

                action_str, row_str, col_str = parts

                try:
                    row = int(row_str)
                    col = int(col_str)
                except ValueError:
                    print("行と列は数字で入力してください")
                    continue

                # コマンド作成
                if action_str == 'd' or action_str == 'dig':
                    command = SolverCommand.dig(row, col)
                elif action_str == 'f' or action_str == 'flag':
                    command = SolverCommand.flag(row, col)
                else:
                    print("アクション: d (掘る) または f (フラグ)")
                    continue

                # 有効性チェック
                if self._is_command_valid(command):
                    self.command_queue.append(command)
                    print(f"コマンド追加: {self._format_command(command)}")
                    break
                else:
                    print("無効なコマンドです（範囲外、すでに開かれているなど）")

            except KeyboardInterrupt:
                print("\n操作をキャンセルしました")
                self.command_queue.append(SolverCommand.no_move())
                break
            except Exception as e:
                print(f"エラー: {e}")

    def get_next_move(self) -> SolverCommand:
        """
        キューから次のコマンドを取得

        Returns:
            次に実行すべきコマンド
        """
        if self.command_queue:
            return self.command_queue.popleft()
        else:
            return SolverCommand.no_move()

    def has_moves(self) -> bool:
        """
        実行可能な手があるかチェック

        Returns:
            手があればTrue、なければFalse
        """
        return len(self.command_queue) > 0

    def reset(self):
        """ソルバーの状態をリセット"""
        self.command_queue.clear()
        self.board_view = None

    def _display_board(self):
        """現在の盤面状態を表示"""
        if self.board_view is None:
            return

        print(f"\n盤面 ({self.board_view.height}x{self.board_view.width}):")
        print("   ", end="")
        for col in range(self.board_view.width):
            print(f"{col:2}", end=" ")
        print()

        from minesweeper import CellState

        for row in range(self.board_view.height):
            print(f"{row:2}: ", end="")
            for col in range(self.board_view.width):
                cell_state = self.board_view.cell_states[row][col]

                if cell_state == CellState.HIDDEN:
                    print(" .", end=" ")
                elif cell_state == CellState.FLAGGED:
                    print(" F", end=" ")
                elif cell_state == CellState.REVEALED:
                    mine_num = self.board_view.get_mine_number(row, col)
                    if mine_num is not None:
                        print(f"{mine_num:2}", end=" ")
                    else:
                        print(" ?", end=" ")
                else:
                    print(" ?", end=" ")
            print()

    def _format_command(self, command: SolverCommand) -> str:
        """コマンドを人間が読みやすい形式でフォーマット"""
        if command.action == SolverAction.DIG:
            return f"掘る ({command.row}, {command.col})"
        elif command.action == SolverAction.FLAG:
            return f"フラグ ({command.row}, {command.col})"
        elif command.action == SolverAction.NO_MOVE:
            return "操作なし"
        else:
            return f"不明なコマンド: {command.action}"
