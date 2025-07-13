"""
メッセージ機能のテスト
"""
from game_manager import MinesweeperGame

def test_message_functionality():
    """メッセージ機能をテストする"""
    # 小さい盤面でテスト
    game = MinesweeperGame(5, 5, 3)

    print("=== メッセージ機能テスト ===")
    print(game.board.display_board())

    # 最初の一手
    print("\n1. 最初の一手 (2, 2) を掘る:")
    result = game.execute_command('dig', 2, 2)
    print(f"実行結果: {result}")

    print("\n現在の盤面:")
    print(game.board.display_board())

    # 同じ場所をもう一度掘ろうとする
    print("\n2. 同じ場所 (2, 2) をもう一度掘ろうとする:")
    result = game.execute_command('dig', 2, 2)
    print(f"実行結果: {result}")

    # フラグを立てる
    print("\n3. 位置 (0, 0) にフラグを立てる:")
    result = game.execute_command('flag', 0, 0)
    print(f"実行結果: {result}")

    print("\n現在の盤面:")
    print(game.board.display_board())

    # フラグの立った場所を掘ろうとする
    print("\n4. フラグの立った場所 (0, 0) を掘ろうとする:")
    result = game.execute_command('dig', 0, 0)
    print(f"実行結果: {result}")

    # フラグを外す
    print("\n5. 位置 (0, 0) のフラグを外す:")
    result = game.execute_command('flag', 0, 0)
    print(f"実行結果: {result}")

    print("\n現在の盤面:")
    print(game.board.display_board())

    # 掘られた場所にフラグを立てようとする
    print("\n6. 掘られた場所 (2, 2) にフラグを立てようとする:")
    result = game.execute_command('flag', 2, 2)
    print(f"実行結果: {result}")

    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    test_message_functionality()
