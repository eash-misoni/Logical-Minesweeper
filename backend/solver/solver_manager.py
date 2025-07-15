"""
ソルバー統合管理 - キューベース実装
論理解法とマニュアル操作の切り替えを管理します
"""

from typing import Optional, List, Tuple, Union
from .solver_base import SolverBase
from .logical_solver import LogicalSolver
from .solver_board_view import SolverBoardView
from .solver_command import SolverCommand, SolverAction
import sys
import os

# 親ディレクトリのminesweeperモジュールをインポートするための設定
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from minesweeper import MinesweeperBoard, CellState


class SolverManager:
    """ソルバーとマニュアル操作を統合管理"""

    def __init__(self, solver: Optional[SolverBase] = None):
        # デフォルトはLogicalSolverを使用
        self.solver = solver if solver is not None else LogicalSolver()
        self.move_history: List[SolverCommand] = []

    @staticmethod
    def create_solver_board_view(board: MinesweeperBoard) -> SolverBoardView:
        """MinesweeperBoardからプレイヤーに見せられるSolverBoardViewを作成

        Args:
            board: MinesweeperBoardインスタンス

        Returns:
            SolverBoardViewインスタンス
        """
        # 発見済みセルのみ地雷数を含む2次元配列を作成
        visible_mine_numbers = [[board.mine_numbers[row][col]
                                if board.cell_states[row][col] == CellState.REVEALED else None
                                for col in range(board.width)] for row in range(board.height)]

        return SolverBoardView(board.height, board.width, board.cell_states, visible_mine_numbers)

    def set_solver(self, solver: SolverBase):
        """使用するソルバーを変更

        Args:
            solver: 新しいソルバーインスタンス
        """
        self.solver = solver

    def get_current_solver(self) -> SolverBase:
        """現在のソルバーを取得"""
        return self.solver

    def analyze_board(self, board: MinesweeperBoard):
        """
        盤面を分析して新しい確定手をキューに追加

        Args:
            board: マインスイーパーの盤面
        """
        solver_view = self.create_solver_board_view(board)
        self.solver.set_board(solver_view)
        self.solver.find_moves()

    def execute_step(self, board: MinesweeperBoard) -> tuple[bool, SolverCommand]:
        """
        analyze_boardで検出された論理的確定手をキューから取得し、1手実行

        Args:
            board: マインスイーパーの盤面

        Returns:
            (成功フラグ, 実行したコマンド)のタプル
        """
        solver_view = self.create_solver_board_view(board)
        self.solver.set_board(solver_view)
        command = self.solver.get_next_move()

        if command.action == SolverAction.NO_MOVE:
            return False, command
        
        if command.action == SolverAction.QUIT:
            return False, command

        success = True
        try:
            if command.action == SolverAction.DIG:
                success = board.dig(command.row, command.col)
            elif command.action == SolverAction.FLAG:
                board.toggle_flag(command.row, command.col)
        except Exception as e:
            print(f"Error executing command: {e}")
            success = False

        return success, command

    def solve_until_manual_needed(self, board: MinesweeperBoard) -> List[SolverCommand]:
        """
        解けるところまで全て実行

        Args:
            board: マインスイーパーの盤面

        Returns:
            実行したコマンドのリスト
        """
        executed_commands = []
        max_iterations = 1000  # 無限ループ防止

        for _ in range(max_iterations):
            # 盤面分析して新しい確定手を検出
            self.analyze_board(board)

            # 確定手があれば実行
            command = self.solver.get_next_move()

            if command.action == SolverAction.NO_MOVE:
                # 確定する手がない→こっから手動(運ゲー)
                break

            # ゲーム盤面で実行
            success = True
            try:
                if command.action == SolverAction.DIG:
                    success = board.dig(command.row, command.col)
                elif command.action == SolverAction.FLAG:
                    board.toggle_flag(command.row, command.col)
            except Exception as e:
                print(f"Error executing command: {e}")
                success = False

            if not success:
                break

            executed_commands.append(command)

            # ゲーム終了チェック
            if board.is_game_over():
                break

        return executed_commands

    def has_moves(self) -> bool:
        """ソルバーに実行可能な手があるかチェック"""
        return self.solver.has_moves()

    def reset(self):
        """ソルバーの状態をリセット"""
        self.solver.reset()
        self.move_history.clear()
