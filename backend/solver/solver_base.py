"""
ソルバーの基底クラス
全てのソルバー実装が従うべき共通インターフェースを定義
"""

from abc import ABC, abstractmethod
from typing import Optional
from .solver_board_view import SolverBoardView
from .solver_command import SolverCommand, SolverAction


class SolverBase(ABC):
    """ソルバーの基底クラス"""

    def __init__(self):
        self.name = "Base Solver"
        self.board_view: Optional[SolverBoardView] = None

    def set_board(self, solver_board_view: SolverBoardView):
        """盤面を設定（標準実装）

        Args:
            solver_board_view: ソルバーが利用できる盤面情報
        """
        self.board_view = solver_board_view

    @abstractmethod
    def find_moves(self):
        """
        盤面を分析して次の手を検出・準備
        実装固有のロジックでキューやリストに手を保持しておく
        """
        pass

    @abstractmethod
    def get_next_move(self) -> SolverCommand:
        """
        find_movesで検出された手から次の手を取得

        Returns:
            次に実行すべきコマンド
        """
        pass

    @abstractmethod
    def has_moves(self) -> bool:
        """
        実行可能な手があるかチェック

        Returns:
            手があればTrue、なければFalse
        """
        pass

    @abstractmethod
    def reset(self):
        """ソルバーの状態をリセット"""
        pass

    def get_solver_name(self) -> str:
        """ソルバーの名前を取得"""
        return self.name

    def _is_command_valid(self, command: SolverCommand) -> bool:
        """コマンドが有効かチェック（共通実装）

        Args:
            command: 検証対象のコマンド

        Returns:
            有効ならTrue、無効ならFalse
        """
        # NO_MOVEは常に有効
        if command.action == SolverAction.NO_MOVE:
            return True

        # 座標が設定されていない場合は無効
        if command.row is None or command.col is None:
            return False

        # 盤面が設定されていない場合は無効
        if self.board_view is None:
            return False

        # 範囲外チェック
        if not self.board_view.is_valid_position(command.row, command.col):
            return False

        from minesweeper import CellState

        cell_state = self.board_view.cell_states[command.row][command.col]

        if command.action == SolverAction.DIG:
            # 掘る行動は未発見のセルのみ有効
            return cell_state == CellState.HIDDEN
        elif command.action == SolverAction.FLAG:
            # フラグ行動は未発見セルまたはフラグ済みセル（トグル）で有効
            return cell_state == CellState.HIDDEN or cell_state == CellState.FLAGGED

        return False
