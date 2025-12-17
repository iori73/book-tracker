#!/usr/bin/env python3
"""
簡単に購入日を更新するスクリプト

使用方法:
python quick_update_purchase_date.py <book_id> <purchase_date>
例: python quick_update_purchase_date.py 41 2021-11-20
"""

import sys
from db_manager import BookDatabase

if len(sys.argv) < 3:
    print("使用方法: python quick_update_purchase_date.py <book_id> <purchase_date>")
    print("例: python quick_update_purchase_date.py 41 2021-11-20")
    sys.exit(1)

book_id = int(sys.argv[1])
purchase_date = sys.argv[2]

with BookDatabase() as db:
    book = db.get_book(book_id)
    if not book:
        print(f"❌ ID {book_id} の本が見つかりません")
        sys.exit(1)
    
    print(f"📚 {book['title']} / {book['author']}")
    print(f"現在の購入日: {book.get('purchase_date') or '未設定'}")
    
    db.update_book(book_id, purchase_date=purchase_date)
    print(f"✅ 購入日を更新しました: {purchase_date}")

