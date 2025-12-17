#!/usr/bin/env python3
"""
ブラウザからAmazonの注文履歴ページを開いて、購入日を抽出するスクリプト

このスクリプトは、ブラウザでAmazonの注文履歴ページを開き、
表示されている本の購入日を抽出してデータベースに登録します。

使用方法:
1. ブラウザでAmazonの注文履歴ページを開く
2. このスクリプトを実行して、ページのHTMLを解析
3. 購入日を抽出してデータベースに登録
"""

import re
from datetime import datetime
from db_manager import BookDatabase


def parse_date_jp(date_str: str) -> str:
    """日本語の日付文字列をYYYY-MM-DD形式に変換"""
    # "2021年12月15日" -> "2021-12-15"
    match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
    if match:
        year = match.group(1)
        month = match.group(2).zfill(2)
        day = match.group(3).zfill(2)
        return f"{year}-{month}-{day}"
    
    # "December 15, 2021" -> "2021-12-15"
    try:
        dt = datetime.strptime(date_str, "%B %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except:
        pass
    
    return None


def extract_orders_from_html(html_content: str) -> list:
    """HTMLから注文情報を抽出"""
    orders = []
    
    # 注文日のパターンを探す
    # "Order placed December 15, 2021" または "注文日 2021年12月15日"
    date_patterns = [
        r'Order placed\s+(\w+\s+\d+,\s+\d{4})',
        r'注文日[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)',
        r'(\d{4}年\d{1,2}月\d{1,2}日)',
    ]
    
    # タイトルのパターンを探す
    # リンクや見出しからタイトルを抽出
    title_pattern = r'<a[^>]*>([^<]+(?:本|Book|書籍)[^<]*)</a>'
    
    # 簡単な実装: ユーザーが手動で情報を入力する方が確実
    return orders


# 手動で情報を入力する方法
def manual_update_from_amazon_orders():
    """Amazonの注文履歴から手動で購入日を入力して更新"""
    print("=" * 60)
    print("Amazon注文履歴から購入日を更新")
    print("=" * 60)
    print("\n注文履歴ページから以下の情報を入力してください：")
    print("（Enterキーを押すとスキップできます）\n")
    
    with BookDatabase() as db:
        while True:
            print("\n" + "-" * 60)
            title = input("本のタイトル（または 'q' で終了）: ").strip()
            if title.lower() == 'q':
                break
            if not title:
                continue
            
            # タイトルで検索
            books = db.search_books(title_search=title)
            if not books:
                print(f"⚠️  '{title}' が見つかりませんでした")
                continue
            
            if len(books) > 1:
                print(f"\n複数の本が見つかりました:")
                for i, b in enumerate(books, 1):
                    print(f"  {i}. ID: {b['id']}, {b['title']} / {b['author']}")
                choice = input("番号を選択（Enterで最初の1つ）: ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(books):
                    book = books[int(choice) - 1]
                else:
                    book = books[0]
            else:
                book = books[0]
            
            print(f"\n選択した本: {book['title']} / {book['author']}")
            print(f"現在の購入日: {book.get('purchase_date') or '未設定'}")
            
            date_input = input("購入日を入力 (YYYY-MM-DD形式、例: 2021-12-15): ").strip()
            if not date_input:
                print("スキップしました")
                continue
            
            # 日付形式を変換
            purchase_date = None
            if re.match(r'\d{4}-\d{2}-\d{2}', date_input):
                purchase_date = date_input
            else:
                purchase_date = parse_date_jp(date_input)
            
            if not purchase_date:
                print("❌ 無効な日付形式です")
                continue
            
            # 更新
            db.update_book(book['id'], purchase_date=purchase_date)
            print(f"✅ 購入日を更新しました: {purchase_date}")


if __name__ == "__main__":
    manual_update_from_amazon_orders()

