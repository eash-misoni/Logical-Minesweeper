# Logical Minesweeper

マインスイーパーゲーム（CLI版とWeb版）

## 機能

- **CLI版**: コマンドラインでプレイ可能
- **Web版**: ブラウザでプレイ可能（予定）
- 初級・中級・上級・カスタム難易度対応
- ユーザーフレンドリーなメッセージ機能

## プロジェクト構成

```
Logical Minesweeper/
├── backend/                # バックエンド（Python）
│   ├── minesweeper.py     # コアロジック
│   ├── game_manager.py    # CLIゲームマネージャー
│   ├── test_messages.py   # テストファイル
│   └── api.py            # Web API（予定）
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

## 開発履歴

- ✅ マインスイーパー盤面クラス実装
- ✅ CLIゲームマネージャー実装
- ✅ ユーザーフレンドリーメッセージ機能実装
- 🚧 Web API実装予定
- 🚧 フロントエンド実装予定

