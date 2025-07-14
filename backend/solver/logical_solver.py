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
from solver_board_view import SolverBoardView
from solver_command import SolverCommand, SolverAction
from solver_move import SolverMove, SolverActionType
from solver_base import SolverBase


class LogicalSolver(SolverBase):
    """論理的に確定する手のみを提案するソルバー"""

    def __init__(self):
        super().__init__()
        self.name = "Logical Certainty Solver"
        self.action_queue = deque()  # 確定した行動のキュー
        self.previous_board_state: Optional[List[List[CellState]]] = None  # 前回の盤面状態

    def set_board(self, solver_board_view: SolverBoardView):
        """盤面を設定（ソルバー用ビューとして）

        Args:
            solver_board_view: SolverBoardViewインスタンス
        """
        self.board_view = solver_board_view

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
            changed_cells = self._detect_changes(self.previous_board_state, self.board_view.cell_states)

        # 差分があるセルについて分析
        for row, col in changed_cells:
            self._analyze_revealed_cell(row, col)

        # 現在の状態を保存（深いコピーを作成）
        self.previous_board_state = [row[:] for row in self.board_view.cell_states]

    def get_next_move(self) -> SolverMove:
        """
        キューから次の有効な確定手を取得
        基底クラスのget_next_moveメソッドの実装

        Returns:
            次に実行すべき確定手
        """
        if self.board_view is None:
            raise ValueError("盤面が設定されていません")

        while self.action_queue:
            move = self.action_queue.popleft()

            # 行動が有効かチェック
            if self._is_move_valid(move):
                return move
            # 無効な場合は次の行動を試す

        # キューが空または全て無効
        return SolverMove(-1, -1, SolverActionType.NO_MOVE)

    def get_next_command(self) -> SolverCommand:
        """
        次の論理的確定手を汎用的なコマンド形式で取得

        Returns:
            実行すべきソルバーコマンド
        """
        move = self.get_next_move()

        if move.action == SolverActionType.SAFE_DIG:
            return SolverCommand.dig(move.row, move.col)
        elif move.action == SolverActionType.CERTAIN_FLAG:
            return SolverCommand.flag(move.row, move.col)
        else:
            return SolverCommand.no_move()

    def _detect_changes(self, previous_state: List[List[CellState]],
                       current_state: List[List[CellState]]) -> List[Tuple[int, int]]:
        """前回から変化したセルを検出"""
        changed_cells = []

        for row in range(len(current_state)):
            for col in range(len(current_state[0])):
                if previous_state[row][col] != current_state[row][col]:
                    # 新たに発見されたセルのみを対象とする
                    if current_state[row][col] == CellState.REVEALED:
                        changed_cells.append((row, col))

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

        # ここに論理判定のロジックを実装してください
        # 例：
        # if flagged_count == mine_number and hidden_count > 0:
        #     for r, c in hidden_neighbors:
        #         self._add_to_queue(LogicalMove(r, c, LogicalAction.SAFE_DIG))
        # elif (flagged_count + hidden_count) == mine_number and hidden_count > 0:
        #     for r, c in hidden_neighbors:
        #         self._add_to_queue(LogicalMove(r, c, LogicalAction.CERTAIN_FLAG))

    def _add_to_queue(self, move: SolverMove):
        """重複チェックしてキューに追加"""
        if move not in self.action_queue:
            self.action_queue.append(move)

    def _is_move_valid(self, move: SolverMove) -> bool:
        """行動が有効かチェック"""
        # 範囲外チェック
        if not self.board_view.is_valid_position(move.row, move.col):
            return False

        cell_state = self.board_view.cell_states[move.row][move.col]

        if move.action == SolverActionType.SAFE_DIG:
            # 掘る行動は未発見のセルのみ有効
            return cell_state == CellState.HIDDEN
        elif move.action == SolverActionType.CERTAIN_FLAG:
            # フラグ行動は未発見のセルのみ有効
            return cell_state == CellState.HIDDEN

        return False

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
