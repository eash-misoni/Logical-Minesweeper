"""
ソルバー統合管理 - キューベース実装
論理解法とマニュアル操作の切り替えを管理します
"""

from typing import Optional, List, Tuple, Union
from .solver_base import SolverBase
from .logical_solver import LogicalSolver
from .solver_move import SolverMove, SolverActionType
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
        # デフォルトは論理ソルバーを使用
        self.solver = solver if solver is not None else LogicalSolver()
        self.move_history: List[SolverMove] = []

    @staticmethod
    def create_solver_board_view(board: MinesweeperBoard) -> SolverBoardView:
        """MinesweeperBoardから安全なSolverBoardViewを作成

        Args:
            board: MinesweeperBoardインスタンス

        Returns:
            SolverBoardViewインスタンス
        """
        revealed_mine_numbers = []
        for row in range(board.height):
            for col in range(board.width):
                if board.cell_states[row][col] == CellState.REVEALED:
                    revealed_mine_numbers.append((row, col, board.mine_numbers[row][col]))

        solver_view = SolverBoardView(board.height, board.width, board.cell_states)

        # 発見済みセルの地雷数を設定
        if revealed_mine_numbers:
            solver_view.update_multiple_mine_numbers(revealed_mine_numbers)

        return solver_view

    def set_solver(self, solver: SolverBase):
        """使用するソルバーを変更

        Args:
            solver: 新しいソルバーインスタンス
        """
        self.solver = solver
        self.move_history.clear()  # 履歴をクリア

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

    def execute_step(self, board: MinesweeperBoard) -> tuple[bool, SolverMove]:
        """
        確定手を1手実行（内部形式）

        Args:
            board: マインスイーパーの盤面

        Returns:
            (成功フラグ, 実行した手)のタプル
        """
        solver_view = self.create_solver_board_view(board)
        self.solver.set_board(solver_view)
        move = self.solver.get_next_move()

        if move.action == SolverActionType.NO_MOVE:
            return False, move

        success = True
        try:
            if move.action == SolverActionType.SAFE_DIG:
                success = board.dig(move.row, move.col)
            elif move.action == SolverActionType.CERTAIN_FLAG:
                board.toggle_flag(move.row, move.col)
        except Exception as e:
            print(f"Error executing move: {e}")
            success = False

        if success:
            self.move_history.append(move)

        return success, move

    def execute_command_step(self, board: MinesweeperBoard) -> tuple[bool, SolverCommand]:
        """
        汎用コマンド形式で確定手を1手実行

        Args:
            board: マインスイーパーの盤面

        Returns:
            (成功フラグ, 実行したコマンド)のタプル
        """
        solver_view = self.create_solver_board_view(board)
        self.solver.set_board(solver_view)
        command = self.solver.get_next_command()

        if command.action == SolverAction.NO_MOVE:
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

    def execute_solver_step(self, board: MinesweeperBoard) -> tuple[bool, SolverCommand]:
        """
        汎用ソルバーインターフェースで1手実行（推奨メソッド）

        Args:
            board: マインスイーパーの盤面

        Returns:
            (成功フラグ, 実行したコマンド)のタプル
        """
        return self.execute_command_step(board)

    def solve_until_manual_needed(self, board: MinesweeperBoard) -> List[SolverMove]:
        """
        内部形式で解けるところまで全て実行

        Args:
            board: マインスイーパーの盤面

        Returns:
            実行した手のリスト
        """
        executed_moves = []
        max_iterations = 1000  # 無限ループ防止

        for _ in range(max_iterations):
            # 盤面分析して新しい確定手を検出
            self.analyze_board(board)

            # 確定手があれば実行
            move = self.solver.get_next_move()

            if move.action == SolverActionType.NO_MOVE:
                # 論理的に確定する手がない→手動操作が必要
                break

            # ゲーム盤面で実行
            success = True
            try:
                if move.action == SolverActionType.SAFE_DIG:
                    success = board.dig(move.row, move.col)
                elif move.action == SolverActionType.CERTAIN_FLAG:
                    board.toggle_flag(move.row, move.col)
            except Exception as e:
                print(f"Error executing move: {e}")
                success = False

            if not success:
                break

            executed_moves.append(move)
            self.move_history.append(move)

            # ゲーム終了チェック
            if board.is_game_over():
                break

        return executed_moves

    def solve_with_commands_until_manual_needed(self, board: MinesweeperBoard) -> List[SolverCommand]:
        """
        汎用コマンド形式で解けるところまで全て実行（推奨メソッド）

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
            command = self.solver.get_next_command()

            if command.action == SolverAction.NO_MOVE:
                # 確定する手がない→手動操作が必要
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
