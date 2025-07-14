"""
ソルバーコマンド定義
ソルバーからの指示を表現する汎用的なデータクラス
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class SolverAction(Enum):
    """ソルバーの行動種類"""
    DIG = "dig"           # セルを掘る
    FLAG = "flag"         # フラグを設置/解除
    NO_MOVE = "no_move"   # 論理的に確定する手がない


@dataclass
class SolverCommand:
    """ソルバーからの指示コマンド"""
    action: SolverAction
    row: Optional[int] = None
    col: Optional[int] = None

    def __post_init__(self):
        """バリデーション"""
        if self.action in (SolverAction.DIG, SolverAction.FLAG):
            if self.row is None or self.col is None:
                raise ValueError(f"{self.action.value} requires both row and col")
        elif self.action == SolverAction.NO_MOVE:
            if self.row is not None or self.col is not None:
                raise ValueError("NO_MOVE should not have row or col")

    @classmethod
    def dig(cls, row: int, col: int) -> 'SolverCommand':
        """掘るコマンドを作成"""
        return cls(SolverAction.DIG, row, col)

    @classmethod
    def flag(cls, row: int, col: int) -> 'SolverCommand':
        """フラグコマンドを作成"""
        return cls(SolverAction.FLAG, row, col)

    @classmethod
    def no_move(cls) -> 'SolverCommand':
        """手がないコマンドを作成"""
        return cls(SolverAction.NO_MOVE)

    def __str__(self):
        if self.action == SolverAction.NO_MOVE:
            return "No logical move available"
        return f"{self.action.value.capitalize()} at ({self.row}, {self.col})"
