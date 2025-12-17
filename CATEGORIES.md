# 📂 カテゴリ機能ガイド

書籍データベースに自動カテゴリ分類機能が追加されました！

## 🎯 カテゴリ一覧

全152冊の書籍が以下の20カテゴリに自動分類されています：

### 📚 主要カテゴリ

1. **デザイン・UI/UX** (19冊)
   - UIデザイン、UXリサーチ、インターフェース設計
   - 例: 『UIデザインの教科書』『なるほどデザイン』

2. **脳科学・神経科学** (10冊)
   - 脳、意識、認知科学、心理学
   - 例: 『進化しすぎた脳』『脳はどこまでコントロールできるか?』

3. **生物学・進化** (12冊)
   - 進化論、生命科学、生態系
   - 例: 『Why Fish Don't Exist』『The Mind of a Bee』

4. **歴史・地政学** (10冊)
   - 世界史、日本史、政治、外交
   - 例: 『世界史とつなげて学べ 超日本史』『１３歳からの地政学』

5. **ビジネス・経営** (8冊)
   - マネジメント、戦略、組織論
   - 例: 『プロダクトマネジメントのすべて』『コンサル一年目が学ぶこと』

6. **テクノロジー・未来** (8冊)
   - AI、Web3、未来予測
   - 例: 『AI 2041』『人工知能は人間を超えるか』

7. **経済・金融** (8冊)
   - 経済学、投資、金融
   - 例: 『会計クイズを解くだけで財務３表がわかる』

8. **自己啓発・マインドフルネス** (9冊)
   - 習慣、生産性、マインドフルネス
   - 例: 『ジェームズ・クリアー式 複利で伸びる１つの習慣』

9. **語学・英語** (9冊)
   - 英語学習、英会話
   - 例: 『起きてから寝るまで英語表現1000』

10. **思考法・問題解決** (6冊)
    - 論理的思考、問題解決、メタ思考
    - 例: 『イシューからはじめよ』『メタ思考トレーニング』

### 📖 その他のカテゴリ

- **健康・運動・栄養** (5冊)
- **教養・一般** (5冊)
- **文学・エッセイ** (4冊)
- **技術・プログラミング** (3冊)
- **社会・人類学** (3冊)
- **科学一般** (3冊)
- **データ・可視化** (2冊)
- **哲学・思想** (2冊)
- **環境・エネルギー** (2冊)
- **その他** (24冊)

---

## 🔍 使い方

### 1. カテゴリ一覧を表示

```bash
python3 book_cli.py categories
```

各カテゴリの統計情報が表示されます：
- 合計冊数
- 完了した本
- 進行中の本
- 未読の本
- 購入済みの本（Kindle）

### 2. 特定カテゴリの本を表示

```bash
# 脳科学の本を全て表示
python3 book_cli.py category "脳科学・神経科学"

# デザインの本を全て表示
python3 book_cli.py category "デザイン・UI/UX"

# 経済の本を全て表示
python3 book_cli.py category "経済・金融"
```

### 3. カテゴリで絞り込み検索

```bash
# Kindleで購入したデザイン本
python3 book_cli.py search --category "デザイン・UI/UX" --source Kindle

# 進行中の歴史本
python3 book_cli.py search --category "歴史・地政学" --status in_progress

# 未読の生物学本
python3 book_cli.py search --category "生物学・進化" --status not_started
```

### 4. 複合検索

```bash
# 池上彰さんの歴史本
python3 book_cli.py search --author "池上" --category "歴史・地政学"

# タイトルに「脳」を含む脳科学本
python3 book_cli.py search --title "脳" --category "脳科学・神経科学"

# Audibleで完了した自己啓発本
python3 book_cli.py search --category "自己啓発・マインドフルネス" \
                           --source Audible \
                           --status completed
```

---

## 🐍 Pythonから使う

