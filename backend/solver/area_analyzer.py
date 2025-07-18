"""
エリアベース論理解法アルゴリズム（第2版）
エリアを削除せずに追加のみで管理し、セル→エリア辞書で効率的な重複検出を行う
"""

from typing import List, Set, Tuple, Optional, Dict
from dataclasses import dataclass

# セルの座標を表す型エイリアス
Cell = Tuple[int, int]  # (row, col)


@dataclass
class Area:
    """エリア（セルの集合）とその地雷数制約を管理するクラス"""
    cells: Set[Cell]
    min_mines: int  # このエリア内の最小地雷数
    max_mines: int  # このエリア内の最大地雷数

    def __post_init__(self):
        """データクラス初期化後の検証"""
        if self.min_mines > self.max_mines:
            raise ValueError(f"min_mines ({self.min_mines}) > max_mines ({self.max_mines})")
        if self.min_mines < 0:
            raise ValueError(f"min_mines ({self.min_mines}) < 0")
        if self.max_mines > len(self.cells):
            raise ValueError(f"max_mines ({self.max_mines}) > cells count ({len(self.cells)})")

    def is_fully_determined(self) -> bool:
        """地雷数が完全に確定しているか（min == max）"""
        return self.min_mines == self.max_mines

    def is_all_mines(self) -> bool:
        """全セルが地雷確定か"""
        return self.min_mines == len(self.cells)

    def is_all_safe(self) -> bool:
        """全セルが安全確定か"""
        return self.max_mines == 0

    def overlaps_with(self, other: 'Area') -> bool:
        """他のエリアと重複があるか"""
        return bool(self.cells & other.cells)

    def get_overlap_cells(self, other: 'Area') -> Set[Cell]:
        """他のエリアとの重複セルを取得"""
        return self.cells & other.cells


