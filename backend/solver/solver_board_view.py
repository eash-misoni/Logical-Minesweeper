"""
ソルバー専用の盤面ビュークラス
地雷位置にアクセスできない制限付きビューを提供
"""

from typing import List, Tuple, Optional, TYPE_CHECKING
import sys
import os

# 親ディレクトリのminesweeperモジュールをインポートするための設定
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from minesweeper import CellState

if TYPE_CHECKING:
    from minesweeper import MinesweeperBoard


class SolverBoardView:
    """ソルバー用の盤面情報"""

    def __init__(self, height: int, width: int, cell_states: List[List[CellState]],
                visible_mine_numbers: List[List[Optional[int]]]):
        self.height = height
        self.width = width
        self.cell_states = cell_states
        self.visible_mine_numbers = visible_mine_numbers

    def update_mine_number(self, row: int, col: int, mine_number: int):
        """発見されたセルの地雷数を更新"""
        if self.is_valid_position(row, col):
            self.visible_mine_numbers[row][col] = mine_number

    def get_mine_number(self, row: int, col: int) -> Optional[int]:
        """指定されたセルの地雷数を取得（不明の場合はNone）"""
        if self.is_valid_position(row, col):
            return self.visible_mine_numbers[row][col]
        return None

    def is_mine_number_known(self, row: int, col: int) -> bool:
        """指定されたセルの地雷数が既知かどうか"""
        return self.get_mine_number(row, col) is not None

    def update_multiple_mine_numbers(self, mine_number_updates: List[Tuple[int, int, int]]):
        """複数のセルの地雷数を一括更新"""
        for row, col, mine_number in mine_number_updates:
            self.update_mine_number(row, col, mine_number)

    def update_cell_states(self, new_cell_states: List[List[CellState]]):
        """セル状態を更新（完全置換）"""
        self.cell_states = new_cell_states

    def update_changed_cells(self, new_cell_states: List[List[CellState]],
                            revealed_mine_numbers: List[Tuple[int, int, int]]):
        """変更されたセルのみを効率的に更新

        Args:
            new_cell_states: 新しいセル状態の2次元配列
            revealed_mine_numbers: (row, col, mine_number)のタプルリスト（発見済みセルのみ）
        """
        # セル状態の差分更新
        for row in range(self.height):
            for col in range(self.width):
                if self.cell_states[row][col] != new_cell_states[row][col]:
                    self.cell_states[row][col] = new_cell_states[row][col]

        # 新しく発見されたセルの地雷数を更新
        if revealed_mine_numbers:
            self.update_multiple_mine_numbers(revealed_mine_numbers)

    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """指定された座標の周囲8マスの座標のリストを返す"""
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = row + dr, col + dc
                if self.is_valid_position(new_row, new_col):
                    neighbors.append((new_row, new_col))
        return neighbors

    def is_valid_position(self, row: int, col: int) -> bool:
        """盤面範囲内にちゃんと収まってる？"""
        return 0 <= row < self.height and 0 <= col < self.width

    def count_neighbors_by_state(self, row: int, col: int, target_state: CellState) -> int:
        """指定された状態の隣接セル数をカウント"""
        neighbors = self.get_neighbors(row, col)
        return sum(1 for r, c in neighbors if self.cell_states[r][c] == target_state)

    def get_neighbors_by_state(self, row: int, col: int, target_state: CellState) -> List[Tuple[int, int]]:
        """指定された状態の隣接セルの座標リストを取得"""
        neighbors = self.get_neighbors(row, col)
        return [(r, c) for r, c in neighbors if self.cell_states[r][c] == target_state]
