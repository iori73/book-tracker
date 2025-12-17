#!/usr/bin/env python3
"""
既存のMarkdownデータをデータベースにインポート
"""

import re
from db_manager import BookDatabase


def parse_audible_completed():
    """Audible完了した本をパース"""
    books = [
        {"title": "疲れない脳をつくる生活習慣―働く人のためのマインドフルネス講座", "author": "石川 善樹"},
        {"title": "世界の「頭のいい人」がやっていることを1冊にまとめてみた", "author": "中野 信子"},
        {"title": "脳はどこまでコントロールできるか?", "author": "中野 信子"},
        {"title": "脳は耳で感動する", "author": "養老 孟司, 久石 譲"},
        {"title": "１分で話せ 世界のトップが絶賛した大事なことだけシンプルに伝える技術", "author": "伊藤 羊一"},
        {"title": "2030年すべてが加速する未来に備える投資法", "author": "方波 見寧"},
        {"title": "１３歳からの地政学: カイゾクとの地球儀航海", "author": "田中 孝幸"},
    ]
    return books


def parse_audible_in_progress():
    """Audible進行中の本をパース"""
    books = [
        # ページ1
        {"title": "残り97%の脳の使い方【ポケット版】", "author": "苫米地 英人", "remaining_time": "2時間 28分", "page": 1},
        {"title": "朗読街道(142)日本人の自然観", "author": "寺田 寅彦", "remaining_time": "1時間 13分", "page": 1},
        {"title": "陰翳礼讃", "author": "谷崎 潤一郎", "remaining_time": "2分", "page": 1},
        {"title": "銃・病原菌・鉄 上", "author": "ジャレド ダイアモンド", "remaining_time": "10時間 5分", "page": 1},
        {"title": "The WEIRDest People in the World", "author": "Joseph Henrich", "remaining_time": "18時間 40分", "page": 1},
        {"title": "PLURALITY", "author": "オードリー・タン, E・グレン・ワイル", "remaining_time": "17時間 55分", "page": 1},
        
        # ページ2
        {"title": "学び直し高校物理 挫折者のための超入門", "author": "田口 善弘", "remaining_time": "6時間 27分", "page": 2},
        {"title": "外資系コンサルが教えるプロジェクトマネジメント", "author": "山口 周", "remaining_time": "3時間 45分", "page": 2},
        {"title": "Exercised", "author": "Daniel Lieberman", "remaining_time": "5時間 48分", "page": 2},
        {"title": "イシューからはじめよ［改訂版］", "author": "安宅 和人", "remaining_time": "3時間 50分", "page": 2},
        {"title": "運動の神話 下", "author": "ダニエル・E・リーバーマン", "remaining_time": "10時間 11分", "page": 2},
        {"title": "Hackers & Painters", "author": "Paul Graham", "remaining_time": "7時間 25分", "page": 2},
        {"title": "自分とか、ないから。", "author": "しんめいP", "remaining_time": "2時間 46分", "page": 2},
        
        # ページ4
        {"title": "Fundamentals of Software Architecture", "author": "Mark Richards, Neal Ford", "remaining_time": "12時間 38分", "page": 4},
        {"title": "AI時代の人生戦略「STEAM」が最強の武器である", "author": "成毛 眞", "remaining_time": "54分", "page": 4},
        {"title": "人工知能は人間を超えるか", "author": "松尾 豊", "remaining_time": "2時間 36分", "page": 4},
        {"title": "プロの思考整理術", "author": "和仁 達也", "remaining_time": "4時間 26分", "page": 4},
        {"title": "すみません、金利ってなんですか？", "author": "小林 義崇", "remaining_time": "4時間 44分", "page": 4},
        {"title": "聞き流すだけで英語をマスター：ピーターラビット", "author": "小分割/和英順方式普及会", "remaining_time": "4分", "page": 4},
        {"title": "知略を養う 戦争と外交の世界史", "author": "出口 治明", "remaining_time": "10時間 6分", "page": 4},
        
        # ページ5
        {"title": "完全改訂版 起きてから寝るまで 子育て英語表現600", "author": "吉田 研作, 春日 聡子", "remaining_time": "1時間 9分", "page": 5},
        {"title": "【限定特典付き】反応しない練習", "author": "草薙 龍瞬", "remaining_time": "5時間 8分", "page": 5},
        {"title": "【草薙龍瞬朗読】反応しない練習 特別版", "author": "草薙 龍瞬", "remaining_time": "4時間 28分", "page": 5},
        {"title": "科学者たちが語る食欲", "author": "デイヴィッド・ローベンハイマー, スティーヴン・Ｊ・シンプソン", "remaining_time": "2時間 57分", "page": 5},
        {"title": "［図解］池上彰の 政治と選挙のニュースが面白いほどわかる本", "author": "池上 彰", "remaining_time": "3時間 17分", "page": 5},
        {"title": "この社会で戦う君に「知の世界地図」をあげよう", "author": "池上 彰", "remaining_time": "2時間 8分", "page": 5},
        {"title": "世界史とつなげて学べ 超日本史", "author": "茂木 誠", "remaining_time": "8時間 39分", "page": 5},
        {"title": "ニュースの\"なぜ？\"は世界史に学べ", "author": "茂木 誠", "remaining_time": "1時間 7分", "page": 5},
        
        # ページ6
        {"title": "改訂第二版 起きてから寝るまで英単語帳", "author": "荒井貴和, 武藤克彦", "remaining_time": "1時間 48分", "page": 6},
        {"title": "起きてから寝るまで英語表現1000 海外旅行編", "author": "吉田研作, 荒井貴和, 武藤克彦", "remaining_time": "1時間 25分", "page": 6},
        {"title": "起きてから寝るまで英語表現1000オフィス編", "author": "アルク, 荒井 貴和, 吉田 研作, 武藤 克彦", "remaining_time": "6時間 36分", "page": 6},
        {"title": "起きてから寝るまで英語表現1000", "author": "荒井 貴和, 武藤 克彦, 吉田 研作", "remaining_time": "14分", "page": 6},
        {"title": "超加速経済アフリカ", "author": "椿 進", "remaining_time": "5時間 48分", "page": 6},
        {"title": "グリーン・ジャイアント 脱炭素ビジネスが世界経済を動かす", "author": "森川 潤", "remaining_time": "4分", "page": 6},
    ]
    return books


