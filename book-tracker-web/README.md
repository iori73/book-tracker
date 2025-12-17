# 📚 Book Tracker Web - shadcn/ui版

Next.js + TypeScript + shadcn/uiで構築した美しい書籍管理Webアプリケーション

## 🚀 起動方法

### 開発サーバーを起動

```bash
cd /Users/iorikawano/Documents/book-tracker/book-tracker-web
npm run dev
```

ブラウザで以下にアクセス:
```
http://localhost:3000
```

## ✨ 機能

### 📊 ダッシュボード (`/`)
- 統計情報の表示
  - 総冊数、完了率、進行中の本
  - Audible/Kindle別の冊数
- カテゴリTop 10の視覚化
  - プログレスバーでステータスを表示
- クイックリンク

### 📚 本の一覧 (`/books`)
- **高度な検索・フィルタリング**
  - タイトル検索（リアルタイム）
  - 著者検索
  - ソースフィルター（Audible/Kindle）
  - ステータスフィルター
  - カテゴリフィルター

- **本の編集**
  - ステータス変更
  - 残り時間の更新
  - メモの追加・編集
  - リアルタイム反映

### 📂 カテゴリ (`/categories`)
- カテゴリ一覧表示
- カテゴリ別統計
- タブでステータス別表示
  - すべて
  - 完了
  - 進行中
  - 未読
  - 購入済み

## 🎨 技術スタック

- **フレームワーク**: Next.js 15 (App Router)
- **言語**: TypeScript
- **UI**: shadcn/ui
- **スタイリング**: Tailwind CSS
- **データベース**: SQLite (better-sqlite3)
- **アイコン**: Lucide React

## 📁 プロジェクト構造

```
book-tracker-web/
├── app/
│   ├── api/              # APIルート
│   │   ├── books/       # 本のCRUD
│   │   ├── stats/       # 統計
│   │   └── categories/  # カテゴリ
│   ├── books/           # 本の一覧ページ
│   ├── categories/      # カテゴリページ
│   ├── page.tsx         # ダッシュボード
│   └── layout.tsx       # レイアウト
├── components/
│   └── ui/              # shadcn/uiコンポーネント
├── lib/
│   ├── db.ts            # データベースアクセス層
│   └── utils.ts         # ユーティリティ
└── public/              # 静的ファイル
```

## 🔌 API エンドポイント

### GET `/api/books`
本を検索・取得

**クエリパラメータ:**
- `source`: Audible | Kindle
- `status`: completed | in_progress | not_started | purchased
- `title`: タイトル検索
- `author`: 著者検索
- `category`: カテゴリ

### GET `/api/books/[id]`
特定の本を取得

### PATCH `/api/books/[id]`
本を更新

**ボディ:**
```json
{
  "status": "completed",
  "remaining_time": "5時間 30分",
  "notes": "とても面白い！"
}
```

### GET `/api/stats`
統計情報を取得

**レスポンス:**
```json
{
  "stats": [...],
  "categories": [...]
}
```

### GET `/api/categories`
カテゴリ一覧を取得

## 🎯 使い方

### 1. 本を探す
1. 「📚 本の一覧」に移動
2. 検索フィルターで条件を指定
3. 結果が自動的に表示される

### 2. 本を編集する
1. 本のカードの「編集」ボタンをクリック
2. ダイアログでステータス、残り時間、メモを編集
3. 「保存」ボタンをクリック

### 3. カテゴリで探す
1. 「📂 カテゴリ」に移動
2. 左側のカテゴリリストから選択
3. タブでステータス別に表示

## 🛠️ 開発

### 依存関係のインストール

```bash
npm install
```

### ビルド

```bash
npm run build
```

### 本番環境で起動

```bash
npm start
```

## 📝 shadcn/uiコンポーネント

使用しているコンポーネント:
- `button` - ボタン
- `card` - カード
- `input` - 入力フィールド
- `label` - ラベル
- `select` - セレクトボックス
- `table` - テーブル
- `tabs` - タブ
- `dialog` - ダイアログ/モーダル
- `badge` - バッジ
- `textarea` - テキストエリア
- `dropdown-menu` - ドロップダウンメニュー

### 新しいコンポーネントを追加

```bash
npx shadcn@latest add <component-name>
```

## 🎨 カスタマイズ

### テーマの変更

`app/globals.css`でCSSカスタムプロパティを編集:

```css
:root {
  --primary: ...;
  --secondary: ...;
  /* ... */
}
```

### ダークモード

shadcn/uiはデフォルトでダークモードに対応しています。
`next-themes`を追加することで切り替えが可能です。

## 🚧 今後の機能追加予定

- [ ] Audible/Kindleからの自動同期
- [ ] 読書時間トラッキング
- [ ] 読書目標の設定
- [ ] レビュー・評価機能
- [ ] グラフの追加（Chart.js/Recharts）
- [ ] モバイルアプリ風のPWA対応
- [ ] データのエクスポート（CSV/JSON）

## 📄 ライセンス

MIT License

---

**shadcn/uiで美しく、Next.jsで高速な書籍管理アプリ！📚✨**
