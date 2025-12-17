-- Book Tracker Database Schema

CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    source TEXT NOT NULL CHECK(source IN ('Audible', 'Kindle')),
    status TEXT NOT NULL CHECK(status IN ('completed', 'in_progress', 'not_started', 'purchased')),
    remaining_time TEXT,  -- Format: "10時間 5分" or "2分"
    total_duration TEXT,  -- Format: "10時間 5分" or "2分"
    purchase_date DATE,   -- For Kindle books
    purchase_order INTEGER, -- For Kindle books (順序)
    page_number INTEGER,  -- Audibleのページ番号
    is_podcast BOOLEAN DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_source ON books(source);
CREATE INDEX IF NOT EXISTS idx_status ON books(status);
CREATE INDEX IF NOT EXISTS idx_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_author ON books(author);
CREATE INDEX IF NOT EXISTS idx_purchase_order ON books(purchase_order);

-- Trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_books_timestamp 
AFTER UPDATE ON books
BEGIN
    UPDATE books SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- View: Audible完了した本
CREATE VIEW IF NOT EXISTS audible_completed AS
SELECT id, title, author, created_at, updated_at
FROM books
WHERE source = 'Audible' AND status = 'completed'
ORDER BY title;

-- View: Audible進行中の本
CREATE VIEW IF NOT EXISTS audible_in_progress AS
SELECT id, title, author, remaining_time, total_duration, page_number
FROM books
WHERE source = 'Audible' AND status = 'in_progress'
ORDER BY page_number, title;

-- View: Audible未聴取の本
CREATE VIEW IF NOT EXISTS audible_not_started AS
SELECT id, title, author, total_duration, page_number
FROM books
WHERE source = 'Audible' AND status = 'not_started'
ORDER BY page_number, title;

-- View: Kindle全ての本（購入順）
CREATE VIEW IF NOT EXISTS kindle_all AS
SELECT id, title, author, purchase_order, purchase_date
FROM books
WHERE source = 'Kindle'
ORDER BY purchase_order;

-- View: 統計情報
CREATE VIEW IF NOT EXISTS statistics AS
SELECT 
    source,
    status,
    COUNT(*) as count
FROM books
GROUP BY source, status
ORDER BY source, status;