def parse_audible_not_started():
    """Audible未聴取の本をパース"""
    books = [
        # ページ1
        {"title": "多様性の科学", "author": "マシュー・サイド", "page": 1},
        {"title": "あなたという習慣を断つ", "author": "ジョー・ディスペンザ", "page": 1},
        {"title": "仕事はうかつに始めるな", "author": "石川 善樹", "page": 1},
        {"title": "世界は贈与でできている", "author": "近内 悠太", "page": 1},
        {"title": "センスの哲学", "author": "千葉雅也", "page": 1},
        {"title": "日本とユダヤの古代史＆世界史", "author": "田中 英道, 茂木 誠", "page": 1},
        {"title": "フルライフ", "author": "石川 善樹", "page": 1},
        {"title": "外資系コンサルが教える 読書を仕事につなげる技術", "author": "山口 周", "page": 1},
        {"title": "The Sense of Wonder", "author": "Rachel Carson", "page": 1},
        {"title": "脳の闇", "author": "中野 信子", "page": 1},
        {"title": "時間をかけて考える", "author": "養老 孟司", "page": 1},
        
        # ページ2
        {"title": "植物たちに心はあるのか", "author": "田中 修", "page": 2},
        {"title": "「腸と脳」の科学", "author": "坪井 貴司", "page": 2},
        {"title": "In Defense of Plants", "author": "Matt Candeias PhD", "page": 2},
        {"title": "Design for How People Think", "author": "John Whalen PhD", "page": 2},
        {"title": "The Laws of Simplicity", "author": "John Maeda", "page": 2},
        {"title": "「複雑系」入門", "author": "金 重明", "page": 2},
        {"title": "進化のからくり", "author": "千葉 聡", "page": 2},
        {"title": "How Emotions Are Made", "author": "Lisa Feldman Barrett", "page": 2},
        {"title": "「具体⇄抽象」トレーニング", "author": "細谷 功", "page": 2},
        {"title": "落ち込まない 考えすぎない気持ちの整理術", "author": "和田 秀樹", "page": 2},
        
        # ページ3
        {"title": "A Pocket Guide to Pigeon Watching", "author": "Rosemary Mosco", "page": 3},
        {"title": "Why Fish Don't Exist", "author": "Lulu Miller", "page": 3},
        {"title": "Expert Secrets - Critical Thinking", "author": "Maxwell Jensen", "page": 3},
        {"title": "イラスト＆図解 知識ゼロでも楽しく読める！ たんぱく質のしくみ", "author": "佐々木 一", "page": 3},
        {"title": "面白くて眠れなくなる植物学", "author": "稲垣 栄洋", "page": 3},
        {"title": "What Is Life?: Five Great Ideas in Biology", "author": "Paul Nurse", "page": 3},
        {"title": "The Mind of a Bee", "author": "Lars Chittka", "page": 3},
        {"title": "筋トレビジネスエリートがやっている最強の食べ方", "author": "Testosterone", "page": 3},
        {"title": "図解 PFCバランス超入門", "author": "浅見 陽輔", "page": 3},
        {"title": "筋肥大の3原理・5原則", "author": "浅見 陽輔", "page": 3},
        {"title": "脳を司る「脳」", "author": "毛内 拡", "page": 3},
        {"title": "睡眠の起源", "author": "金谷 啓之", "page": 3},
        {"title": "生物学的に、しょうがない！", "author": "石川 幹人", "page": 3},
        {"title": "進化しすぎた脳", "author": "池谷 裕二", "page": 3},
        {"title": "生命とは何か", "author": "シュレーディンガー", "page": 3},
        {"title": "生物から見た世界", "author": "ユクスキュル, クリサート", "page": 3},
        {"title": "Astrophysics for People in a Hurry", "author": "Neil deGrasse Tyson", "page": 3},
        {"title": "Algorithms to Live By", "author": "Brian Christian, Tom Griffiths", "page": 3},
        {"title": "Who We Are and How We Got Here", "author": "David Reich", "page": 3},
        {"title": "The Sixth Extinction", "author": "Elizabeth Kolbert", "page": 3},
        
        # ページ4
        {"title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann", "page": 4},
        {"title": "Silent Spring", "author": "Rachel Carson", "page": 4},
        {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "page": 4},
        {"title": "ＮＦＴの教科書", "author": "天羽 健介, 増田 雅史", "page": 4},
        {"title": "【限定特典付】Web3とDAO", "author": "亀井 聡彦, 鈴木 雄大, 赤澤 直樹", "page": 4},
        {"title": "努力不要論", "author": "中野 信子", "page": 4},
        {"title": "大富豪が実践しているお金の哲学", "author": "冨田 和成", "page": 4},
        {"title": "「説明が上手い人」がやっていることを1冊にまとめてみた", "author": "ハック大学 ぺそ", "page": 4},
        {"title": "世界はいつでも不安定", "author": "内藤 陽介", "page": 4},
        {"title": "今さら聞けない! 政治のキホンが2時間で全部頭に入る", "author": "馬屋原 吉博", "page": 4},
        {"title": "VOAニュースフラッシュ2021年度版", "author": "アルク", "page": 4},
        {"title": "知らないと損する 経済とおかねの超基本１年生", "author": "大江 英樹", "page": 4},
        {"title": "ENGLISH JOURNAL 2021年11月号", "author": "アルク", "page": 4},
        
        # ページ5
        {"title": "2025年を制覇する破壊的企業", "author": "山本 康正", "page": 5},
        {"title": "海外ドラマはたった350の単語でできている", "author": "Cozy", "page": 5},
        {"title": "お金の流れでわかる世界の歴史", "author": "大村 大次郎", "page": 5},
        {"title": "ジェイソン流お金の増やし方", "author": "厚切りジェイソン", "page": 5},
        {"title": "［図解］池上彰の 経済のニュースが面白いほどわかる本", "author": "池上 彰", "page": 5},
        {"title": "世界を変えた10冊の本", "author": "池上 彰", "page": 5},
        {"title": "中国、朝鮮、ベトナム、日本――極東アジアの地政学", "author": "川島 博之", "page": 5},
        {"title": "ビジュアル版 経済・戦争・宗教から見る教養の世界史", "author": "飯田 育浩", "page": 5},
        {"title": "最短の時間で最大の成果を手に入れる 超効率勉強法", "author": "メンタリストＤａｉＧｏ", "page": 5},
        {"title": "ジェームズ・クリアー式 複利で伸びる１つの習慣", "author": "ジェームズ・クリアー", "page": 5},
        {"title": "起きてから寝るまでネコ英語表現", "author": "吉田 研作", "page": 5},
        {"title": "ネイティブがよく使う! 英会話 瞬間返しフレーズ100", "author": "カリン・シールズ", "page": 5},
        
        # ページ6
        {"title": "エネルギーをめぐる旅――文明の歴史と私たちの未来", "author": "古舘 恒介", "page": 6},
    ]
    return books


