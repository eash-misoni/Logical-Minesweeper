import random
from enum import Enum
from typing import List, Tuple, Set

class CellState(Enum):
    """マスの状態を表す列挙型"""
    HIDDEN = 0      # 未発見
    REVEALED = 1    # 発見済み
    FLAGGED = 2     # フラグ付き

class GameState(Enum):
    """ゲームの状態を表す列挙型"""
    PLAYING = 0     # プレイ中
    WON = 1         # 勝利
    LOST = 2        # 敗北

class MinesweeperBoard:
    """マインスイーパーの盤面クラス"""

    def __init__(self, height: int, width: int, mine_count: int):
        """
        マインスイーパーの盤面を初期化

        Args:
            height: 盤面の高さ
            width: 盤面の幅
            mine_count: 地雷の数
        """
        self.height = height
        self.width = width
        self.mine_count = mine_count
        self.first_click = True
        self.game_state = GameState.PLAYING

        # 盤面の状態を初期化
        self.mines: List[List[bool]] = [[False for _ in range(width)] for _ in range(height)]
        self.cell_states: List[List[CellState]] = [[CellState.HIDDEN for _ in range(width)] for _ in range(height)]
        self.mine_numbers: List[List[int]] = [[0 for _ in range(width)] for _ in range(height)]

    def _is_valid_position(self, row: int, col: int) -> bool:
        """盤面範囲内にちゃんと収まってる？"""
        return 0 <= row < self.height and 0 <= col < self.width

    def _get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """指定された座標の周囲8マスの座標のリストを返すよ"""
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = row + dr, col + dc
                if self._is_valid_position(new_row, new_col):
                    neighbors.append((new_row, new_col))
        return neighbors

    def generate_mines(self, first_click_row: int, first_click_col: int):
        """
        地雷をランダム生成（最初の一手以外の場所に配置）

        Args:
            first_click_row: 最初にクリックした行
            first_click_col: 最初にクリックした列
        """

        # 最初のクリック位置中心の3x3マスを地雷生成除外エリアとして設定
        excluded_positions = set()
        excluded_positions.add((first_click_row, first_click_col))
        for neighbor in self._get_neighbors(first_click_row, first_click_col):
            excluded_positions.add(neighbor)

        # 利用可能な位置のリストを作成
        available_positions = []
        for row in range(self.height):
            for col in range(self.width):
                if (row, col) not in excluded_positions:
                    available_positions.append((row, col))

        # 地雷数が多すぎたらダメだ
        if self.mine_count > len(available_positions):
            raise ValueError("地雷数が多すぎます")

        # 地雷配置する～
        mine_positions = random.sample(available_positions, self.mine_count)
        for row, col in mine_positions:
            self.mines[row][col] = True

        # 各マスの周囲の地雷数をmine_numbersに記入
        self._calculate_mine_numbers()

        self.first_click = False

    def _calculate_mine_numbers(self):
        """各マスの周囲の地雷数をmine_numbersに記入"""
        for row in range(self.height):
            for col in range(self.width):
                if not self.mines[row][col]:
                    count = 0
                    for neighbor_row, neighbor_col in self._get_neighbors(row, col):
                        if self.mines[neighbor_row][neighbor_col]:
                            count += 1
                    self.mine_numbers[row][col] = count

    def dig(self, row: int, col: int) -> bool:
        """
        指定された位置を掘るよ
        最初の一手の場合は地雷も生成されるよ

        Args:
            row: 行
            col: 列

        Returns:
            bool: 成功した場合True、地雷を踏んだ場合False
        """
        if not self._is_valid_position(row, col):
            raise ValueError("指定された位置が盤面外です")

        # 既に発見済みまたはフラグ付きの場合は何もしない
        if self.cell_states[row][col] != CellState.HIDDEN:
            return True

        # 最初のクリックの場合、専用メソッドを呼び出して地雷配置を行う
        if self.first_click:
            return self._first_dig(row, col)

        # 二手目以降の通常のdig
        return self._normal_dig(row, col)

    def _first_dig(self, row: int, col: int) -> bool:
        """
        地雷生成を含むしてから最初の一手を掘るよ

        Args:
            row: 行
            col: 列

        Returns:
            bool: 常にTrue（最初の一手は必ず安全）
        """
        # 地雷を生成
        self.generate_mines(row, col)

        # 掘る
        self._reveal_cell(row, col)

        # 勝利条件をチェック
        self._check_win_condition()

        return True

    def _normal_dig(self, row: int, col: int) -> bool:
        """
        二手目以降の通常のdig

        Args:
            row: 行
            col: 列

        Returns:
            bool: 成功した場合True、地雷を踏んだ場合False
        """
        # 地雷を踏んだ場合
        if self.mines[row][col]:
            self.cell_states[row][col] = CellState.REVEALED
            self.game_state = GameState.LOST
            return False

        # 掘るぜ
        self._reveal_cell(row, col)

        # 勝利条件をチェック
        self._check_win_condition()

        return True

    def _reveal_cell(self, row: int, col: int):
        """マスを発見状態にし、周囲の0のマスも展開するよね"""

        if self.cell_states[row][col] != CellState.HIDDEN:
            return

        if self.mines[row][col]:
            return

        self.cell_states[row][col] = CellState.REVEALED

        # 周囲に地雷がない場合、自動的に周囲も展開
        if self.mine_numbers[row][col] == 0:
            for neighbor_row, neighbor_col in self._get_neighbors(row, col):
                self._reveal_cell(neighbor_row, neighbor_col)

    def toggle_flag(self, row: int, col: int):
        """フラグを切り替え"""
        if not self._is_valid_position(row, col):
            raise ValueError("指定された位置が盤面外です")

        if self.game_state != GameState.PLAYING:
            return

        if self.cell_states[row][col] == CellState.HIDDEN:
            self.cell_states[row][col] = CellState.FLAGGED
        elif self.cell_states[row][col] == CellState.FLAGGED:
            self.cell_states[row][col] = CellState.HIDDEN

    def _check_win_condition(self):
        """勝利条件をチェックしてgame_stateを更新"""
        for row in range(self.height):
            for col in range(self.width):
                if not self.mines[row][col] and self.cell_states[row][col] == CellState.HIDDEN:
                    return  # まだ未発見の安全なマスがある

        self.game_state = GameState.WON

    def get_cell_display(self, row: int, col: int) -> str:
        """指定された位置のマスの表示文字を取得"""
        if not self._is_valid_position(row, col):
            return "?"

        state = self.cell_states[row][col]

        if state == CellState.FLAGGED:
            return "F"
        elif state == CellState.HIDDEN:
            return "."
        elif state == CellState.REVEALED:
            if self.mines[row][col]:
                return "*"
            elif self.mine_numbers[row][col] == 0:
                return " "
            else:
                return str(self.mine_numbers[row][col])

        return "?"

    def display_board(self, show_mines: bool = False) -> str:
        """
        盤面を文字列として表示します

        Args:
            show_mines: 地雷の位置を表示するか（デバッグ用）

        Returns:
            str: 盤面の文字列表現
        """
        result = []

        # 列番号のヘッダー
        header = "   " + "".join(f"{i%10}" for i in range(self.width))
        result.append(header)

        # 各行を表示
        for row in range(self.height):
            row_str = f"{(row%10):2} "
            for col in range(self.width):
                if show_mines and self.mines[row][col]:
                    row_str += "*"
                else:
                    row_str += self.get_cell_display(row, col)
            result.append(row_str)

        # ゲーム状態の表示
        if self.game_state == GameState.WON:
            result.append("\n勝利！")
        elif self.game_state == GameState.LOST:
            result.append("\n敗北...")

        return "\n".join(result)

    def get_remaining_mines(self) -> int:
        """残りの地雷数を取得（地雷数-フラグ数）"""
        flagged_count = sum(
            1 for row in range(self.height)
            for col in range(self.width)
            if self.cell_states[row][col] == CellState.FLAGGED
        )
        return self.mine_count - flagged_count

    def is_game_over(self) -> bool:
        """ゲームが終了しているかチェック"""
        return self.game_state != GameState.PLAYING

    def get_game_state(self) -> GameState:
        """現在のゲーム状態を取得"""
        return self.game_state


# 使用例とテスト用のコード
if __name__ == "__main__":
    # 20x16の盤面に40個の地雷で新しいゲームを開始
    board = MinesweeperBoard(20, 16, 40)

    print("マインスイーパーの盤面（初期状態）:")
    print(board.display_board())

    # 最初の一手（5, 5）を掘る
    print(f"\n位置 (5, 5) を掘ります...")
    success = board.dig(5, 5)
    print(f"結果: {'成功' if success else '地雷を踏みました'}")

    print("\n掘った後の盤面:")
    print(board.display_board())

    print(f"\n残り地雷数: {board.get_remaining_mines()}")
    print(f"ゲーム状態: {board.get_game_state().name}")
