-- カテゴリフィールドとタグ機能を追加

-- 1. カテゴリカラムを追加
ALTER TABLE books ADD COLUMN category TEXT;
ALTER TABLE books ADD COLUMN tags TEXT; -- カンマ区切りのタグ

-- 2. カテゴリ用のインデックスを作成
CREATE INDEX IF NOT EXISTS idx_category ON books(category);

-- 3. カテゴリ別統計ビュー
CREATE VIEW IF NOT EXISTS category_statistics AS
SELECT 
    category,
    source,
    COUNT(*) as count
FROM books
WHERE category IS NOT NULL
GROUP BY category, source
ORDER BY category, source;

-- 4. カテゴリ一覧ビュー
CREATE VIEW IF NOT EXISTS categories_summary AS
SELECT 
    category,
    COUNT(*) as total_books,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
    SUM(CASE WHEN status = 'not_started' THEN 1 ELSE 0 END) as not_started,
    SUM(CASE WHEN status = 'purchased' THEN 1 ELSE 0 END) as purchased
FROM books
WHERE category IS NOT NULL
GROUP BY category
ORDER BY total_books DESC;