def parse_kindle_books():
    """Kindle本をパース"""
    books = [
        {"order": 1, "title": "Hajimete no UI design kaiteiban (Japanese Edition)", "author": "Ikeda Takuji; Uno Yu; Kaminogoya Taichi; Tsubota Tomo; Motoyama Kazuyuki; Yoshitake Ryo"},
        {"order": 2, "title": "プロダクトマネジメントのすべて 事業戦略・IT開発・UXデザイン・マーケティングからチーム・組織運営まで (Japanese Edition)", "author": "及川 卓也; 小城 久美子; 曽根原 春樹"},
        {"order": 3, "title": "会計クイズを解くだけで財務３表がわかる 世界一楽しい決算書の読み方 (Japanese Edition)", "author": "大手町のランダムウォーカー"},
        {"order": 4, "title": "コンサル一年目が学ぶこと 新人・就活生からベテラン社員まで一生役立つ究極のベーシックスキル30選 (Japanese Edition)", "author": "大石哲之"},
        {"order": 5, "title": "Hontoni zero karano bokisankyuu FukushimaMasayuki no boki nyuumon (Japanese Edition)", "author": "ふくしままさゆき"},
        {"order": 6, "title": "苦しかったときの話をしようか (Japanese Edition)", "author": "森岡 毅"},
        {"order": 7, "title": "UIデザインの教科書［新版］ マルチデバイス時代のインターフェース設計 (Japanese Edition)", "author": "原田 秀司"},
        {"order": 8, "title": "AI 2041: Ten Visions for Our Future", "author": "Lee, Kai-Fu; Qiufan, Chen"},
        {"order": 9, "title": "UI/UXデザインの原則 (Japanese Edition)", "author": "平石大祐"},
        {"order": 10, "title": "オブジェクト指向UIデザイン──使いやすいソフトウェアの原理 WEB+DB PRESS plus (Japanese Edition)", "author": "ソシオメディア株式会社; 上野 学; 藤井 幸多"},
        {"order": 11, "title": "AI分析でわかった トップ5％社員の習慣 トップ5%シリーズ (Japanese Edition)", "author": "越川慎司"},
        {"order": 12, "title": "はじめてのUXリサーチ ユーザーとともに価値あるサービスを作り続けるために (Japanese Edition)", "author": "松薗 美帆; 草野 孔希"},
        {"order": 13, "title": "なぜか好かれる人がやっている100の習慣 (Japanese Edition)", "author": "藤本 梨恵子"},
        {"order": 14, "title": "Build: An Unorthodox Guide to Making Things Worth Making", "author": "Fadell, Tony"},
        {"order": 15, "title": "イシューからはじめよ――知的生産の「シンプルな本質」 (Japanese Edition)", "author": "安宅和人"},
        {"order": 16, "title": "人間中心設計入門 HCDライブラリー0巻 (Japanese Edition)", "author": "山崎 和彦; 松原 幸行; 竹内 公啓"},
        {"order": 17, "title": "システムを作らせる技術 エンジニアではないあなたへ (日本経済新聞出版) (Japanese Edition)", "author": "白川克; 濵本佳史"},
        {"order": 18, "title": "なるほどデザイン (Japanese Edition)", "author": "筒井 美希"},
        {"order": 19, "title": "イノベーション・スキルセット～世界が求めるBTC型人材とその手引き (Japanese Edition)", "author": "田川欣哉"},
        {"order": 20, "title": "First database design: E-R Diagram Creation (Japanese Edition)", "author": "Tatsuya Matsuda"},
        {"order": 21, "title": "メタ思考トレーニング 発想力が飛躍的にアップする34問 PHPビジネス新書 (Japanese Edition)", "author": "細谷 功"},
        {"order": 22, "title": "未来に先回りする思考法 (Japanese Edition)", "author": "佐藤航陽"},
        {"order": 23, "title": "コンサルを超える 問題解決と価値創造の全技法 (Japanese Edition)", "author": "名和高司"},
        {"order": 24, "title": "ちいさくはじめるデザインシステム (Japanese Edition)", "author": "大塚 亜周; 稲葉 志奈; 金森 悠; samemaru; 圓山 伊吹; 植田 将基; 関口 裕; 8chari; 後藤 拓也; 小木曽 槙一; 桝田 草一"},
        {"order": 25, "title": "データ と デザイン 人とデータのつなぎかた (Japanese Edition)", "author": "櫻井 稔"},
        {"order": 26, "title": "デザイン、学びのしくみ ニューヨークの美大講師が考える創造力の伸ばし方 (Japanese Edition)", "author": "遠藤 大輔"},
        {"order": 27, "title": "融けるデザイン ハード×ソフト×ネット時代の新たな設計論 (Japanese Edition)", "author": "渡邊 恵太"},
        {"order": 28, "title": "お金のむこうに人がいる――元ゴールドマン・サックス金利トレーダーが書いた 予備知識のいらない経済新入門 (Japanese Edition)", "author": "田内 学"},
        {"order": 29, "title": "仕事が速い人は、「これ」しかやらない ラクして速く成果を出す「7つの原則」 (Japanese Edition)", "author": "石川 和男"},
        {"order": 30, "title": "図解 コンサル一年目が学ぶこと (Japanese Edition)", "author": "大石哲之"},
        {"order": 31, "title": "単純な脳、複雑な「私」 (ブルーバックス) (Japanese Edition)", "author": "池谷裕二"},
        {"order": 32, "title": "意識の脳科学 「デジタル不老不死」の扉を開く (講談社現代新書) (Japanese Edition)", "author": "渡辺正峰"},
        {"order": 33, "title": "未来を築くデザインの思想 ―ポスト人間中心デザインへ向けて読むべき24のテキスト (Japanese Edition)", "author": "ヘレン・アームストロング"},
        {"order": 34, "title": "夢を叶えるために脳はある 「私という現象」、高校生と脳を語り尽くす (Japanese Edition)", "author": "池谷裕二"},
        {"order": 35, "title": "データ視覚化の人類史――グラフの発明から時間と空間の可視化まで (Japanese Edition)", "author": "マイケル フレンドリー; ハワード ウェイナー"},
        {"order": 36, "title": "データ視覚化のデザイン (Japanese Edition)", "author": "永田 ゆかり"},
        {"order": 37, "title": "データ可視化の基本が全部わかる本 収集・変換からビジュアライゼーション・データ分析支援まで (Japanese Edition)", "author": "矢崎 裕一"},
        {"order": 38, "title": "ABOUT FACE インタラクションデザインの本質 (Japanese Edition)", "author": "Alan Cooper; Robert Reimann; David Cronin; Christopher Noessel"},
        {"order": 39, "title": "The Elements of User Experience[固定版]: 5段階モデルで考えるUXデザイン (Japanese Edition)", "author": "Jesse James Garrett; ジェシー・ジェームズ・ギャレット"},
        {"order": 40, "title": "生物から見た世界 (岩波文庫) (Japanese Edition)", "author": "ユクスキュル; クリサート; 日高 敏隆; 羽田 節子"},
        {"order": 41, "title": "ChoZyouhouSyakaiNiOkeruSabaibaruZyutu Iihito Senryaku (Japanese Edition)", "author": "Toshio Okada FREEex"},
        {"order": 42, "title": "植物はそこまで知っている 感覚に満ちた世界に生きる植物たち (河出文庫) (Japanese Edition)", "author": "ダニエル・チャモヴィッツ"},
        {"order": 43, "title": "問い続ける力 (ちくま新書) (Japanese Edition)", "author": "石川善樹"},
        {"order": 44, "title": "「風の谷」という希望――残すに値する未来をつくる (Japanese Edition)", "author": "安宅和人"},
    ]
    return books


