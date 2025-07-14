"""
ソルバーで使用する内部データ構造
SolverMoveとSolverActionTypeの定義
"""

from enum import Enum


class SolverActionType(Enum):
    """ソルバーが確定した行動の種類"""
    SAFE_DIG = "safe_dig"          # 100%安全に掘れる
    CERTAIN_FLAG = "certain_flag"  # 100%地雷確定
    NO_MOVE = "no_move"           # 確定できない


class SolverMove:
    """ソルバーが確定した手の情報"""

    def __init__(self, row: int, col: int, action: SolverActionType):
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
