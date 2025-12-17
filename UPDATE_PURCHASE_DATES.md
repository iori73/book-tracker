# 購入日の更新方法

このドキュメントでは、Amazonの注文履歴から購入日情報を取得してデータベースに登録する方法を説明します。

## 📋 現在の状態

購入日が設定されていない本の数を確認するには：

```bash
source venv/bin/activate
python update_purchase_dates.py --list
```

## 🔍 Amazonの注文履歴から購入日を取得する方法

### 方法1: 手動でCSVファイルを作成

1. Amazonの注文履歴ページ（https://www.amazon.co.jp/your-orders）にアクセス
2. 各注文の購入日を確認
3. `purchase_dates.csv`ファイルを作成し、以下の形式で記入：

```csv
title,author,purchase_date
本のタイトル1,著者名1,2021-01-15
本のタイトル2,著者名2,2021-02-20
```

**注意事項：**
- タイトルと著者名は、データベースに登録されているものと完全に一致する必要はありません（部分一致で検索されます）
- 日付は `YYYY-MM-DD` 形式で入力してください
- タイトルや著者名にカンマが含まれる場合は、ダブルクォートで囲んでください

### 方法2: JSONファイルを使用

`purchase_dates.json`ファイルを作成し、以下の形式で記入：

```json
[
  {
    "title": "本のタイトル1",
    "author": "著者名1",
    "purchase_date": "2021-01-15"
  },
  {
    "id": 1,
    "purchase_date": "2021-01-15"
  }
]
```

**IDで指定する場合：**
- 本のIDが分かっている場合は、`id`フィールドを使用できます
- この場合、`title`や`author`は不要です

## 📥 購入日をインポートする

### CSVファイルからインポート

```bash
source venv/bin/activate
python update_purchase_dates.py --csv purchase_dates.csv
```

### JSONファイルからインポート

```bash
source venv/bin/activate
python update_purchase_dates.py --json purchase_dates.json
```

### ドライラン（実際には更新せず、更新予定を確認）

```bash
python update_purchase_dates.py --csv purchase_dates.csv --dry-run
```

## 🖱️ インタラクティブモード

1つずつ手動で購入日を入力する場合：

```bash
source venv/bin/activate
python update_purchase_dates.py --interactive
```

このモードでは：
- 購入日が設定されていない本のリストが表示されます
- 本のIDを入力して、購入日を1つずつ入力できます
- `all`と入力すると、すべての本を順番に更新できます

## 📝 テンプレートファイル

以下のテンプレートファイルを参考にしてください：

- `purchase_dates_template.csv` - CSV形式のテンプレート
- `purchase_dates_template.json` - JSON形式のテンプレート

## ⚠️ 注意事項

1. **セキュリティ**: 認証情報（メールアドレスやパスワード）をスクリプトに直接入力することは推奨されません
2. **データのバックアップ**: 大量のデータを更新する前に、データベースのバックアップを取ることをお勧めします
3. **日付形式**: 日付は必ず `YYYY-MM-DD` 形式（例: `2021-01-15`）で入力してください
4. **部分一致検索**: タイトルや著者名は部分一致で検索されるため、完全に一致する必要はありません

## 🔧 トラブルシューティング

### 本が見つからない場合

- タイトルや著者名のスペルを確認してください
- タイトルに特殊文字が含まれている場合は、エスケープが必要な場合があります
- IDが分かっている場合は、JSON形式でIDを直接指定してください

### 日付が無効と表示される場合

- 日付形式が `YYYY-MM-DD` になっているか確認してください
- 例: `2021-01-15` ✅ | `2021/01/15` ❌ | `01-15-2021` ❌

## 📊 更新結果の確認

更新後、StreamlitアプリまたはWebアプリで購入日カラムが表示されていることを確認してください。

```bash
# Streamlitアプリを起動
streamlit run app.py
```

ブラウザで `http://localhost:8501` にアクセスし、「Books」ページで購入日カラムが表示されていることを確認します。

