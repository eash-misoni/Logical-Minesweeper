"""
AreaAnalyzer（第2版）の基本テスト
エリア削除せずに追加のみで管理する新方式のテスト
"""

import sys
import os

# 親ディレクトリのminesweeperモジュールをインポートするための設定
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solver.area_analyzer import AreaAnalyzer, Area


def test_basic_area_operations():
    """基本的なエリア操作のテスト"""
    print("=== エリア基本操作テスト ===")

    # エリア作成
    area1 = Area({(0, 0), (0, 1)}, min_mines=1, max_mines=1)
    area2 = Area({(0, 1), (1, 0)}, min_mines=0, max_mines=2)

    print(f"エリア1: {len(area1.cells)}セル, 地雷数: {area1.min_mines}-{area1.max_mines}")
    print(f"エリア2: {len(area2.cells)}セル, 地雷数: {area2.min_mines}-{area2.max_mines}")
    print(f"エリア1と2は重複: {area1.overlaps_with(area2)}")
    print(f"重複セル: {area1.get_overlap_cells(area2)}")
    print(f"安全エリア: {area1.is_all_safe()}")
    print(f"地雷エリア: {area1.is_all_mines()}")


def test_area_analyzer_basic():
    """AreaAnalyzerの基本機能テスト"""
    print("\n=== AreaAnalyzer基本テスト ===")

    analyzer = AreaAnalyzer()
    safe_cells, mine_cells = analyzer.initialize(2, 2, 2)
    print(f"初期化後エリア数: {analyzer.get_area_count()}")

    if analyzer.get_area_count() > 0:
        print(f"全体制約エリア: {len(analyzer.get_active_areas()[0].cells)}セル")
    else:
        print("全体制約エリアが作成されていません")

    # エリア追加
    cells = {(0, 0), (0, 1), (1, 0)}
    area = Area(cells, min_mines=1, max_mines=1)
    safe_cells, mine_cells = analyzer.add_constraint_area(area)

    print(f"制約エリア追加後: {analyzer.get_area_count()}個のエリア")
    print(f"確定セル: 安全={len(safe_cells)}個, 地雷={len(mine_cells)}個")


def test_merge_with_global_constraint():
    """全体制約との複雑なマージテスト"""
    print("\n=== 全体制約マージテスト ===")

    # 3x3盤面、地雷数2
    analyzer = AreaAnalyzer()
    safe_cells, mine_cells = analyzer.initialize(3, 3, 2)
    print(f"初期状態: {analyzer.get_area_count()}個のエリア")

    # 部分制約を追加（全体制約と重複）
    partial_area = Area({(0, 0), (0, 1), (1, 0)}, min_mines=1, max_mines=1)
    safe_cells, mine_cells = analyzer.add_constraint_area(partial_area)

    print(f"部分制約追加後: {analyzer.get_area_count()}個のエリア")
    print(f"確定セル: 安全={len(safe_cells)}個, 地雷={len(mine_cells)}個")

    for i, area in enumerate(analyzer.get_active_areas()):
        print(f"  エリア{i+1}: {len(area.cells)}セル, 地雷数: {area.min_mines}-{area.max_mines}")


def test_determined_cell_removal():
    """確定セルによるエリア削除テスト"""
    print("\n=== 確定セル削除テスト ===")

    analyzer = AreaAnalyzer()
    safe_cells, mine_cells = analyzer.initialize(2, 3, 1)
    print(f"初期エリア数: {analyzer.get_area_count()}")

    # 単一セル確定エリアを追加
    mine_area = Area({(0, 0)}, min_mines=1, max_mines=1)
    safe_cells, mine_cells = analyzer.add_constraint_area(mine_area)

    print(f"地雷確定エリア追加後: {analyzer.get_area_count()}個のエリア")
    print(f"地雷確定セル: {mine_cells}")
    print(f"安全確定セル: {safe_cells}")

    if mine_cells:
        print(f"  地雷確定セル: {mine_cells}")

    for i, area in enumerate(analyzer.get_active_areas()):
        print(f"  エリア{i+1}: {len(area.cells)}セル, 地雷数: {area.min_mines}-{area.max_mines}")


