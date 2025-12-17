#!/usr/bin/env python3
"""
書籍データベース CLI ツール

使い方:
  python book_cli.py list              # 全ての本をリスト表示
  python book_cli.py stats             # 統計情報を表示
  python book_cli.py search "タイトル" # タイトルで検索
  python book_cli.py audible           # Audibleの本のみ表示
  python book_cli.py kindle            # Kindleの本のみ表示
  python book_cli.py in-progress       # 進行中の本を表示
  python book_cli.py export            # Markdownにエクスポート
  python book_cli.py add               # 本を追加（対話式）
  python book_cli.py update ID         # 本を更新
  python book_cli.py delete ID         # 本を削除
"""

import sys
import argparse
from db_manager import BookDatabase


def list_books(args):
    """全ての本をリスト表示"""
    with BookDatabase() as db:
        books = db.search_books()
        
        if not books:
            print("📚 本が登録されていません")
            return
        
        print(f"\n📚 登録されている本: {len(books)}冊\n")
        print(f"{'ID':<5} {'Source':<10} {'Status':<15} {'Title':<60} {'Author':<30}")
        print("-" * 120)
        
        for book in books:
            status_jp = {
                'completed': '完了',
                'in_progress': '進行中',
                'not_started': '未聴取',
                'purchased': '購入済み'
            }.get(book['status'], book['status'])
            
            title = book['title'][:57] + "..." if len(book['title']) > 60 else book['title']
            author = (book['author'] or "")[:27] + "..." if book['author'] and len(book['author']) > 30 else (book['author'] or "")
            
            print(f"{book['id']:<5} {book['source']:<10} {status_jp:<15} {title:<60} {author:<30}")


def show_stats(args):
    """統計情報を表示"""
    with BookDatabase() as db:
        stats = db.get_statistics()
        
        print("\n" + "=" * 60)
        print("📊 書籍データベース統計")
        print("=" * 60)
        
        print(f"\n{'ソース':<15} {'ステータス':<15} {'冊数':>10}")
        print("-" * 45)
        
        total = 0
        for stat in stats:
            status_jp = {
                'completed': '完了',
                'in_progress': '進行中',
                'not_started': '未聴取',
                'purchased': '購入済み'
            }.get(stat['status'], stat['status'])
            
            print(f"{stat['source']:<15} {status_jp:<15} {stat['count']:>10}冊")
            total += stat['count']
        
        print("-" * 45)
        print(f"{'合計':<30} {total:>10}冊")
        print()


def search_books(args):
    """本を検索"""
    with BookDatabase() as db:
        books = db.search_books(
            source=args.source,
            status=args.status,
            title_search=args.title,
            author_search=args.author,
            category=args.category if hasattr(args, 'category') else None
        )
        
        if not books:
            print("🔍 該当する本が見つかりませんでした")
            return
        
        print(f"\n🔍 検索結果: {len(books)}冊\n")
        
        for book in books:
            print(f"ID: {book['id']}")
            print(f"  タイトル: {book['title']}")
            print(f"  著者: {book['author'] or 'N/A'}")
            print(f"  ソース: {book['source']}")
            
            status_jp = {
                'completed': '完了',
                'in_progress': '進行中',
                'not_started': '未聴取',
                'purchased': '購入済み'
            }.get(book['status'], book['status'])
            print(f"  ステータス: {status_jp}")
            
            if book.get('category'):
                print(f"  カテゴリ: {book['category']}")
            if book.get('tags'):
                print(f"  タグ: {book['tags']}")
            if book['remaining_time']:
                print(f"  残り時間: {book['remaining_time']}")
            if book['page_number']:
                print(f"  ページ: {book['page_number']}")
            if book['purchase_order']:
                print(f"  購入順: {book['purchase_order']}")
            print()


def show_audible(args):
    """Audibleの本を表示"""
    with BookDatabase() as db:
        print("\n📘 Audible - 完了した本")
        print("-" * 80)
        completed = db.get_audible_completed()
        for i, book in enumerate(completed, 1):
            print(f"{i}. {book['title']} / {book['author']}")
        
        print(f"\n📗 Audible - 進行中の本 (残り時間あり)")
        print("-" * 80)
        in_progress = db.get_audible_in_progress()
        for i, book in enumerate(in_progress, 1):
            remaining = book['remaining_time'] or 'N/A'
            page = book['page_number'] or '-'
            print(f"{i}. {book['title']} / {book['author']} (残り: {remaining}, ページ: {page})")
        
        print(f"\n📙 Audible - 未聴取の本")
        print("-" * 80)
        not_started = db.get_audible_not_started()
        for i, book in enumerate(not_started, 1):
            page = book['page_number'] or '-'
            print(f"{i}. {book['title']} / {book['author']} (ページ: {page})")
        
        print(f"\n合計: 完了{len(completed)}冊 + 進行中{len(in_progress)}冊 + 未聴取{len(not_started)}冊 = {len(completed) + len(in_progress) + len(not_started)}冊")


