# 📚 Book Tracker Database

書籍管理システム - AudibleとKindleの本を効率的に管理するSQLiteデータベース

## 📊 データベース構造

### テーブル: `books`

| カラム | 型 | 説明 |
|--------|----|----|
| id | INTEGER | 主キー |
| title | TEXT | タイトル（必須） |
| author | TEXT | 著者 |
| source | TEXT | ソース（Audible / Kindle） |
| status | TEXT | ステータス（completed / in_progress / not_started / purchased） |
| remaining_time | TEXT | 残り時間（例: "10時間 5分"） |
| total_duration | TEXT | 全体時間 |
| purchase_date | DATE | 購入日 |
| purchase_order | INTEGER | 購入順序（Kindle用） |
| page_number | INTEGER | ページ番号（Audible用） |
| is_podcast | BOOLEAN | ポッドキャストフラグ |
| notes | TEXT | メモ |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

### ビュー

- `audible_completed` - Audible完了した本
- `audible_in_progress` - Audible進行中の本
- `audible_not_started` - Audible未聴取の本
- `kindle_all` - Kindle全ての本（購入順）
- `statistics` - 統計情報

---

## 🚀 セットアップ

### 1. データベース初期化とデータインポート

```bash
python3 import_data.py
```

これにより以下が実行されます：
- SQLiteデータベースの作成
- スキーマの適用
- 既存のMarkdownデータのインポート

---

## 💻 使い方

### CLIツール

`book_cli.py` を使って簡単にデータベースを操作できます。

#### 統計情報を表示

```bash
python3 book_cli.py stats
```

#### 全ての本をリスト表示

```bash
python3 book_cli.py list
```

#### Audibleの本のみ表示

```bash
python3 book_cli.py audible
```

#### Kindleの本のみ表示

```bash
python3 book_cli.py kindle
```

#### 進行中の本を表示

```bash
python3 book_cli.py in-progress
```

#### カテゴリ一覧を表示

```bash
python3 book_cli.py categories
```

#### 特定カテゴリの本を表示

```bash
python3 book_cli.py category "脳科学・神経科学"
python3 book_cli.py category "デザイン・UI/UX"
python3 book_cli.py category "ビジネス・経営"
```

#### 本を検索

```bash
# タイトルで検索
python3 book_cli.py search --title "脳"

# 著者で検索
python3 book_cli.py search --author "石川"

# ソースで絞り込み
python3 book_cli.py search --source Audible

# ステータスで絞り込み
python3 book_cli.py search --status in_progress

# カテゴリで絞り込み
python3 book_cli.py search --category "脳科学・神経科学"

# 複合検索
python3 book_cli.py search --source Audible --status completed --title "脳"

# カテゴリ + ソース + ステータスの複合検索
python3 book_cli.py search --category "デザイン・UI/UX" --source Kindle --status purchased
```

#### 本を追加（対話式）

```bash
python3 book_cli.py add
```

#### 本を更新

```bash
# ステータスを更新
python3 book_cli.py update 1 --status completed

# 残り時間を更新
python3 book_cli.py update 5 --remaining-time "5時間 30分"

# メモを追加
python3 book_cli.py update 10 --notes "とても面白い！"
```

#### 本を削除

```bash
python3 book_cli.py delete 123
```

#### Markdownにエクスポート

```bash
# デフォルトファイル名
python3 book_cli.py export

# カスタムファイル名
python3 book_cli.py export --output my_books.md
```

---

## 🐍 Pythonから直接使う

### 基本的な使い方

```python
from db_manager import BookDatabase

# データベースに接続
with BookDatabase() as db:
    # 統計情報を取得
    stats = db.get_statistics()
    for stat in stats:
        print(f"{stat['source']} - {stat['status']}: {stat['count']}冊")
    
    # Audible進行中の本を取得
    in_progress = db.get_audible_in_progress()
    for book in in_progress:
        print(f"{book['title']} (残り: {book['remaining_time']})")
    
    # 本を検索
    books = db.search_books(title_search="脳", source="Audible")
    for book in books:
        print(f"{book['title']} / {book['author']}")
    
    # 本を追加
    book_id = db.add_book(
        title="新しい本",
        author="著者名",
        source="Audible",
        status="not_started",
        page_number=1
    )
    
    # 本を更新
    db.update_book(book_id, status="in_progress", remaining_time="8時間 30分")
    
    # 本を削除
    db.delete_book(book_id)
```

### 高度な検索

