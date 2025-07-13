from minesweeper import MinesweeperBoard, GameState, CellState
import sys

class MinesweeperGame:
    """マインスイーパーゲームマネージャー"""

    def __init__(self, height: int = 9, width: int = 9, mine_count: int = 10):
        """
        ゲームマネージャーを初期化

        Args:
            height: 盤面の高さ
            width: 盤面の幅
            mine_count: 地雷の数
        """
        self.board = MinesweeperBoard(height, width, mine_count)
        self.turn_count = 0

    def display_help(self):
        """ヘルプを表示"""
        print("\n=== コマンド ===")
        print("  d y x : 位置 (y, x) を掘る")
        print("  f y x : 位置 (y, x) にフラグを立てる/外す")
        print("  h     : ヘルプを表示")
        print("  q     : ゲームを終了")
        print("例: d 0 1 → 0行1列を掘る")
        print("    f 2 3 → 2行3列にフラグを立てる\n")

    def parse_command(self, command: str):
        """
        コマンドを解析

        Args:
            command: ユーザー入力のコマンド

        Returns:
            tuple: (action, row, col) または None
        """
        parts = command.strip().lower().split()

        if not parts:
            return None

        if parts[0] == 'h':
            return ('help', None, None)
        elif parts[0] == 'q':
            return ('quit', None, None)
        elif parts[0] in ['d', 'f'] and len(parts) == 3:
            try:
                action = 'dig' if parts[0] == 'd' else 'flag'
                row = int(parts[1])
                col = int(parts[2])
                return (action, row, col)
            except ValueError:
                return None

        return None

    def execute_command(self, action: str, row: int, col: int) -> bool:
        """
        コマンドを実行

        Args:
            action: 'dig' または 'flag'
            row: 行
            col: 列

        Returns:
            bool: 実行が成功したかどうか
        """
        try:
            # 位置の妥当性チェック
            if not (0 <= row < self.board.height and 0 <= col < self.board.width):
                print(f"❌ 無効な位置です: ({row}, {col})")
                return False

            if action == 'dig':
                if self.board.is_game_over():
                    print("ゲームは既に終了しています。")
                    return False

                # digの前にセルの状態をチェック
                current_state = self.board.cell_states[row][col]
                if current_state == CellState.REVEALED:
                    print(f"⚠️ 位置 ({row}, {col}) は既に掘られています")
                    return True
                elif current_state == CellState.FLAGGED:
                    print(f"⚠️ 位置 ({row}, {col}) にはフラグが立っています。先にフラグを外してください")
                    return True

                success = self.board.dig(row, col)
                if not success:
                    print(f"💥 地雷を踏みました！位置: ({row}, {col})")
                else:
                    print(f"✅ 位置 ({row}, {col}) を掘りました")

            elif action == 'flag':
                if self.board.is_game_over():
                    print("ゲームは既に終了しています。")
                    return False

                # flagの前にセルの状態をチェック
                current_state = self.board.cell_states[row][col]
                if current_state == CellState.REVEALED:
                    print(f"⚠️ 位置 ({row}, {col}) は既に掘られているため、フラグを立てることはできません")
                    return True

                old_state = current_state
                self.board.toggle_flag(row, col)

                if old_state == CellState.FLAGGED:
                    print(f"🚩 位置 ({row}, {col}) のフラグを外しました")
                else:
                    print(f"🚩 位置 ({row}, {col}) にフラグを立てました")

            return True

        except ValueError as e:
            print(f"❌ エラー: {e}")
            return False
        except Exception as e:
            print(f"❌ 予期しないエラー: {e}")
            return False

    def display_game_status(self):
        """ゲーム状態を表示"""
        print(f"\n=== ターン {self.turn_count} ===")
        print(self.board.display_board())
        print(f"残り地雷数: {self.board.get_remaining_mines()}")

        # ゲーム終了判定
        if self.board.is_game_over():
            if self.board.get_game_state() == GameState.WON:
                print("\n🎉🎉🎉 おめでとうございます！勝利しました！ 🎉🎉🎉")
                print(f"ターン数: {self.turn_count}")
            else:
                print("\n💀💀💀 残念...敗北しました 💀💀💀")
                print("地雷の位置:")
                print(self.board.display_board(show_mines=True))

    def start_game(self):
        """ゲームを開始"""
        print("🎮 マインスイーパーゲームへようこそ！")
        print(f"盤面サイズ: {self.board.height}x{self.board.width}")
        print(f"地雷数: {self.board.mine_count}")

        self.display_help()

        while True:
            self.display_game_status()

            # ゲーム終了チェック
            if self.board.is_game_over():
                play_again = input("\nもう一度プレイしますか？ (y/n): ").strip().lower()
                if play_again == 'y':
                    self.__init__(self.board.height, self.board.width, self.board.mine_count)
                    continue
                else:
                    print("ゲームを終了します。お疲れ様でした！")
                    break

            # ユーザー入力
            command_input = input("\nコマンドを入力してください: ").strip()

            if not command_input:
                continue

            parsed = self.parse_command(command_input)

            if parsed is None:
                print("❌ 無効なコマンドです。'h' でヘルプを表示できます。")
                continue

            action, row, col = parsed

            if action == 'help':
                self.display_help()
                continue
            elif action == 'quit':
                print("ゲームを終了します。お疲れ様でした！")
                break
            else:
                success = self.execute_command(action, row, col)
                if success:
                    self.turn_count += 1


def select_difficulty():
    """難易度選択"""
    print("=== マインスイーパー設定 ===\n")
    print("難易度を選択してください:")
    print("1. 初級 (9x9, 地雷10個)")
    print("2. 中級 (16x16, 地雷40個)")
    print("3. 上級 (24x20, 地雷99個)")
    print("4. カスタム")

    while True:
        try:
            choice = input("選択 (1-4): ").strip()

            if choice == '1':
                return 9, 9, 10
            elif choice == '2':
                return 16, 16, 40
            elif choice == '3':
                return 20, 24, 99
            elif choice == '4':
                print("\n=== カスタム設定 ===")
                height = int(input("高さ (5-50): "))
                width = int(input("幅 (5-50): "))
                max_mines = height * width - 1
                mine_count = int(input(f"地雷数 (1-{max_mines}): "))

                if not (5 <= height <= 50 and 5 <= width <= 50):
                    print("高さと幅は5-50の範囲で指定してください。")
                    continue
                if not (1 <= mine_count <= max_mines):
                    print(f"地雷数は1-{max_mines}の範囲で指定してください。")
                    continue

                return height, width, mine_count
            else:
                print("1-4の数字を入力してください。")
        except ValueError:
            print("数値を入力してください。")
        except KeyboardInterrupt:
            print("\nゲームを終了します。")
            sys.exit(0)


def main():
    """メイン関数"""
    try:
        height, width, mine_count = select_difficulty()
        game = MinesweeperGame(height, width, mine_count)
        game.start_game()
    except KeyboardInterrupt:
        print("\nゲームを終了します。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
