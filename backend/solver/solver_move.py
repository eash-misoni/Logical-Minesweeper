"""
ソルバーで使用する内部データ構造
SolverMoveの定義
"""

from .solver_command import SolverAction


class SolverMove:
    """ソルバーが確定した手の情報"""

    def __init__(self, row: int, col: int, action: SolverAction):
        self.row = row
        self.col = col
        self.action = action

    def __repr__(self):
        return f"SolverMove({self.row}, {self.col}, {self.action.value})"

    def __eq__(self, other):
        if not isinstance(other, SolverMove):
            return False
        return (self.row, self.col, self.action) == (other.row, other.col, other.action)

    def __hash__(self):
        return hash((self.row, self.col, self.action))