def show_kindle(args):
    """Kindleの本を表示"""
    with BookDatabase() as db:
        print("\n📕 Kindle - 全ての本（購入順）")
        print("-" * 80)
        kindle = db.get_kindle_all()
        for book in kindle:
            print(f"{book['purchase_order']}. {book['title']} / {book['author']}")
        print(f"\n合計: {len(kindle)}冊")


def show_in_progress(args):
    """進行中の本を表示"""
    with BookDatabase() as db:
        books = db.search_books(status='in_progress')
        
        if not books:
            print("📗 進行中の本はありません")
            return
        
        print(f"\n📗 進行中の本: {len(books)}冊\n")
        
        for i, book in enumerate(books, 1):
            print(f"{i}. {book['title']}")
            print(f"   著者: {book['author'] or 'N/A'}")
            if book.get('category'):
                print(f"   カテゴリ: {book['category']}")
            if book['remaining_time']:
                print(f"   残り時間: {book['remaining_time']}")
            if book['page_number']:
                print(f"   ページ: {book['page_number']}")
            print()


def show_categories(args):
    """カテゴリ一覧を表示"""
    with BookDatabase() as db:
        cursor = db.conn.execute("""
            SELECT category, total_books, completed, in_progress, not_started, purchased
            FROM categories_summary
            ORDER BY total_books DESC
        """)
        
        categories = [dict(row) for row in cursor.fetchall()]
        
        if not categories:
            print("📂 カテゴリがありません")
            return
        
        print("\n" + "=" * 90)
        print("📂 カテゴリ別統計")
        print("=" * 90)
        
        print(f"\n{'カテゴリ':30s} {'合計':>6s} {'完了':>6s} {'進行':>6s} {'未読':>6s} {'購入':>6s}")
        print("-" * 90)
        
        total_sum = 0
        for cat in categories:
            print(f"{cat['category']:30s} {cat['total_books']:6d} {cat['completed']:6d} "
                  f"{cat['in_progress']:6d} {cat['not_started']:6d} {cat['purchased']:6d}")
            total_sum += cat['total_books']
        
        print("-" * 90)
        print(f"{'合計':30s} {total_sum:6d}\n")


def show_category_books(args):
    """特定カテゴリの本を表示"""
    category = args.category
    
    with BookDatabase() as db:
        books = db.search_books(category=category)
        
        if not books:
            print(f"📂 カテゴリ「{category}」の本が見つかりません")
            return
        
        print(f"\n📂 カテゴリ: {category} ({len(books)}冊)\n")
        
        for i, book in enumerate(books, 1):
            status_jp = {
                'completed': '✅',
                'in_progress': '📗',
                'not_started': '📚',
                'purchased': '📕'
            }.get(book['status'], '  ')
            
            print(f"{status_jp} {i}. {book['title']}")
            print(f"      著者: {book['author'] or 'N/A'}")
            print(f"      ソース: {book['source']}")
            if book['remaining_time']:
                print(f"      残り時間: {book['remaining_time']}")
            print()


def export_markdown(args):
    """Markdownにエクスポート"""
    output_path = args.output or "book_export.md"
    
    with BookDatabase() as db:
        db.export_to_markdown(output_path)
    
    print(f"\n✅ エクスポート完了: {output_path}")


def add_book_interactive(args):
    """本を追加（対話式）"""
    print("\n📚 新しい本を追加")
    print("-" * 60)
    
    title = input("タイトル: ").strip()
    if not title:
        print("❌ タイトルは必須です")
        return
    
    author = input("著者: ").strip() or None
    
    print("\nソースを選択:")
    print("  1. Audible")
    print("  2. Kindle")
    source_choice = input("選択 (1 or 2): ").strip()
    source = "Audible" if source_choice == "1" else "Kindle"
    
    print("\nステータスを選択:")
    if source == "Audible":
        print("  1. 完了 (completed)")
        print("  2. 進行中 (in_progress)")
        print("  3. 未聴取 (not_started)")
        status_choice = input("選択 (1, 2, or 3): ").strip()
        status_map = {"1": "completed", "2": "in_progress", "3": "not_started"}
    else:
        print("  1. 購入済み (purchased)")
        status_choice = "1"
        status_map = {"1": "purchased"}
    
    status = status_map.get(status_choice, "not_started")
    
    remaining_time = None
    page_number = None
    purchase_order = None
    
    if source == "Audible" and status == "in_progress":
        remaining_time = input("残り時間 (例: 10時間 5分): ").strip() or None
    
    if source == "Audible":
        page_input = input("ページ番号 (1-6): ").strip()
        if page_input.isdigit():
            page_number = int(page_input)
    
    if source == "Kindle":
        order_input = input("購入順序: ").strip()
        if order_input.isdigit():
            purchase_order = int(order_input)
    
    notes = input("メモ（任意）: ").strip() or None
    
    with BookDatabase() as db:
        book_id = db.add_book(
            title=title,
            author=author,
            source=source,
            status=status,
            remaining_time=remaining_time,
            page_number=page_number,
            purchase_order=purchase_order,
            notes=notes
        )
    
    print(f"\n✅ 本を追加しました (ID: {book_id})")