def test_multiple_overlapping_merge():
    """複数エリアとの重複マージテスト"""
    print("\n=== 複数重複マージテスト ===")

    analyzer = AreaAnalyzer()
    safe_cells, mine_cells = analyzer.initialize(3, 3, 3)

    # 複数の部分制約を順次追加
    area1 = Area({(0, 0), (0, 1)}, min_mines=1, max_mines=1)
    area2 = Area({(1, 0), (1, 1)}, min_mines=0, max_mines=1)
    area3 = Area({(2, 0), (2, 1)}, min_mines=1, max_mines=1)

    analyzer.add_constraint_area(area1)
    print(f"エリア1追加後: {analyzer.get_area_count()}個のエリア")

    analyzer.add_constraint_area(area2)
    print(f"エリア2追加後: {analyzer.get_area_count()}個のエリア")

    analyzer.add_constraint_area(area3)
    print(f"エリア3追加後: {analyzer.get_area_count()}個のエリア")

    # 複数エリアと重複する新エリアを追加
    new_area = Area({(0, 1), (1, 1), (2, 1)}, min_mines=2, max_mines=2)
    print(f"\n新エリア追加: セル{new_area.cells}, 地雷{new_area.min_mines}-{new_area.max_mines}")

    safe_cells, mine_cells = analyzer.add_constraint_area(new_area)

    print(f"追加後: 安全={len(safe_cells)}個, 地雷={len(mine_cells)}個, エリア数={analyzer.get_area_count()}")
    if safe_cells:
        print(f"  安全確定セル: {safe_cells}")
    if mine_cells:
        print(f"  地雷確定セル: {mine_cells}")

    for i, area in enumerate(analyzer.get_active_areas()):
        print(f"  エリア{i+1}: {len(area.cells)}セル, 地雷数: {area.min_mines}-{area.max_mines}")


def test_cascade_determination():
    """連鎖的確定のテスト"""
    print("\n=== 連鎖確定テスト ===")

    analyzer = AreaAnalyzer()
    safe_cells, mine_cells = analyzer.initialize(5, 1, 2)

    # 連鎖確定を引き起こすエリア群を構築
    area1 = Area({(0, 0), (0, 1), (0, 2)}, min_mines=1, max_mines=1)
    area2 = Area({(0, 2), (0, 3), (0, 4)}, min_mines=1, max_mines=1)

    safe_cells, mine_cells = analyzer.add_constraint_area(area1)
    print(f"エリア1追加後: 安全={len(safe_cells)}個, 地雷={len(mine_cells)}個, エリア数={analyzer.get_area_count()}")
    if safe_cells:
        print(f"  安全確定セル: {safe_cells}")
    if mine_cells:
        print(f"  地雷確定セル: {mine_cells}")
    for i, area in enumerate(analyzer.get_active_areas()):
        print(f"  エリア{i+1}: {len(area.cells)}セル, 地雷数: {area.min_mines}-{area.max_mines}")
        print(f"  セル: {area.cells}")

    safe_cells, mine_cells = analyzer.add_constraint_area(area2)
    print(f"エリア2追加後: 安全={len(safe_cells)}個, 地雷={len(mine_cells)}個, エリア数={analyzer.get_area_count()}")
    if safe_cells:
        print(f"  安全確定セル: {safe_cells}")
    if mine_cells:
        print(f"  地雷確定セル: {mine_cells}")
    for i, area in enumerate(analyzer.get_active_areas()):
        print(f"  エリア{i+1}: {len(area.cells)}セル, 地雷数: {area.min_mines}-{area.max_mines}")
        print(f"  セル: {area.cells}")

    # さらに制約を追加して確定を発生させる
    area3 = Area({(0, 1), (0, 2), (0, 3)}, min_mines=0, max_mines=0)  # 全て安全
    safe_cells, mine_cells = analyzer.add_constraint_area(area3)
    print(f"エリア3追加後: 安全={len(safe_cells)}個, 地雷={len(mine_cells)}個, エリア数={analyzer.get_area_count()}")
    if safe_cells:
        print(f"  安全確定セル: {safe_cells}")
    if mine_cells:
        print(f"  地雷確定セル: {mine_cells}")
    for i, area in enumerate(analyzer.get_active_areas()):
        print(f"  エリア{i+1}: {len(area.cells)}セル, 地雷数: {area.min_mines}-{area.max_mines}")
        print(f"  セル: {area.cells}")


