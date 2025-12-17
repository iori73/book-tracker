#!/usr/bin/env python3
"""
書籍に自動的にカテゴリを付与するスクリプト

タイトルと著者から意味的に判断してカテゴリを決定します。
"""

import sqlite3
import re
from typing import Dict, List, Tuple

DB_PATH = "book_tracker.db"

# カテゴリ定義とキーワード
CATEGORIES = {
    "脳科学・神経科学": [
        "脳", "神経", "意識", "認知", "感情", "心理", "brain", "neuroscience", 
        "consciousness", "池谷裕二", "中野信子", "渡辺正峰"
    ],
    "ビジネス・経営": [
        "ビジネス", "経営", "マネジメント", "リーダーシップ", "組織", "戦略",
        "コンサル", "起業", "イノベーション", "management", "business", "山口周"
    ],
    "デザイン・UI/UX": [
        "デザイン", "UI", "UX", "インターフェース", "ユーザー", "design",
        "interface", "user experience", "プロダクト"
    ],
    "技術・プログラミング": [
        "プログラミング", "アルゴリズム", "ソフトウェア", "アーキテクチャ",
        "システム", "データベース", "programming", "software", "algorithm",
        "architecture", "code", "engineer"
    ],
    "経済・金融": [
        "経済", "金融", "投資", "お金", "資本", "市場", "finance", "economy",
        "investment", "金利", "決算", "会計", "簿記"
    ],
    "歴史・地政学": [
        "歴史", "地政学", "政治", "世界史", "日本史", "戦争", "外交",
        "history", "geopolitics", "池上彰", "茂木誠", "出口治明"
    ],
    "哲学・思想": [
        "哲学", "思想", "東洋", "禅", "センス", "問い", "philosophy",
        "千葉雅也", "石川善樹"
    ],
    "生物学・進化": [
        "生物", "進化", "生命", "植物", "動物", "ecology", "evolution",
        "biology", "species", "darwin", "extinction", "bee", "fish"
    ],
    "健康・運動・栄養": [
        "健康", "運動", "筋トレ", "栄養", "食", "睡眠", "疲れ", "health",
        "exercise", "fitness", "nutrition", "protein", "ダイエット", "腸"
    ],
    "自己啓発・マインドフルネス": [
        "習慣", "マインドフルネス", "瞑想", "集中", "生産性", "時間",
        "mindfulness", "habit", "productivity", "ウェルビーイング", "反応しない"
    ],
    "語学・英語": [
        "英語", "英会話", "english", "language", "speaking", "vocabulary",
        "起きてから寝るまで", "ネイティブ"
    ],
    "科学一般": [
        "科学", "物理", "化学", "天文", "宇宙", "science", "physics",
        "chemistry", "astrophysics", "複雑系"
    ],
    "社会・人類学": [
        "社会", "人類", "文化", "民主主義", "diversity", "anthropology",
        "society", "WEIRD", "plurality"
    ],
    "テクノロジー・未来": [
        "AI", "人工知能", "テクノロジー", "未来", "2030", "2041", "web3",
        "NFT", "DAO", "technology", "future", "innovation"
    ],
    "環境・エネルギー": [
        "環境", "エネルギー", "気候", "脱炭素", "グリーン", "environment",
        "energy", "climate", "carbon", "アフリカ", "silent spring"
    ],
    "文学・エッセイ": [
        "文学", "小説", "エッセイ", "陰翳礼讃", "gatsby", "谷崎",
        "朗読", "wonder"
    ],
    "思考法・問題解決": [
        "思考", "問題解決", "イシュー", "メタ思考", "抽象", "具体",
        "thinking", "problem solving", "critical", "ロジカル"
    ],
    "データ・可視化": [
        "データ", "可視化", "グラフ", "visualization", "data", "analytics",
        "統計"
    ],
    "教養・一般": [
        "教養", "知識", "学び", "入門", "基本", "わかる", "面白い"
    ]
}

