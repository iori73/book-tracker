import Database from 'better-sqlite3';
import path from 'path';

// データベースのパス（親ディレクトリのbook_tracker.dbを参照）
const DB_PATH = path.join(process.cwd(), '..', 'book_tracker.db');

export interface Book {
  id: number;
  title: string;
  author: string | null;
  source: 'Audible' | 'Kindle';
  status: 'completed' | 'in_progress' | 'not_started' | 'purchased';
  remaining_time: string | null;
  total_duration: string | null;
  purchase_date: string | null;
  purchase_order: number | null;
  page_number: number | null;
  is_podcast: number;
  notes: string | null;
  category: string | null;
  tags: string | null;
  created_at: string;
  updated_at: string;
}

export interface Statistics {
  source: string;
  status: string;
  count: number;
}

export interface CategorySummary {
  category: string;
  total_books: number;
  completed: number;
  in_progress: number;
  not_started: number;
  purchased: number;
}

export function getDatabase() {
  const db = new Database(DB_PATH, { readonly: false });
  return db;
}

export function getAllBooks(): Book[] {
  const db = getDatabase();
  const books = db.prepare('SELECT * FROM books ORDER BY source, status, title').all() as Book[];
  db.close();
  return books;
}

export function searchBooks(params: {
  source?: string;
  status?: string;
  title?: string;
  author?: string;
  category?: string;
}): Book[] {
  const db = getDatabase();
  
  let query = 'SELECT * FROM books WHERE 1=1';
  const values: any[] = [];
  
  if (params.source) {
    query += ' AND source = ?';
    values.push(params.source);
  }
  
  if (params.status) {
    query += ' AND status = ?';
    values.push(params.status);
  }
  
  if (params.title) {
    query += ' AND title LIKE ?';
    values.push(`%${params.title}%`);
  }
  
  if (params.author) {
    query += ' AND author LIKE ?';
    values.push(`%${params.author}%`);
  }
  
  if (params.category) {
    query += ' AND category = ?';
    values.push(params.category);
  }
  
  query += ' ORDER BY source, status, title';
  
  const books = db.prepare(query).all(...values) as Book[];
  db.close();
  return books;
}

export function getStatistics(): Statistics[] {
  const db = getDatabase();
  const stats = db.prepare(`
    SELECT source, status, COUNT(*) as count
    FROM books
    GROUP BY source, status
    ORDER BY source, status
  `).all() as Statistics[];
  db.close();
  return stats;
}

export function getCategorySummary(): CategorySummary[] {
  const db = getDatabase();
  const categories = db.prepare(`
    SELECT * FROM categories_summary
    ORDER BY total_books DESC
  `).all() as CategorySummary[];
  db.close();
  return categories;
}

export function getCategories(): string[] {
  const db = getDatabase();
  const categories = db.prepare(`
    SELECT DISTINCT category
    FROM books
    WHERE category IS NOT NULL
    ORDER BY category
  `).all() as Array<{ category: string }>;
  db.close();
  return categories.map(c => c.category);
}

export function updateBook(id: number, updates: Partial<Book>): void {
  const db = getDatabase();
  
  const fields: string[] = [];
  const values: any[] = [];
  
  if (updates.status !== undefined) {
    fields.push('status = ?');
    values.push(updates.status);
  }
  
  if (updates.remaining_time !== undefined) {
    fields.push('remaining_time = ?');
    values.push(updates.remaining_time);
  }
  
  if (updates.notes !== undefined) {
    fields.push('notes = ?');
    values.push(updates.notes);
  }
  
  if (fields.length > 0) {
    values.push(id);
    const query = `UPDATE books SET ${fields.join(', ')}, updated_at = CURRENT_TIMESTAMP WHERE id = ?`;
    db.prepare(query).run(...values);
  }
  
  db.close();
}

export function getBook(id: number): Book | null {
  const db = getDatabase();
  const book = db.prepare('SELECT * FROM books WHERE id = ?').get(id) as Book | undefined;
  db.close();
  return book || null;
}

