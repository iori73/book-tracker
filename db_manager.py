#!/usr/bin/env python3
"""
Book Tracker Database Manager

このスクリプトは書籍データベースを管理するための機能を提供します。
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), "book_tracker.db")


class BookDatabase:
    """書籍データベース管理クラス"""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def initialize_database(self):
        """データベースを初期化"""
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        
        self.conn.executescript(schema)
        self.conn.commit()
        print(f"✅ データベースを初期化しました: {self.db_path}")

    def add_book(
        self,
        title: str,
        author: str,
        source: str,
        status: str,
        remaining_time: Optional[str] = None,
        total_duration: Optional[str] = None,
        purchase_date: Optional[str] = None,
        purchase_order: Optional[int] = None,
        page_number: Optional[int] = None,
        is_podcast: bool = False,
        notes: Optional[str] = None
    ) -> int:
        """本を追加"""
        cursor = self.conn.execute(
            """
            INSERT INTO books (
                title, author, source, status, remaining_time, total_duration,
                purchase_date, purchase_order, page_number, is_podcast, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (title, author, source, status, remaining_time, total_duration,
             purchase_date, purchase_order, page_number, is_podcast, notes)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_book(
        self,
        book_id: int,
        **kwargs
    ):
        """本の情報を更新"""
        allowed_fields = [
            'title', 'author', 'source', 'status', 'remaining_time',
            'total_duration', 'purchase_date', 'purchase_order',
            'page_number', 'is_podcast', 'notes'
        ]
        
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return
        
        values.append(book_id)
        query = f"UPDATE books SET {', '.join(fields)} WHERE id = ?"
        
        self.conn.execute(query, values)
        self.conn.commit()
        print(f"✅ 本を更新しました (ID: {book_id})")

    def delete_book(self, book_id: int):
        """本を削除"""
        self.conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        self.conn.commit()
        print(f"✅ 本を削除しました (ID: {book_id})")

    def get_book(self, book_id: int) -> Optional[Dict]:
        """IDで本を取得"""
        cursor = self.conn.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def search_books(
        self,
        source: Optional[str] = None,
        status: Optional[str] = None,
        title_search: Optional[str] = None,
        author_search: Optional[str] = None,
        page_number: Optional[int] = None,
        category: Optional[str] = None
    ) -> List[Dict]:
        """本を検索"""
        query = "SELECT * FROM books WHERE 1=1"
        params = []

        if source:
            query += " AND source = ?"
            params.append(source)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if title_search:
            query += " AND title LIKE ?"
            params.append(f"%{title_search}%")
        
        if author_search:
            query += " AND author LIKE ?"
            params.append(f"%{author_search}%")
        
        if page_number is not None:
            query += " AND page_number = ?"
            params.append(page_number)
        
        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY source, status, title"

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_audible_completed(self) -> List[Dict]:
        """Audible完了した本を取得"""
        cursor = self.conn.execute("SELECT * FROM audible_completed")
        return [dict(row) for row in cursor.fetchall()]

    def get_audible_in_progress(self) -> List[Dict]:
        """Audible進行中の本を取得"""
        cursor = self.conn.execute("SELECT * FROM audible_in_progress")
        return [dict(row) for row in cursor.fetchall()]

    def get_audible_not_started(self) -> List[Dict]:
        """Audible未聴取の本を取得"""
        cursor = self.conn.execute("SELECT * FROM audible_not_started")
        return [dict(row) for row in cursor.fetchall()]

    def get_kindle_all(self) -> List[Dict]:
        """Kindle全ての本を取得（購入順）"""
        cursor = self.conn.execute("SELECT * FROM kindle_all")
        return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> List[Dict]:
        """統計情報を取得"""
        cursor = self.conn.execute("SELECT * FROM statistics")
        return [dict(row) for row in cursor.fetchall()]

    def export_to_markdown(self, output_path: str):
        """データベースの内容をMarkdownにエクスポート"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 読書トラッカーデータ（データベースエクスポート）\n\n")
            f.write(f"エクスポート日: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n")
            
            # 統計
            f.write("## 📊 統計情報\n\n")
            stats = self.get_statistics()
            f.write("| ソース | ステータス | 冊数 |\n")
            f.write("|--------|-----------|------|\n")
            for stat in stats:
                f.write(f"| {stat['source']} | {stat['status']} | {stat['count']}冊 |\n")
            f.write("\n---\n\n")
            
            # Audible完了
            f.write("## Audible - 完了した本\n\n")
            completed = self.get_audible_completed()
            f.write("| # | タイトル | 著者 |\n")
            f.write("|---|---------|------|\n")
            for i, book in enumerate(completed, 1):
                f.write(f"| {i} | {book['title']} | {book['author']} |\n")
            f.write("\n---\n\n")
            
            # Audible進行中
            f.write("## Audible - 進行中の本\n\n")
            in_progress = self.get_audible_in_progress()
            f.write("| # | タイトル | 著者 | 残り時間 | ページ |\n")
            f.write("|---|---------|------|----------|--------|\n")
            for i, book in enumerate(in_progress, 1):
                remaining = book['remaining_time'] or 'N/A'
                page = book['page_number'] or '-'
                f.write(f"| {i} | {book['title']} | {book['author']} | {remaining} | {page} |\n")
            f.write("\n---\n\n")
            
            # Audible未聴取
            f.write("## Audible - 未聴取の本\n\n")
            not_started = self.get_audible_not_started()
            f.write("| # | タイトル | 著者 | ページ |\n")
            f.write("|---|---------|------|--------|\n")
            for i, book in enumerate(not_started, 1):
                page = book['page_number'] or '-'
                f.write(f"| {i} | {book['title']} | {book['author']} | {page} |\n")
            f.write("\n---\n\n")
            
            # Kindle
            f.write("## Kindle - 全ての本（購入順）\n\n")
            kindle = self.get_kindle_all()
            f.write("| # | タイトル | 著者 |\n")
            f.write("|---|---------|------|\n")
            for book in kindle:
                order = book['purchase_order']
                f.write(f"| {order} | {book['title']} | {book['author']} |\n")
            
        print(f"✅ Markdownにエクスポートしました: {output_path}")


def main():
    """メイン関数（初期化とテスト）"""
    with BookDatabase() as db:
        db.initialize_database()
        
        # 統計を表示
        print("\n📊 データベース統計:")
        stats = db.get_statistics()
        if stats:
            for stat in stats:
                print(f"  {stat['source']} - {stat['status']}: {stat['count']}冊")
        else:
            print("  まだデータがありません")


if __name__ == "__main__":
    main()

