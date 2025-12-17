# 📚 クイックスタートガイド

## 🚀 5分で始める書籍データベース

### ステップ1: データベースの確認

データベースはすでに作成済みです！

```bash
ls -lh book_tracker.db
```

### ステップ2: 統計を確認

```bash
python3 book_cli.py stats
```

**出力例:**
```
============================================================
📊 書籍データベース統計
============================================================

ソース             ステータス                   冊数
---------------------------------------------
Audible         完了                       7冊
Audible         進行中                     34冊
Audible         未聴取                     67冊
Kindle          購入済み                    44冊
---------------------------------------------
合計                                    152冊
```

---

## 💡 よく使うコマンド

### 📖 読書中の本を確認

```bash
python3 book_cli.py in-progress
```

これで今読んでいる本と残り時間が一覧できます！

### 🔍 本を探す

```bash
# タイトルで検索
python3 book_cli.py search --title "脳"

# 著者で検索
python3 book_cli.py search --author "石川"

# Audibleの進行中の本だけ
python3 book_cli.py search --source Audible --status in_progress
```

### 📝 進捗を更新

本を読み終わったら：

```bash
python3 book_cli.py update 8 --status completed
```

残り時間を更新：

```bash
python3 book_cli.py update 8 --remaining-time "3時間 20分"
```

### ➕ 新しい本を追加

```bash
python3 book_cli.py add
```

対話式で簡単に追加できます！

---

## 🎯 実用例

### 📚 シナリオ1: 今日読む本を決める

```bash
# 進行中で残り時間が短い本を探す
python3 book_cli.py in-progress
```

→ 残り時間を見て、今日読む本を決める！

### 📊 シナリオ2: 読書の進捗をチェック

```bash
# 統計を確認
python3 book_cli.py stats

# Audibleで完了した本を確認
python3 book_cli.py audible
```

→ 「完了した本」が増えていくのを実感！

### 🔍 シナリオ3: 積読本を確認

```bash
# Audible未聴取の本
python3 book_cli.py search --source Audible --status not_started

# Kindle未読の本（全て購入済み）
python3 book_cli.py kindle
```

→ 積読本リストを眺めて、次に読む本を選ぶ！

### 📈 シナリオ4: 特定のテーマの本を探す

```bash
# 「脳」に関する本を全て表示
python3 book_cli.py search --title "脳"

# 「デザイン」に関するKindle本
python3 book_cli.py search --title "デザイン" --source Kindle

# 池上彰さんの本
python3 book_cli.py search --author "池上"
```

### 💾 シナリオ5: バックアップを作る

```bash
# Markdownにエクスポート
python3 book_cli.py export --output backup_$(date +%Y%m%d).md

# データベースファイルをコピー
cp book_tracker.db book_tracker_backup.db
```

---

## 🐍 Pythonで直接使う

簡単なスクリプトを作ってみましょう：

```python
# my_reading_stats.py
from db_manager import BookDatabase

with BookDatabase() as db:
    # 進行中の本の数
    in_progress = db.search_books(status='in_progress')
    print(f"📗 今読んでいる本: {len(in_progress)}冊")
    
    # 完了した本の数
    completed = db.search_books(status='completed')
    print(f"✅ 読み終わった本: {len(completed)}冊")
    
    # 未読の本の数
    not_started = db.search_books(status='not_started')
    print(f"📚 これから読む本: {len(not_started)}冊")
```

実行：

```bash
python3 my_reading_stats.py
```

---

## 🎨 さらに便利に使う

### エイリアスを設定（オプション）

`.zshrc` または `.bashrc` に追加：

```bash
# Book Tracker エイリアス
alias books='cd ~/Documents/book-tracker && python3 book_cli.py'
alias books-stats='cd ~/Documents/book-tracker && python3 book_cli.py stats'
alias books-reading='cd ~/Documents/book-tracker && python3 book_cli.py in-progress'
alias books-search='cd ~/Documents/book-tracker && python3 book_cli.py search'
```

これで簡単に：

```bash
books stats
books-reading
books-search --title "脳"
```

---

## 📱 次のステップ

1. **定期的に進捗を更新**
   - 本を読み終わったら `update` コマンドでステータスを更新
   - 残り時間も更新して進捗を可視化

2. **検索を活用**
   - 気分に合わせて読む本を探す
   - 特定のテーマの本をまとめてチェック

3. **統計を楽しむ**
   - 定期的に `stats` コマンドで読書の進捗を確認
   - 完了した本が増えていくのを楽しむ！

4. **カスタマイズ**
   - Pythonスクリプトで自分だけの分析ツールを作る
   - SQLで高度なクエリを書いてみる

---

## 🆘 困ったときは

### データベースを最初から作り直したい

```bash
# 既存のデータベースを削除
rm book_tracker.db

# 再インポート
python3 import_data.py
```

### コマンドのヘルプを見たい

```bash
python3 book_cli.py --help
python3 book_cli.py search --help
```

### Pythonのドキュメントを見たい

```python
from db_manager import BookDatabase
help(BookDatabase)
```

---

**Happy Reading! 📚✨**