def main():
    """メイン処理"""
    print("=" * 80)
    print("📚 書籍データベース インポート開始")
    print("=" * 80)
    
    with BookDatabase() as db:
        # データベース初期化
        db.initialize_database()
        
        # Audible完了した本をインポート
        print("\n📘 Audible完了した本をインポート中...")
        completed_books = parse_audible_completed()
        for book in completed_books:
            db.add_book(
                title=book["title"],
                author=book["author"],
                source="Audible",
                status="completed"
            )
        print(f"  ✅ {len(completed_books)}冊をインポートしました")
        
        # Audible進行中の本をインポート
        print("\n📗 Audible進行中の本をインポート中...")
        in_progress_books = parse_audible_in_progress()
        for book in in_progress_books:
            db.add_book(
                title=book["title"],
                author=book["author"],
                source="Audible",
                status="in_progress",
                remaining_time=book.get("remaining_time"),
                page_number=book.get("page")
            )
        print(f"  ✅ {len(in_progress_books)}冊をインポートしました")
        
        # Audible未聴取の本をインポート
        print("\n📙 Audible未聴取の本をインポート中...")
        not_started_books = parse_audible_not_started()
        for book in not_started_books:
            db.add_book(
                title=book["title"],
                author=book["author"],
                source="Audible",
                status="not_started",
                page_number=book.get("page")
            )
        print(f"  ✅ {len(not_started_books)}冊をインポートしました")
        
        # Kindle本をインポート
        print("\n📕 Kindle本をインポート中...")
        kindle_books = parse_kindle_books()
        for book in kindle_books:
            db.add_book(
                title=book["title"],
                author=book["author"],
                source="Kindle",
                status="purchased",
                purchase_order=book["order"]
            )
        print(f"  ✅ {len(kindle_books)}冊をインポートしました")
        
        # 統計表示
        print("\n" + "=" * 80)
        print("📊 インポート完了 - 統計情報")
        print("=" * 80)
        stats = db.get_statistics()
        for stat in stats:
            status_jp = {
                'completed': '完了',
                'in_progress': '進行中',
                'not_started': '未聴取',
                'purchased': '購入済み'
            }.get(stat['status'], stat['status'])
            print(f"  {stat['source']:10s} - {status_jp:10s}: {stat['count']:3d}冊")
        
        # 合計
        total = sum(stat['count'] for stat in stats)
        print(f"\n  {'合計':23s}: {total:3d}冊")
        
        print("\n✅ 全てのデータをインポートしました！")
        print(f"📁 データベース: {db.db_path}")


if __name__ == "__main__":
    main()