def categorize_book(title: str, author: str) -> Tuple[str, List[str]]:
    """
    タイトルと著者から本のカテゴリとタグを決定
    
    Returns:
        (category, tags): メインカテゴリと追加タグのリスト
    """
    title_lower = title.lower()
    author_lower = (author or "").lower()
    combined = f"{title_lower} {author_lower}"
    
    # 各カテゴリとのマッチ度を計算
    scores = {}
    matched_keywords = {}
    
    for category, keywords in CATEGORIES.items():
        score = 0
        matches = []
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in combined:
                score += 1
                matches.append(keyword)
        
        if score > 0:
            scores[category] = score
            matched_keywords[category] = matches
    
    # スコアが高い順にソート
    sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    if not sorted_categories:
        # マッチするカテゴリがない場合
        return "その他", []
    
    # メインカテゴリは最もスコアが高いもの
    main_category = sorted_categories[0][0]
    
    # タグは上位3つのカテゴリ（メインを除く）
    tags = [cat for cat, score in sorted_categories[1:4] if score >= 1]
    
    return main_category, tags


def update_categories():
    """全ての本にカテゴリとタグを付与"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # カテゴリカラムを追加（既に存在する場合はスキップ）
    try:
        conn.execute("ALTER TABLE books ADD COLUMN category TEXT")
        conn.execute("ALTER TABLE books ADD COLUMN tags TEXT")
        print("✅ カテゴリカラムを追加しました")
    except sqlite3.OperationalError:
        print("ℹ️  カテゴリカラムは既に存在します")
    
    # 全ての本を取得
    cursor = conn.execute("SELECT id, title, author FROM books")
    books = cursor.fetchall()
    
    print(f"\n📚 {len(books)}冊の本を分析中...\n")
    
    # カテゴリ統計
    category_counts = {}
    
    # 各本にカテゴリを付与
    for book in books:
        book_id = book['id']
        title = book['title']
        author = book['author']
        
        category, tags = categorize_book(title, author)
        tags_str = ",".join(tags) if tags else None
        
        # データベースを更新
        conn.execute(
            "UPDATE books SET category = ?, tags = ? WHERE id = ?",
            (category, tags_str, book_id)
        )
        
        # 統計
        category_counts[category] = category_counts.get(category, 0) + 1
        
        # 進捗表示
        print(f"  {book_id:3d}. [{category:25s}] {title[:50]}")
    
    conn.commit()
    
    # インデックスとビューを作成
    print("\n📊 インデックスとビューを作成中...")
    with open('add_categories.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
        # ALTER TABLE は既に実行済みなのでスキップ
        for statement in sql_script.split(';'):
            if statement.strip() and 'ALTER TABLE' not in statement:
                try:
                    conn.execute(statement)
                except sqlite3.OperationalError as e:
                    if 'already exists' not in str(e):
                        print(f"⚠️  {e}")
    
    conn.commit()
    
    # カテゴリ統計を表示
    print("\n" + "=" * 80)
    print("📊 カテゴリ別統計")
    print("=" * 80)
    
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    for category, count in sorted_categories:
        print(f"  {category:30s}: {count:3d}冊")
    
    print(f"\n  {'合計':30s}: {len(books):3d}冊")
    
    # ビューから統計を取得
    print("\n" + "=" * 80)
    print("📈 カテゴリ別詳細統計")
    print("=" * 80)
    
    cursor = conn.execute("""
        SELECT category, total_books, completed, in_progress, not_started, purchased
        FROM categories_summary
    """)
    
    print(f"\n{'カテゴリ':30s} {'合計':>6s} {'完了':>6s} {'進行':>6s} {'未読':>6s} {'購入':>6s}")
    print("-" * 80)
    
    for row in cursor:
        print(f"{row['category']:30s} {row['total_books']:6d} {row['completed']:6d} "
              f"{row['in_progress']:6d} {row['not_started']:6d} {row['purchased']:6d}")
    
    conn.close()
    
    print("\n✅ カテゴリ付与が完了しました！")


if __name__ == "__main__":
    update_categories()