def update_book(args):
    """本を更新"""
    book_id = args.id
    
    with BookDatabase() as db:
        book = db.get_book(book_id)
        
        if not book:
            print(f"❌ ID {book_id} の本が見つかりません")
            return
        
        print(f"\n📝 本を更新 (ID: {book_id})")
        print(f"現在のタイトル: {book['title']}")
        print("-" * 60)
        
        # 更新する項目を入力
        updates = {}
        
        if args.title:
            updates['title'] = args.title
        if args.author:
            updates['author'] = args.author
        if args.status:
            updates['status'] = args.status
        if args.remaining_time:
            updates['remaining_time'] = args.remaining_time
        if args.notes:
            updates['notes'] = args.notes
        
        if not updates:
            print("❌ 更新する項目を指定してください")
            return
        
        db.update_book(book_id, **updates)
        print(f"✅ 本を更新しました")


def delete_book(args):
    """本を削除"""
    book_id = args.id
    
    with BookDatabase() as db:
        book = db.get_book(book_id)
        
        if not book:
            print(f"❌ ID {book_id} の本が見つかりません")
            return
        
        print(f"\n⚠️  以下の本を削除しますか？")
        print(f"ID: {book_id}")
        print(f"タイトル: {book['title']}")
        print(f"著者: {book['author'] or 'N/A'}")
        
        confirm = input("\n削除する場合は 'yes' を入力: ").strip().lower()
        
        if confirm == 'yes':
            db.delete_book(book_id)
            print("✅ 本を削除しました")
        else:
            print("❌ 削除をキャンセルしました")


def main():
    parser = argparse.ArgumentParser(
        description="書籍データベース CLI ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='コマンド')
    
    # list コマンド
    parser_list = subparsers.add_parser('list', help='全ての本をリスト表示')
    parser_list.set_defaults(func=list_books)
    
    # stats コマンド
    parser_stats = subparsers.add_parser('stats', help='統計情報を表示')
    parser_stats.set_defaults(func=show_stats)
    
    # search コマンド
    parser_search = subparsers.add_parser('search', help='本を検索')
    parser_search.add_argument('--title', help='タイトルで検索')
    parser_search.add_argument('--author', help='著者で検索')
    parser_search.add_argument('--source', choices=['Audible', 'Kindle'], help='ソースで絞り込み')
    parser_search.add_argument('--status', choices=['completed', 'in_progress', 'not_started', 'purchased'], help='ステータスで絞り込み')
    parser_search.add_argument('--category', help='カテゴリで絞り込み')
    parser_search.set_defaults(func=search_books)
    
    # audible コマンド
    parser_audible = subparsers.add_parser('audible', help='Audibleの本を表示')
    parser_audible.set_defaults(func=show_audible)
    
    # kindle コマンド
    parser_kindle = subparsers.add_parser('kindle', help='Kindleの本を表示')
    parser_kindle.set_defaults(func=show_kindle)
    
    # in-progress コマンド
    parser_in_progress = subparsers.add_parser('in-progress', help='進行中の本を表示')
    parser_in_progress.set_defaults(func=show_in_progress)
    
    # categories コマンド
    parser_categories = subparsers.add_parser('categories', help='カテゴリ一覧を表示')
    parser_categories.set_defaults(func=show_categories)
    
    # category コマンド
    parser_category = subparsers.add_parser('category', help='特定カテゴリの本を表示')
    parser_category.add_argument('category', help='カテゴリ名')
    parser_category.set_defaults(func=show_category_books)
    
    # export コマンド
    parser_export = subparsers.add_parser('export', help='Markdownにエクスポート')
    parser_export.add_argument('--output', '-o', help='出力ファイル名')
    parser_export.set_defaults(func=export_markdown)
    
    # add コマンド
    parser_add = subparsers.add_parser('add', help='本を追加（対話式）')
    parser_add.set_defaults(func=add_book_interactive)
    
    # update コマンド
    parser_update = subparsers.add_parser('update', help='本を更新')
    parser_update.add_argument('id', type=int, help='本のID')
    parser_update.add_argument('--title', help='タイトル')
    parser_update.add_argument('--author', help='著者')
    parser_update.add_argument('--status', choices=['completed', 'in_progress', 'not_started', 'purchased'], help='ステータス')
    parser_update.add_argument('--remaining-time', dest='remaining_time', help='残り時間')
    parser_update.add_argument('--notes', help='メモ')
    parser_update.set_defaults(func=update_book)
    
    # delete コマンド
    parser_delete = subparsers.add_parser('delete', help='本を削除')
    parser_delete.add_argument('id', type=int, help='本のID')
    parser_delete.set_defaults(func=delete_book)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()