```python
with BookDatabase() as db:
    # 複数条件で検索
    books = db.search_books(
        source="Audible",
        status="in_progress",
        author_search="石川",
        page_number=1,
        category="自己啓発・マインドフルネス"
    )
    
    # カスタムクエリ
    cursor = db.conn.execute("""
        SELECT title, author, remaining_time 
        FROM books 
        WHERE source = 'Audible' 
          AND status = 'in_progress'
          AND remaining_time LIKE '%時間%'
        ORDER BY title
    """)
    
    for row in cursor:
        print(dict(row))
```

---

## 📈 SQLで直接クエリ

```bash
sqlite3 book_tracker.db
```

### サンプルクエリ

```sql
-- 全ての本を表示
SELECT * FROM books;

-- Audible完了した本
SELECT * FROM audible_completed;

-- 進行中の本で残り時間が長い順
SELECT title, author, remaining_time 
FROM books 
WHERE status = 'in_progress' 
ORDER BY remaining_time DESC;

-- 著者別の本の数
SELECT author, COUNT(*) as count 
FROM books 
GROUP BY author 
ORDER BY count DESC;

-- ページ番号別の本の数（Audible）
SELECT page_number, COUNT(*) as count 
FROM books 
WHERE source = 'Audible' 
GROUP BY page_number 
ORDER BY page_number;

-- 統計情報
SELECT * FROM statistics;

-- カテゴリ別統計
SELECT * FROM categories_summary;

-- 特定カテゴリの本
SELECT title, author FROM books WHERE category = 'デザイン・UI/UX';

-- カテゴリ別の完了率
SELECT 
    category,
    total_books,
    completed,
    ROUND(completed * 100.0 / total_books, 1) as completion_rate
FROM categories_summary
WHERE total_books > 0
ORDER BY completion_rate DESC;
```

---

## 📝 データの管理

### バックアップ

```bash
# データベースファイルをコピー
cp book_tracker.db book_tracker_backup_$(date +%Y%m%d).db

# Markdownとしてエクスポート
python3 book_cli.py export --output backup_$(date +%Y%m%d).md
```

### リストア

```bash
# バックアップから復元
cp book_tracker_backup_20251213.db book_tracker.db
```

---

## 📁 ファイル構成

```
book-tracker/
├── 📊 データベース
│   └── book_tracker.db          (152冊、20カテゴリ)
│
├── 🐍 Pythonスクリプト
│   ├── db_manager.py            (データベース管理クラス)
│   ├── import_data.py           (データインポート)
│   ├── book_cli.py              (CLIツール)
│   └── categorize_books.py      (カテゴリ自動分類)
│
├── 📄 SQL
│   ├── schema.sql               (データベース定義)
│   └── add_categories.sql       (カテゴリ追加SQL)
│
├── 📚 ドキュメント
│   ├── README.md                (完全マニュアル)
│   ├── QUICKSTART.md            (クイックスタート)
│   └── CATEGORIES.md            (カテゴリ機能ガイド)
│
└── 💾 データ（元データ・エクスポート）
    ├── book-data.md             (元のMarkdownデータ)
    ├── audible-unfinished-complete.md
    └── database_export.md       (エクスポート例)
```

---

## 📊 現在のデータ統計

### ソース別

| ソース | ステータス | 冊数 |
|--------|-----------|------|
| Audible | 完了 | 7冊 |
| Audible | 進行中 | 34冊 |
| Audible | 未聴取 | 67冊 |
| Kindle | 購入済み | 44冊 |
| **合計** | | **152冊** |

### カテゴリ別（Top 10）

| カテゴリ | 冊数 |
|---------|------|
| デザイン・UI/UX | 19冊 |
| 生物学・進化 | 12冊 |
| 脳科学・神経科学 | 10冊 |
| 歴史・地政学 | 10冊 |
| 自己啓発・マインドフルネス | 9冊 |
| 語学・英語 | 9冊 |
| テクノロジー・未来 | 8冊 |
| ビジネス・経営 | 8冊 |
| 経済・金融 | 8冊 |
| 思考法・問題解決 | 6冊 |

**全20カテゴリ** - 詳細は `CATEGORIES.md` を参照

---

## 🎯 今後の拡張案

- [ ] Webインターフェース（Flask / FastAPI）
- [ ] 読書進捗グラフの可視化
- [ ] 自動同期機能（Audible/Kindle API）
- [ ] タグ・カテゴリー機能
- [ ] 読書時間トラッキング
- [ ] レビュー・評価機能
- [ ] 読書目標設定機能

---

## 📄 ライセンス

MIT License

---

## 👤 作成者

書籍管理データベース v1.0

