#!/usr/bin/env python3
"""
Amazonの注文履歴ページから購入日を抽出してデータベースに更新するスクリプト

使用方法:
python update_from_amazon_orders.py [year]
例: python update_from_amazon_orders.py 2021
"""

import re
import sys
from datetime import datetime
from db_manager import BookDatabase
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def parse_date_en(date_str: str) -> str:
    """英語の日付文字列をYYYY-MM-DD形式に変換"""
    try:
        dt = datetime.strptime(date_str.strip(), "%B %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except:
        return None


def find_book_in_database(title: str, db: BookDatabase):
    """データベースで本を検索"""
    # タイトルで検索
    books = db.search_books(title_search=title)
    if books:
        return books[0] if len(books) == 1 else books
    
    # タイトルの一部で検索
    words = title.split()
    for word in words:
        if len(word) > 3:  # 3文字以上の単語で検索
            books = db.search_books(title_search=word)
            if books:
                return books[0] if len(books) == 1 else books
    
    return None


def extract_orders_from_page(page):
    """ページから注文情報を抽出"""
    orders = []
    
    # ページが完全に読み込まれるまで待つ
    try:
        page.wait_for_selector('body', timeout=10000)
    except PlaywrightTimeoutError:
        print("ページの読み込みに時間がかかっています...")
    
    # ページのテキストを取得
    page_text = page.inner_text('body')
    
    # 注文セクションを探す
    # "Order placed" というテキストを含む要素を探す
    order_elements = page.query_selector_all('h5, h4, [class*="order"], [data-order-id]')
    
    for element in order_elements:
        text = element.inner_text()
        if 'Order placed' in text or 'Subscription charged on' in text:
            # 日付を抽出
            date_match = re.search(r'(?:Order placed|Subscription charged on)\s+([A-Za-z]+\s+\d+,\s+\d{4})', text)
            if date_match:
                date_str = date_match.group(1)
                purchase_date = parse_date_en(date_str)
                
                if purchase_date:
                    # 親要素を取得して、その中の本のタイトルを探す
                    parent = element.evaluate_handle('el => el.closest("div, section, article")')
                    if parent:
                        # リンクを探す
                        try:
                            links = parent.query_selector_all('a[href*="/dp/"], a[href*="/product"]')
                            for link in links:
                                title = link.inner_text().strip()
                                # 意味のあるタイトルかチェック
                                if title and len(title) > 10 and not title.startswith('http'):
                                    # 本に関連するキーワードをチェック
                                    if any(keyword in title.lower() for keyword in ['book', '本', 'audiobook', 'オーディオブック', 'kindle', 'audible']):
                                        orders.append({
                                            'title': title,
                                            'purchase_date': purchase_date
                                        })
                                        break
                        except:
                            pass
    
    return orders


def update_purchase_dates_from_amazon(year=2021):
    """Amazonの注文履歴ページから購入日を抽出して更新"""
    print("=" * 60)
    print(f"Amazon注文履歴（{year}年）から購入日を抽出して更新")
    print("=" * 60)
    
    url = f"https://www.amazon.co.jp/your-orders/orders?timeFilter=year-{year}"
    print(f"\nブラウザで {url} にアクセスしています...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            print("✅ ページを読み込みました")
            
            # ページが完全に読み込まれるまで待つ
            page.wait_for_timeout(5000)
            
            # 注文情報を抽出
            print("\n📖 ページから注文情報を抽出中...")
            orders = extract_orders_from_page(page)
            
            if not orders:
                print("⚠️  自動抽出できませんでした。手動で情報を入力してください。\n")
                print("ページを見ながら、以下の情報を入力してください：\n")
                
                with BookDatabase() as db:
                    while True:
                        print("-" * 60)
                        title = input("本のタイトル（または 'q' で終了）: ").strip()
                        if title.lower() == 'q':
                            break
                        if not title:
                            continue
                        
                        book = find_book_in_database(title, db)
                        if not book:
                            print(f"⚠️  '{title}' が見つかりませんでした")
                            continue
                        
                        if isinstance(book, list):
                            print(f"\n複数の本が見つかりました:")
                            for i, b in enumerate(book, 1):
                                print(f"  {i}. ID: {b['id']}, {b['title']} / {b['author']}")
                            choice = input("番号を選択（Enterで最初の1つ）: ").strip()
                            if choice.isdigit() and 1 <= int(choice) <= len(book):
                                book = book[int(choice) - 1]
                            else:
                                book = book[0]
                        
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
                            purchase_date = parse_date_en(date_input)
                        
                        if not purchase_date:
                            print("❌ 無効な日付形式です")
                            continue
                        
                        # 更新
                        db.update_book(book['id'], purchase_date=purchase_date)
                        print(f"✅ 購入日を更新しました: {purchase_date}")
            else:
                print(f"\n✅ {len(orders)}件の注文情報を抽出しました")
                
                with BookDatabase() as db:
                    updated = 0
                    not_found = []
                    
                    for order in orders:
                        print(f"\n📚 {order['title']} - {order['purchase_date']}")
                        book = find_book_in_database(order['title'], db)
                        
                        if book:
                            if isinstance(book, list):
                                book = book[0]  # 最初の1つを選択
                            
                            db.update_book(book['id'], purchase_date=order['purchase_date'])
                            print(f"  ✅ 更新: {book['title']} (ID: {book['id']})")
                            updated += 1
                        else:
                            print(f"  ⚠️  データベースに見つかりませんでした")
                            not_found.append(order)
                    
                    print(f"\n📊 更新完了: {updated}冊")
                    if not_found:
                        print(f"⚠️  見つからなかった本: {len(not_found)}冊")
            
            print("\n✅ 完了しました。ブラウザを閉じるにはEnterキーを押してください。")
            input()
            browser.close()
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            browser.close()


if __name__ == "__main__":
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2021
    update_purchase_dates_from_amazon(year)