class AreaAnalyzer:
    """エリアベースの論理解法アルゴリズム（第2版）"""

    def __init__(self):
        """空のAreaAnalyzerを初期化"""
        self.areas: List[Optional[Area]] = []  # エリアリスト（削除されたエリアはNone）
        self.cell_to_areas: Dict[Cell, List[int]] = {}  # セル→エリアID一覧のマッピング
        self.next_area_id = 0  # 次に割り当てるエリアID

    def _find_same_cell_area(self, area: Area) -> Optional[int]:
        """同じセル集合を持つ既存エリアを探し、あればそのIDを返す"""
        if not area.cells:
            return None

        # 1つの代表セルで既存エリアを検索
        sample_cell = next(iter(area.cells))
        if sample_cell not in self.cell_to_areas:
            return None

        for existing_id in self.cell_to_areas[sample_cell]:
            if self.areas[existing_id] is not None:
                existing_area = self.areas[existing_id]
                if existing_area.cells == area.cells:
                    return existing_id

        return None

    def _update_area_constraints(self, area_id: int, new_min: int, new_max: int):
        """既存エリアの制約をより厳しい値に更新"""
        if area_id >= len(self.areas) or self.areas[area_id] is None:
            return

        existing_area = self.areas[area_id]
        updated_min = max(existing_area.min_mines, new_min)
        updated_max = min(existing_area.max_mines, new_max)

        # 制約が無効になった場合（min > max）は何もしない
        if updated_min <= updated_max:
            self.areas[area_id] = Area(existing_area.cells, updated_min, updated_max)

    def _add_area(self, area: Area) -> int:
        """エリアを追加し、セル→エリア辞書を更新"""
        # 同じセル集合のエリアをチェック
        same_cell_id = self._find_same_cell_area(area)
        if same_cell_id is not None:
            # 既存エリアの制約をより厳しく更新
            self._update_area_constraints(same_cell_id, area.min_mines, area.max_mines)
            return same_cell_id

        area_id = self.next_area_id
        self.next_area_id += 1

        # エリアリストに追加
        self.areas.append(area)

        # セル→エリア辞書を更新
        for cell in area.cells:
            if cell not in self.cell_to_areas:
                self.cell_to_areas[cell] = []
            self.cell_to_areas[cell].append(area_id)

        return area_id

    def _remove_area(self, area_id: int):
        """エリアを削除し、セル→エリア辞書を更新"""
        if area_id >= len(self.areas) or self.areas[area_id] is None:
            return

        area = self.areas[area_id]

        # セル→エリア辞書からエリアIDを削除
        for cell in area.cells:
            if cell in self.cell_to_areas:
                if area_id in self.cell_to_areas[cell]:
                    self.cell_to_areas[cell].remove(area_id)

        # エリアリストからエリアを削除（メモリ効率のためNoneに）
        self.areas[area_id] = None

    def _get_overlapping_area_ids(self, target_area: Area) -> Set[int]:
        """指定エリアと重複する既存エリアのIDを取得"""
        overlapping_ids = set()

        for cell in target_area.cells:
            if cell in self.cell_to_areas:
                overlapping_ids.update(self.cell_to_areas[cell])

        return overlapping_ids

    def _merge_two_areas(self, area1: Area, area2: Area) -> Tuple[List[Area], Set[Cell], Set[Cell]]:
        """
        2つのエリアをマージして新エリアリストを作成

        Returns:
            (新エリアリスト, 確定安全セル, 確定地雷セル)
        """
        overlap = area1.get_overlap_cells(area2)
        area1_only = area1.cells - overlap
        area2_only = area2.cells - overlap

        new_areas = []
        safe_cells = set()
        mine_cells = set()

        # A ∩ B（重複部分）
        if overlap:
            min_overlap = max(0,
                            area1.min_mines - len(area1_only),
                            area2.min_mines - len(area2_only))
            max_overlap = min(len(overlap),
                            area1.max_mines,
                            area2.max_mines)

            if min_overlap <= max_overlap:
                area = Area(overlap, min_overlap, max_overlap)
                if area.is_all_safe():
                    safe_cells.update(area.cells)
                elif area.is_all_mines():
                    mine_cells.update(area.cells)
                else:
                    new_areas.append(area)

        # A \ B（area1のみ）
        if area1_only:
            min_a_only = max(0, area1.min_mines - max_overlap if overlap else area1.min_mines)
            max_a_only = min(len(area1_only), area1.max_mines - min_overlap if overlap else area1.max_mines)

            if min_a_only <= max_a_only:
                area = Area(area1_only, min_a_only, max_a_only)
                if area.is_all_safe():
                    safe_cells.update(area.cells)
                elif area.is_all_mines():
                    mine_cells.update(area.cells)
                else:
                    new_areas.append(area)

        # B \ A（area2のみ）
        if area2_only:
            min_b_only = max(0, area2.min_mines - max_overlap if overlap else area2.min_mines)
            max_b_only = min(len(area2_only), area2.max_mines - min_overlap if overlap else area2.max_mines)

            if min_b_only <= max_b_only:
                area = Area(area2_only, min_b_only, max_b_only)
                if area.is_all_safe():
                    safe_cells.update(area.cells)
                elif area.is_all_mines():
                    mine_cells.update(area.cells)
                else:
                    new_areas.append(area)

        return new_areas, safe_cells, mine_cells

    def _remove_areas_overlapping_with_cells(self, determined_cells: Set[Cell]):
        """確定セルと重複するエリアを削除"""
        areas_to_remove = set()

        for cell in determined_cells:
            if cell in self.cell_to_areas:
                areas_to_remove.update(self.cell_to_areas[cell])

        for area_id in areas_to_remove:
            self._remove_area(area_id)

    def add_constraint_area(self, new_area: Area) -> Tuple[Set[Cell], Set[Cell]]:
        """
        制約エリアを追加し、重複エリアとマージ処理を実行

        Returns:
            (確定した安全セル, 確定した地雷セル)のタプル
        """
        # 重複エリアIDを取得
        overlapping_ids = self._get_overlapping_area_ids(new_area)

        all_safe_cells = set()
        all_mine_cells = set()

        # 重複エリアがある場合はマージ処理
        if overlapping_ids:
            # 各重複エリアと個別にマージ
            for area_id in overlapping_ids:
                if self.areas[area_id] is not None:  # エリアが削除されていない場合のみ
                    existing_area = self.areas[area_id]
                    new_areas, safe_cells, mine_cells = self._merge_two_areas(new_area, existing_area)

                    # 確定セルを累積
                    all_safe_cells.update(safe_cells)
                    all_mine_cells.update(mine_cells)

                    # 新エリアを追加
                    for area in new_areas:
                        self._add_area(area)

                    # 確定セルがある場合、即座に重複エリアを削除
                    if safe_cells or mine_cells:
                        determined_cells = safe_cells | mine_cells
                        self._remove_areas_overlapping_with_cells(determined_cells)
        else:
            # 重複エリアがない場合は単純に追加
            if new_area.is_all_safe():
                all_safe_cells.update(new_area.cells)
            elif new_area.is_all_mines():
                all_mine_cells.update(new_area.cells)
            else:
                self._add_area(new_area)

        return all_safe_cells, all_mine_cells

    def get_area_count(self) -> int:
        """現在のアクティブなエリア数を取得"""
        return sum(1 for area in self.areas if area is not None)

    def get_active_areas(self) -> List[Area]:
        """現在のアクティブなエリアのリストを取得"""
        return [area for area in self.areas if area is not None]

    def reset(self, width: int = 0, height: int = 0, total_mines: int = 0) -> Tuple[Set[Cell], Set[Cell]]:
        """
        エリア情報をリセットし、必要に応じて全体制約を設定
        
        Args:
            width: 盤面の幅（0の場合は全体制約を設定しない）
            height: 盤面の高さ（0の場合は全体制約を設定しない）
            total_mines: 盤面全体の地雷数
        
        Returns:
            (確定した安全セル, 確定した地雷セル)のタプル
        """
        # 既存データをクリア
        self.areas.clear()
        self.cell_to_areas.clear()
        self.next_area_id = 0
        
        # 全体制約エリアを追加
        if width > 0 and height > 0:
            all_cells = {(row, col) for row in range(height) for col in range(width)}
            global_area = Area(all_cells, total_mines, total_mines)
            return self.add_constraint_area(global_area)
        
        return set(), set()

    def initialize(self, width: int, height: int, total_mines: int) -> Tuple[Set[Cell], Set[Cell]]:
        """
        初期化専用メソッド（内部でresetを呼び出し）
        
        Args:
            width: 盤面の幅
            height: 盤面の高さ
            total_mines: 盤面全体の地雷数
        
        Returns:
            (確定した安全セル, 確定した地雷セル)のタプル
        """
        return self.reset(width, height, total_mines)

    def clear(self):
        """エリア情報をクリア（resetの引数なし版）"""
        self.reset()
