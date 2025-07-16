"""
論理解法専用ソルバー - キューベース実装
確定した行動をキューで管理し、盤面差分から新しい確定を検出
"""

from typing import List, Tuple, Optional
from collections import deque
import sys
import os

# 親ディレクトリのminesweeperモジュールをインポートするための設定
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from minesweeper import CellState
from .solver_board_view import SolverBoardView
from .solver_command import SolverCommand, SolverAction
from .solver_base import SolverBase


class LogicalSolver(SolverBase):
    """論理的に確定する手のみを提案するソルバー"""

    def __init__(self):
        super().__init__()
        self.name = "Logical Certainty Solver"
        self.action_queue = deque()  # 確定した行動のキュー（SolverCommand）
        self.previous_board_state: Optional[List[List[CellState]]] = None  # 前回の盤面状態

    def find_moves(self):
        """
        前回との差分を検出し、新しい確定手をキューに追加
        基底クラスのfind_movesメソッドの実装
        """
        if self.board_view is None:
            raise ValueError("盤面が設定されていません")

        if self.previous_board_state is None:
            # 初回実行時は全ての発見済みセルを差分として扱う
            changed_cells = []
            for row in range(self.board_view.height):
                for col in range(self.board_view.width):
                    if self.board_view.cell_states[row][col] == CellState.REVEALED:
                        changed_cells.append((row, col))
        else:
            # 差分を検出
            changed_cells = self._detect_changes(self.board_view.cell_states)

        # 差分があるセルについて分析
        for row, col in changed_cells:
            self._analyze_revealed_cell(row, col)

        # 現在の状態を保存（深いコピーを作成）
        self.previous_board_state = [row[:] for row in self.board_view.cell_states]

    def get_next_move(self) -> SolverCommand:
        """
        次の論理的確定手を取得

        Returns:
            実行すべきソルバーコマンド
        """
        if self.board_view is None:
            raise ValueError("盤面が設定されていません")

        while self.action_queue:
            command = self.action_queue.popleft()

            # 行動が有効かチェック
            if self._is_command_valid(command):
                return command
            # 無効な場合は次の行動を試す

        # キューが空または全て無効
        return SolverCommand.no_move()

    def _detect_changes(self, current_state: List[List[CellState]]) -> List[Tuple[int, int]]:
        """前回から変化したセルを検出"""
        changed_cells = []

        for row in range(len(current_state)):
            for col in range(len(current_state[0])):
                if self.previous_board_state[row][col] != current_state[row][col]:
                    # 新たに発見されたセルを対象とする
                    if current_state[row][col] == CellState.REVEALED:
                        changed_cells.append((row, col))
                    # フラグを立てたセルの周囲を対象とする
                    elif current_state[row][col] == CellState.FLAGGED:
                        changed_cells.extend(self.board_view.get_neighbors(row, col))

        return changed_cells

    def _analyze_revealed_cell(self, row: int, col: int):
        """
        発見済みセル周辺の論理的確定を分析してキューに追加

        Args:
            row: 分析対象の行
            col: 分析対象の列
        """
        # TODO: ここに具体的な論理解法のロジックを実装
        # 基本的なルール：
        # 1. 周囲のフラグ数 = 地雷数 → 残りは安全
        # 2. 周囲の未発見マス数 = 残り必要地雷数 → 全て地雷

        mine_number = self.board_view.get_mine_number(row, col)
        if mine_number is None:
            # 地雷数が不明な場合は分析できない
            return

        # 便利メソッドを使って周辺セルを分類
        hidden_neighbors = self.board_view.get_neighbors_by_state(row, col, CellState.HIDDEN)
        flagged_count = self.board_view.count_neighbors_by_state(row, col, CellState.FLAGGED)

        hidden_count = len(hidden_neighbors)

        # 論理判定のロジック
        if flagged_count == mine_number and hidden_count > 0:
            # フラグ数 = 地雷数 → 残りは安全
            for r, c in hidden_neighbors:
                self._add_to_queue(SolverCommand.dig(r, c))
        elif (flagged_count + hidden_count) == mine_number and hidden_count > 0:
            # フラグ数 + 未発見数 = 地雷数 → 残り全て地雷
            for r, c in hidden_neighbors:
                self._add_to_queue(SolverCommand.flag(r, c))

    def _add_to_queue(self, command: SolverCommand):
        """重複チェックしてキューに追加"""
        if command not in self.action_queue:
            self.action_queue.append(command)

    def has_moves(self) -> bool:
        """
        実行可能な手があるかチェック
        基底クラスのhas_movesメソッドの実装

        Returns:
            手があればTrue、なければFalse
        """
        return len(self.action_queue) > 0

    def reset(self):
        """ソルバーの状態をリセット"""
        self.action_queue.clear()
        self.previous_board_state = None
        self.board_view = None
