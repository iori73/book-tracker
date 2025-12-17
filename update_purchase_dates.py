#!/usr/bin/env python3
"""
購入日を一括更新するスクリプト

使用方法:
1. CSVファイルからインポート:
   python update_purchase_dates.py --csv purchase_dates.csv

2. JSONファイルからインポート:
   python update_purchase_dates.py --json purchase_dates.json

3. インタラクティブモード:
   python update_purchase_dates.py --interactive

CSV形式:
title,author,purchase_date
本のタイトル,著者名,2021-01-15

JSON形式:
[
  {"title": "本のタイトル", "author": "著者名", "purchase_date": "2021-01-15"},
  {"id": 1, "purchase_date": "2021-01-15"}
]
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from typing import List, Dict, Optional
from db_manager import BookDatabase


def validate_date(date_str: str) -> bool:
    """日付形式を検証"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def update_from_csv(csv_path: str, dry_run: bool = False):
    """CSVファイルから購入日を更新"""
    updated_count = 0
    not_found = []
    
    with BookDatabase() as db:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                title = row.get('title', '').strip()
                author = row.get('author', '').strip()
                purchase_date = row.get('purchase_date', '').strip()
                
                if not purchase_date:
                    continue
                
                if not validate_date(purchase_date):
                    print(f"⚠️  無効な日付形式: {purchase_date} (タイトル: {title})")
                    continue
                
                # タイトルと著者で検索
                books = db.search_books(title_search=title, author_search=author)
                
                if not books:
                    not_found.append({'title': title, 'author': author, 'purchase_date': purchase_date})
                    continue
                
                # 複数見つかった場合は最初の1つを更新
                book = books[0]
                if len(books) > 1:
                    print(f"⚠️  複数の本が見つかりました。最初の1つを更新します: {book['title']}")
                
                if not dry_run:
                    db.update_book(book['id'], purchase_date=purchase_date)
                    print(f"✅ 更新: {book['title']} (ID: {book['id']}) → {purchase_date}")
                else:
                    print(f"[DRY RUN] 更新予定: {book['title']} (ID: {book['id']}) → {purchase_date}")
                
                updated_count += 1
    
    print(f"\n📊 更新完了: {updated_count}冊")
    if not_found:
        print(f"\n⚠️  見つからなかった本: {len(not_found)}冊")
        for item in not_found:
            print(f"  - {item['title']} / {item['author']}")


def update_from_json(json_path: str, dry_run: bool = False):
    """JSONファイルから購入日を更新"""
    updated_count = 0
    not_found = []
    
    with BookDatabase() as db:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for item in data:
            purchase_date = item.get('purchase_date', '').strip()
            
            if not purchase_date:
                continue
            
            if not validate_date(purchase_date):
                print(f"⚠️  無効な日付形式: {purchase_date}")
                continue
            
            book = None
            
            # IDで検索
            if 'id' in item:
                book = db.get_book(item['id'])
            
            # タイトルと著者で検索
            if not book:
                title = item.get('title', '').strip()
                author = item.get('author', '').strip()
                if title or author:
                    books = db.search_books(title_search=title, author_search=author)
                    if books:
                        book = books[0]
            
            if not book:
                not_found.append(item)
                continue
            
            if not dry_run:
                db.update_book(book['id'], purchase_date=purchase_date)
                print(f"✅ 更新: {book['title']} (ID: {book['id']}) → {purchase_date}")
            else:
                print(f"[DRY RUN] 更新予定: {book['title']} (ID: {book['id']}) → {purchase_date}")
            
            updated_count += 1
    
    print(f"\n📊 更新完了: {updated_count}冊")
    if not_found:
        print(f"\n⚠️  見つからなかった本: {len(not_found)}冊")
        for item in not_found:
            print(f"  - {item}")


def interactive_mode():
    """インタラクティブモードで購入日を更新"""
    with BookDatabase() as db:
        # 購入日が設定されていない本を表示
        all_books = db.search_books()
        books_without_date = [b for b in all_books if not b.get('purchase_date')]
        
        if not books_without_date:
            print("✅ すべての本に購入日が設定されています")
            return
        
        print(f"\n📚 購入日が設定されていない本: {len(books_without_date)}冊\n")
        
        for i, book in enumerate(books_without_date[:20], 1):  # 最初の20冊を表示
            print(f"{i}. ID: {book['id']} | {book['title']} / {book['author']}")
        
        if len(books_without_date) > 20:
            print(f"\n... 他 {len(books_without_date) - 20}冊")
        
        print("\n購入日を更新する本のIDを入力してください（複数の場合はカンマ区切り）:")
        print("例: 1,2,3 または 'all' ですべて更新")
        
        user_input = input("> ").strip()
        
        if user_input.lower() == 'all':
            book_ids = [b['id'] for b in books_without_date]
        else:
            try:
                book_ids = [int(x.strip()) for x in user_input.split(',')]
            except ValueError:
                print("❌ 無効な入力です")
                return
        
        for book_id in book_ids:
            book = db.get_book(book_id)
            if not book:
                print(f"❌ ID {book_id} の本が見つかりません")
                continue
            
            print(f"\n📖 {book['title']} / {book['author']}")
            print(f"現在の購入日: {book.get('purchase_date') or '未設定'}")
            
            date_input = input("購入日を入力 (YYYY-MM-DD形式、スキップする場合はEnter): ").strip()
            
            if not date_input:
                print("スキップしました")
                continue
            
            if not validate_date(date_input):
                print("❌ 無効な日付形式です。YYYY-MM-DD形式で入力してください")
                continue
            
            db.update_book(book_id, purchase_date=date_input)
            print(f"✅ 購入日を更新しました: {date_input}")


def show_books_without_date():
    """購入日が設定されていない本を表示"""
    with BookDatabase() as db:
        all_books = db.search_books()
        books_without_date = [b for b in all_books if not b.get('purchase_date')]
        
        if not books_without_date:
            print("✅ すべての本に購入日が設定されています")
            return
        
        print(f"\n📚 購入日が設定されていない本: {len(books_without_date)}冊\n")
        print("ID | タイトル | 著者 | ソース | ステータス")
        print("-" * 80)
        
        for book in books_without_date:
            print(f"{book['id']:3} | {book['title'][:40]:40} | {book['author'] or 'N/A':20} | {book['source']:7} | {book['status']}")


def main():
    parser = argparse.ArgumentParser(description='購入日を一括更新するスクリプト')
    parser.add_argument('--csv', help='CSVファイルから購入日をインポート')
    parser.add_argument('--json', help='JSONファイルから購入日をインポート')
    parser.add_argument('--interactive', action='store_true', help='インタラクティブモード')
    parser.add_argument('--list', action='store_true', help='購入日が設定されていない本を表示')
    parser.add_argument('--dry-run', action='store_true', help='実際には更新せず、更新予定を表示')
    
    args = parser.parse_args()
    
    if args.list:
        show_books_without_date()
    elif args.csv:
        update_from_csv(args.csv, dry_run=args.dry_run)
    elif args.json:
        update_from_json(args.json, dry_run=args.dry_run)
    elif args.interactive:
        interactive_mode()
    else:
        parser.print_help()
        print("\n💡 ヒント:")
        print("  - 購入日が設定されていない本を確認: python update_purchase_dates.py --list")
        print("  - インタラクティブモード: python update_purchase_dates.py --interactive")
        print("  - CSVからインポート: python update_purchase_dates.py --csv purchase_dates.csv")
        print("  - JSONからインポート: python update_purchase_dates.py --json purchase_dates.json")


if __name__ == "__main__":
    main()