```python
from db_manager import BookDatabase

with BookDatabase() as db:
    # カテゴリで検索
    design_books = db.search_books(category="デザイン・UI/UX")
    
    # カテゴリ統計を取得
    cursor = db.conn.execute("""
        SELECT * FROM categories_summary
        ORDER BY total_books DESC
    """)
    
    for row in cursor:
        print(f"{row['category']}: {row['total_books']}冊")
    
    # 特定カテゴリの進行中の本
    brain_in_progress = db.search_books(
        category="脳科学・神経科学",
        status="in_progress"
    )
```

---

## 📊 SQLで直接クエリ

```sql
-- カテゴリ別統計
SELECT * FROM categories_summary;

-- 最も本が多いカテゴリTop5
SELECT category, total_books 
FROM categories_summary 
ORDER BY total_books DESC 
LIMIT 5;

-- 特定カテゴリの本を全て取得
SELECT title, author, status 
FROM books 
WHERE category = 'デザイン・UI/UX'
ORDER BY title;

-- カテゴリ別の完了率
SELECT 
    category,
    total_books,
    completed,
    ROUND(completed * 100.0 / total_books, 1) as completion_rate
FROM categories_summary
WHERE total_books > 0
ORDER BY completion_rate DESC;

-- タグで検索（複数カテゴリに関連する本）
SELECT title, category, tags 
FROM books 
WHERE tags IS NOT NULL
ORDER BY category;
```

---

## 🎨 カテゴリの仕組み

### 自動分類アルゴリズム

1. **キーワードマッチング**
   - タイトルと著者名からキーワードを抽出
   - 各カテゴリの定義キーワードとマッチング

2. **スコアリング**
   - マッチしたキーワード数でスコアを計算
   - 最もスコアが高いカテゴリをメインカテゴリに

3. **タグ付与**
   - 2番目〜4番目にスコアが高いカテゴリをタグとして追加
   - 複数のテーマにまたがる本を適切に分類

### カテゴリの再分類

カテゴリを再計算したい場合：

```bash
python3 categorize_books.py
```

---

## 📈 カテゴリ別の読書状況

### 完了率が高いカテゴリ

- **脳科学・神経科学**: 20% (2/10冊完了)
- **自己啓発・マインドフルネス**: 11% (1/9冊完了)

### 進行中の本が多いカテゴリ

- **語学・英語**: 6冊進行中
- **歴史・地政学**: 4冊進行中

### 積読が多いカテゴリ

- **デザイン・UI/UX**: 19冊のうち16冊がKindle購入済み
- **その他**: 24冊のうち17冊が未読

---

## 💡 活用例

### 📚 テーマ別読書計画

```bash
# 今月は脳科学を集中的に読む
python3 book_cli.py category "脳科学・神経科学"

# 次はデザイン系の本を
python3 book_cli.py search --category "デザイン・UI/UX" --status not_started
```

### 📊 分野別の進捗確認

```bash
# カテゴリ統計を見て、偏りをチェック
python3 book_cli.py categories

# 読書バランスを調整
```

### 🎯 目標設定

```bash
# 「生物学・進化」カテゴリの未読本10冊を今年中に読破
python3 book_cli.py search --category "生物学・進化" --status not_started

# 進捗を確認しながら読み進める
```

---

## 🔧 カスタマイズ

### カテゴリ定義の変更

`categorize_books.py`の`CATEGORIES`辞書を編集して、独自のカテゴリを追加・変更できます：

```python
CATEGORIES = {
    "あなたのカテゴリ": [
        "キーワード1", "キーワード2", ...
    ],
    # ... 他のカテゴリ
}
```

### 手動でカテゴリを変更

```bash
# 本のカテゴリを手動で変更
python3 book_cli.py update 123 --notes "カテゴリ: 自己啓発"
```

または直接SQLで：

```sql
UPDATE books 
SET category = '自己啓発・マインドフルネス' 
WHERE id = 123;
```

---

**カテゴリ機能で、より効率的な読書管理を！📚✨**

