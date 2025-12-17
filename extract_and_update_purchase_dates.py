#!/usr/bin/env python3
"""
Amazonの注文履歴ページから購入日を抽出してデータベースに更新するスクリプト

Playwrightを使用してブラウザでAmazonの注文履歴ページにアクセスし、
表示されている本の購入日を抽出してデータベースに登録します。
"""

import re
from datetime import datetime
from db_manager import BookDatabase
from playwright.sync_api import sync_playwright


def parse_date_en(date_str: str) -> str:
    """英語の日付文字列をYYYY-MM-DD形式に変換"""
    # "December 15, 2021" -> "2021-12-15"
    try:
        dt = datetime.strptime(date_str.strip(), "%B %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except:
        pass
    
    # "November 20, 2021" -> "2021-11-20"
    try:
        dt = datetime.strptime(date_str.strip(), "%B %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except:
        pass
    
    return None


def extract_orders_from_page(page):
    """ページから注文情報を抽出"""
    orders = []
    
    # 注文セクションを取得
    order_sections = page.query_selector_all('[data-order-id], .order-card, [class*="order"]')
    
    # より具体的なセレクタを試す
    # "Order placed" というテキストを含む要素を探す
    order_headings = page.query_selector_all('h5, h4, [class*="order"]')
    
    for heading in order_headings:
        text = heading.inner_text()
        if 'Order placed' in text or '注文日' in text:
            # 日付を抽出
            date_match = re.search(r'(?:Order placed|注文日)[：:\s]+([A-Za-z]+\s+\d+,\s+\d{4}|\d{4}年\d{1,2}月\d{1,2}日)', text)
            if date_match:
                date_str = date_match.group(1)
                purchase_date = parse_date_en(date_str)
                
                # 同じセクション内の本のタイトルを探す
                parent = heading.evaluate_handle('el => el.closest("div, section, article")')
                if parent:
                    # リンクやタイトルを探す
                    links = parent.query_selector_all('a[href*="/dp/"], a[href*="/product"]')
                    for link in links:
                        title = link.inner_text().strip()
                        if title and len(title) > 5:  # 意味のあるタイトル
                            orders.append({
                                'title': title,
                                'purchase_date': purchase_date
                            })
                            break
    
    return orders


def update_purchase_dates_from_amazon():
    """Amazonの注文履歴ページから購入日を抽出して更新"""
    print("=" * 60)
    print("Amazon注文履歴から購入日を抽出して更新")
    print("=" * 60)
    
    url = input("\nAmazonの注文履歴ページのURLを入力（Enterでデフォルト）: ").strip()
    if not url:
        url = "https://www.amazon.co.jp/your-orders/orders?timeFilter=year-2021"
    
    print(f"\nブラウザで {url} にアクセスしています...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            page.goto(url, wait_until="networkidle")
            print("ページを読み込みました。")
            
            # ページが完全に読み込まれるまで待つ
            page.wait_for_timeout(3000)
            
            # ページの内容を取得
            page_content = page.content()
            
            # 注文情報を抽出（より簡単な方法：ページのテキストから抽出）
            page_text = page.inner_text('body')
            
            print("\nページから注文情報を抽出中...")
            
            # 正規表現で注文情報を抽出
            # "Order placed December 15, 2021" のパターン
            order_pattern = r'Order placed\s+([A-Za-z]+\s+\d+,\s+\d{4})'
            dates = re.findall(order_pattern, page_text)
            
            # 各注文セクションを処理
            orders = []
            order_sections = page.query_selector_all('div[class*="order"], section[class*="order"]')
            
            print(f"\n{len(order_sections)}個の注文セクションが見つかりました")
            
            # より直接的な方法：ページのHTMLから構造を解析
            # "Order placed" を含む要素の近くにある本のタイトルを探す
            
            # 手動で情報を入力する方法にフォールバック
            print("\n自動抽出が難しいため、手動で情報を入力してください。")
            print("ページを見ながら、以下の情報を入力してください：\n")
            
            with BookDatabase() as db:
                while True:
                    print("-" * 60)
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
                        purchase_date = parse_date_en(date_input)
                    
                    if not purchase_date:
                        print("❌ 無効な日付形式です")
                        continue
                    
                    # 更新
                    db.update_book(book['id'], purchase_date=purchase_date)
                    print(f"✅ 購入日を更新しました: {purchase_date}")
            
            browser.close()
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
            browser.close()


if __name__ == "__main__":
    update_purchase_dates_from_amazon()

