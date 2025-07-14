"""
ソルバーの基底クラス
全てのソルバー実装が従うべき共通インターフェースを定義
"""

from abc import ABC, abstractmethod
from typing import Optional
from solver_board_view import SolverBoardView
from solver_command import SolverCommand
from solver_move import SolverMove


class SolverBase(ABC):
    """全てのソルバーの基底クラス"""

    def __init__(self):
        self.name = "Base Solver"
        self.board_view: Optional[SolverBoardView] = None

    @abstractmethod
    def set_board(self, solver_board_view: SolverBoardView):
        """盤面を設定

        Args:
            solver_board_view: ソルバー用の安全な盤面ビュー
        """
        pass

    @abstractmethod
    def find_moves(self):
        """
        盤面を分析して次の手を検出・準備
        実装固有のロジックでキューやリストに手を追加
        """
        pass

    @abstractmethod
    def get_next_move(self) -> SolverMove:
        """
        次の手を内部形式で取得

        Returns:
            次に実行すべき手（内部データ構造）
        """
        pass

    @abstractmethod
    def get_next_command(self) -> SolverCommand:
        """
        次の手を汎用コマンド形式で取得

        Returns:
            次に実行すべきコマンド（外部インターフェース）
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
