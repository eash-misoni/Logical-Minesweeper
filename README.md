# Logical Minesweeper

マインスイーパーゲーム（CLI版とWeb版）+ 論理ソルバーシステム

## 機能

- **CLI版**: コマンドラインでプレイ可能
- **Web版**: ブラウザでプレイ可能（予定）
- **論理ソルバー**: 100%論理的に解けるマスを自動検出
- 初級・中級・上級・カスタム難易度対応
- ユーザーフレンドリーなメッセージ機能
- 拡張可能なソルバーアーキテクチャ

## プロジェクト構成

```
Logical Minesweeper/
├── backend/                # バックエンド（Python）
│   ├── minesweeper.py     # コアロジック
│   ├── game_manager.py    # CLIゲームマネージャー
│   ├── api.py            # Web API（予定）
│   ├── test_messages.py   # テストファイル
│   └── solver/           # ソルバーシステム
│       ├── solver_base.py        # ソルバー基底クラス
│       ├── logical_solver.py     # 論理ソルバー実装
│       ├── solver_manager.py     # ソルバー統合管理
│       ├── solver_board_view.py  # チート防止盤面ビュー
│       ├── solver_command.py     # 汎用コマンドIF
│       ├── solver_move.py        # 内部データ構造
│       └── test_solver.py        # ソルバーテスト
├── frontend/              # フロントエンド（HTML/CSS/JS）
│   ├── index.html        # メインページ（予定）
│   ├── style.css         # スタイルシート（予定）
│   └── script.js         # JavaScript（予定）
└── README.md             # このファイル
```

## 使用方法

### CLI版
```bash
cd backend
python game_manager.py
```

### Web版
```bash
# 予定
python backend/api.py
```

### ソルバーシステム
```python
from backend.solver.solver_manager import SolverManager
from backend.minesweeper import MinesweeperBoard

# ゲーム盤面を作成
board = MinesweeperBoard(9, 9, 10)  # 初級レベル

# ソルバーマネージャーを初期化
manager = SolverManager()

# 論理的に解ける手を自動実行
commands = manager.solve_with_commands_until_manual_needed(board)
print(f"自動で{len(commands)}手実行しました")
```

## ソルバーアーキテクチャ

### 設計思想
- **チート防止**: ソルバーは地雷位置にアクセス不可
- **拡張性**: 新しいソルバー（確率的・AI等）を簡単に追加可能
- **分離**: 内部実装と外部インターフェースを明確に分離

### 主要コンポーネント

- **SolverBase**: 全ソルバーの抽象基底クラス
- **LogicalSolver**: 100%論理的確定のみを検出
- **SolverBoardView**: 安全な盤面ビュー（地雷位置非表示）
- **SolverManager**: ソルバーとゲームの統合管理
- **SolverCommand/SolverMove**: 汎用・内部データ構造

## 技術仕様

### 環境
- Python 3.12+
- FastAPI（Web API用、予定）
- HTML/CSS/JavaScript（フロントエンド、予定）

### ソルバーの特徴
- **論理的確定性**: 推測なしで100%確実な手のみ実行
- **エラー処理**: 無限ループ防止・例外ハンドリング完備
- **型安全**: 型ヒント・データクラス活用
- **テスト可能**: モジュール分離による単体テスト対応

### 拡張予定
- 確率計算ソルバー
- 機械学習ベースソルバー
- パフォーマンス最適化
- Web UI統合

## 開発履歴

### ゲームシステム
- ✅ マインスイーパー盤面クラス実装
- ✅ CLIゲームマネージャー実装
- ✅ ユーザーフレンドリーメッセージ機能実装

### ソルバーシステム（WIP）
- ✅ ソルバー基底クラス（SolverBase）実装
- ✅ 論理ソルバー（LogicalSolver）基本実装
- ✅ チート防止盤面ビュー（SolverBoardView）実装
- ✅ 汎用コマンドインターフェース実装
- ✅ ソルバー統合管理システム実装
- 🚧 論理解法アルゴリズム詳細実装
- 🚧 確率的ソルバー実装予定

### Webシステム
- 🚧 Web API実装予定
- 🚧 フロントエンド実装予定