def test_cell_to_areas_consistency():
    """セル→エリア辞書の整合性テスト"""
    print("\n=== セル→エリア辞書整合性テスト ===")

    analyzer = AreaAnalyzer()
    safe_cells, mine_cells = analyzer.initialize(2, 2, 1)

    # セル辞書の内容確認
    print("初期セル→エリア辞書:")
    for cell, area_ids in analyzer.cell_to_areas.items():
        print(f"  {cell}: {area_ids}")

    # エリア追加
    area = Area({(0, 0), (0, 1)}, min_mines=1, max_mines=1)
    analyzer.add_constraint_area(area)

    print("\nエリア追加後のセル→エリア辞書:")
    for cell, area_ids in analyzer.cell_to_areas.items():
        print(f"  {cell}: {area_ids}")

    print(f"\nアクティブエリア数: {analyzer.get_area_count()}")


def test_edge_cases():
    """エッジケースのテスト"""
    print("\n=== エッジケーステスト ===")

    analyzer = AreaAnalyzer()
    safe_cells, mine_cells = analyzer.initialize(1, 1, 1)
    print(f"1x1盤面初期状態: {analyzer.get_area_count()}個のエリア")

    # 単一セル全地雷エリア
    all_mine_area = Area({(0, 0)}, min_mines=1, max_mines=1)
    safe_cells, mine_cells = analyzer.add_constraint_area(all_mine_area)

    print(f"全地雷エリア追加後: {analyzer.get_area_count()}個のエリア")
    print(f"確定セル: 安全={len(safe_cells)}個, 地雷={len(mine_cells)}個")

    if mine_cells:
        print(f"  地雷確定セル: {mine_cells}")

    # 空の制約（0地雷エリア）テスト
    analyzer2 = AreaAnalyzer()
    safe_cells, mine_cells = analyzer2.initialize(2, 1, 0)
    empty_constraint = Area({(0, 0), (0, 1)}, min_mines=0, max_mines=0)
    safe_cells, mine_cells = analyzer2.add_constraint_area(empty_constraint)

    print(f"\n空制約テスト: 安全={len(safe_cells)}個, 地雷={len(mine_cells)}個")
    if safe_cells:
        print(f"  安全確定セル: {safe_cells}")


def test_area_id_management():
    """エリアID管理のテスト"""
    print("\n=== エリアID管理テスト ===")

    analyzer = AreaAnalyzer()
    safe_cells, mine_cells = analyzer.initialize(3, 1, 1)
    print(f"初期next_area_id: {analyzer.next_area_id}")

    # 複数エリア追加
    area1 = Area({(0, 0)}, min_mines=0, max_mines=0)
    area2 = Area({(0, 1)}, min_mines=1, max_mines=1)

    analyzer.add_constraint_area(area1)
    print(f"エリア1追加後: next_area_id={analyzer.next_area_id}, アクティブ数={analyzer.get_area_count()}")

    analyzer.add_constraint_area(area2)
    print(f"エリア2追加後: next_area_id={analyzer.next_area_id}, アクティブ数={analyzer.get_area_count()}")

    print(f"エリアリスト長: {len(analyzer.areas)}")
    print(f"None要素数: {sum(1 for area in analyzer.areas if area is None)}")


def test_constraint_integration():
    """制約統合機能のテスト"""
    print("\n=== 制約統合テスト ===")
    
    analyzer = AreaAnalyzer()
    analyzer.reset()  # 空で初期化
    
    # 同じセル集合で異なる制約のエリアを追加
    cells = {(0, 0), (0, 1)}
    area1 = Area(cells, min_mines=0, max_mines=2)
    area2 = Area(cells, min_mines=1, max_mines=1)
    
    id1 = analyzer._add_area(area1)
    print(f"エリア1追加: ID={id1}, 制約={analyzer.areas[id1].min_mines}-{analyzer.areas[id1].max_mines}")
    
    id2 = analyzer._add_area(area2)
    print(f"エリア2追加: ID={id2}, 制約={analyzer.areas[id2].min_mines}-{analyzer.areas[id2].max_mines}")
    
    if id1 == id2:
        print("✓ 同じセル集合のエリアが統合された")
        print(f"統合後制約: {analyzer.areas[id1].min_mines}-{analyzer.areas[id1].max_mines}")
    else:
        print("✗ エリアが統合されなかった")
    
    print(f"総エリア数: {analyzer.get_area_count()}")


if __name__ == "__main__":
    test_basic_area_operations()
    test_area_analyzer_basic()
    test_merge_with_global_constraint()
    test_determined_cell_removal()
    test_multiple_overlapping_merge()
    test_cascade_determination()
    test_cell_to_areas_consistency()
    test_edge_cases()
    test_area_id_management()
    test_constraint_integration()
    print("\n=== 全テスト完了 ===")
