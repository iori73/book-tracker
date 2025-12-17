#!/usr/bin/env python3
"""
Book Tracker Web GUI

Streamlitベースの書籍管理Webアプリケーション
(Shadcn UI Style - 機能強化版)
"""

import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db_manager import BookDatabase
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="Book Tracker",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS - shadcn風の微調整 + テーブルなどの視認性向上
st.markdown("""
<style>
    /* 全体のフォントと背景 */
    .stApp {
        background-color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* サイドバーの背景 */
    section[data-testid="stSidebar"] {
        background-color: #f4f4f5;
        border-right: 1px solid #e4e4e7;
    }
    
    /* ヘッダーの調整 */
    h1, h2, h3 {
        color: #09090b;
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    
    /* データフレームのスタイル */
    [data-testid="stDataFrame"] {
        border: 1px solid #e4e4e7;
        border-radius: 0.5rem;
        overflow: hidden;
    }
    
    /* 編集エリアの強調 */
    .edit-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e9ecef;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'refresh' not in st.session_state:
    st.session_state.refresh = 0


def get_status_emoji(status):
    """ステータスの絵文字を取得"""
    emoji_map = {
        'completed': '✅',
        'in_progress': '📗',
        'not_started': '📚',
        'purchased': '📕'
    }
    return emoji_map.get(status, '📖')


def get_status_jp(status):
    """ステータスの日本語を取得"""
    status_map = {
        'completed': '完了',
        'in_progress': '進行中',
        'not_started': '未読',
        'purchased': '購入済み'
    }
    return status_map.get(status, status)


def show_dashboard():
    """ダッシュボードページ"""
    st.title("Dashboard")
    st.markdown("読書の進捗状況と統計データのサマリー")
    st.markdown("---")
    
    with BookDatabase() as db:
        # 統計情報を取得
        stats = db.get_statistics()
        stats_df = pd.DataFrame(stats)
        
        # メトリクス表示 (shadcn UI card)
        total_books = stats_df['count'].sum()
        audible_books = stats_df[stats_df['source'] == 'Audible']['count'].sum()
        kindle_books = stats_df[stats_df['source'] == 'Kindle']['count'].sum()
        completed = stats_df[stats_df['status'] == 'completed']['count'].sum()
        
        cols = st.columns(4)
        with cols[0]:
            ui.metric_card(title="総冊数", content=f"{total_books}", description="登録されている全書籍", key="card1")
        with cols[1]:
            ui.metric_card(title="Audible", content=f"{audible_books}", description="オーディオブック", key="card2")
        with cols[2]:
            ui.metric_card(title="Kindle", content=f"{kindle_books}", description="電子書籍", key="card3")
        with cols[3]:
            completion_rate = (completed / total_books * 100) if total_books > 0 else 0
            ui.metric_card(title="完了率", content=f"{completion_rate:.1f}%", description=f"読了: {completed}冊", key="card4")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # グラフ表示
        col1, col2 = st.columns(2)
        
        with col1:
            ui.card(title="Sources", description="Audible vs Kindle", key="source_card", content=" ")
            # ソース別の円グラフ
            source_stats = stats_df.groupby('source')['count'].sum().reset_index()
            fig_source = px.pie(
                source_stats, 
                values='count', 
                names='source',
                hole=0.4,
                color_discrete_sequence=['#09090b', '#71717a'] # 黒/グレー系でシックに
            )
            fig_source.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
            st.plotly_chart(fig_source, use_container_width=True)
        
        with col2:
            ui.card(title="Status", description="現在の読書状況", key="status_card", content=" ")
            # ステータス別の棒グラフ
            status_stats = stats_df.groupby('status')['count'].sum().reset_index()
            status_stats['status_label'] = status_stats['status'].apply(get_status_jp)
            
            fig_status = px.bar(
                status_stats,
                x='status_label',
                y='count',
                color_discrete_sequence=['#09090b']
            )
            fig_status.update_layout(
                margin=dict(t=0, b=0, l=0, r=0), 
                height=300,
                xaxis_title=None,
                yaxis_title=None,
                plot_bgcolor='white'
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        # カテゴリ統計
        st.subheader("Categories")
        st.markdown("分野別の読書傾向")
        
        cursor = db.conn.execute("""
            SELECT category, total_books, completed, in_progress, not_started, purchased
            FROM categories_summary
            ORDER BY total_books DESC
            LIMIT 10
        """)
        category_stats = pd.DataFrame(
            cursor.fetchall(),
            columns=['Category', 'Total', 'Completed', 'In Progress', 'Not Started', 'Purchased']
        )
        
        st.dataframe(
            category_stats,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Total": st.column_config.ProgressColumn(
                    "Total Books",
                    format="%d",
                    min_value=0,
                    max_value=int(category_stats['Total'].max()),
                )
            }
        )


def show_books():
    """本の一覧・検索ページ"""
    st.title("Books")
    st.markdown("書籍の検索と管理")
    
    with BookDatabase() as db:
        # 検索エリアをカード風に
        with st.container():
            st.markdown("""
                <div style="background-color: #fcfcfc; padding: 1.5rem; border-radius: 0.5rem; border: 1px solid #e4e4e7; margin-bottom: 2rem;">
                    <h4 style="margin-top: 0;">Filters</h4>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                search_query = ui.input(placeholder="Search title or author...", key="search_input")
            
            with col2:
                # カテゴリ一覧を取得
                cursor = db.conn.execute(
                    "SELECT DISTINCT category FROM books WHERE category IS NOT NULL ORDER BY category"
                )
                categories = ["All Categories"] + [row[0] for row in cursor.fetchall()]
                selected_category = st.selectbox("Category", categories, label_visibility="collapsed")

            col3, col4 = st.columns(2)
            with col3:
                source_filter = ui.tabs(options=['All', 'Audible', 'Kindle'], default_value='All', key="source_tabs")
            with col4:
                status_filter = st.selectbox("Status", ["All", "Completed", "In Progress", "Not Started", "Purchased"], label_visibility="collapsed")
        
        # フィルターロジック
        source = None if source_filter == "All" else source_filter
        
        status_map = {
            "Completed": "completed",
            "In Progress": "in_progress",
            "Not Started": "not_started",
            "Purchased": "purchased"
        }
        status = status_map.get(status_filter) if status_filter != "All" else None
        category = None if selected_category == "All Categories" else selected_category
        
        # 検索実行
        books = db.search_books(
            source=source,
            status=status,
            title_search=search_query if search_query else None,
            author_search=search_query if search_query else None,
            category=category
        )
        
        st.info(f"🔍 **{len(books)}** 冊の本が見つかりました")
        
        if books:
            books_df = pd.DataFrame(books)
            
            # テーブル表示用のデータ加工（日本語化と絵文字追加）
            display_df = books_df.copy()
            display_df['status_display'] = display_df['status'].apply(lambda x: f"{get_status_emoji(x)} {get_status_jp(x)}")
            
            st.markdown("##### 編集したい本をリストからクリックして選択してください 👇")
            
            # インタラクティブなデータフレーム表示
            selection = st.dataframe(
                display_df[['id', 'title', 'author', 'source', 'status_display', 'category', 'purchase_date', 'remaining_time']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": st.column_config.NumberColumn("ID", width="small"),
                    "title": st.column_config.TextColumn("タイトル", width="large"),
                    "author": st.column_config.TextColumn("著者"),
                    "source": st.column_config.TextColumn("ソース", width="small"),
                    "status_display": st.column_config.TextColumn("ステータス"),
                    "category": st.column_config.TextColumn("カテゴリ"),
                    "purchase_date": st.column_config.DateColumn("購入日", width="medium", format="YYYY-MM-DD"),
                    "remaining_time": st.column_config.TextColumn("残り時間"),
                },
                on_select="rerun",  # 選択時にリラン
                selection_mode="single-row"  # 単一行選択
            )
            
            # 選択された行のIDを取得
            selected_book_id = None
            if selection.selection.rows:
                selected_index = selection.selection.rows[0]
                selected_book_id = display_df.iloc[selected_index]['id']
            
            st.markdown("---")
            
            if selected_book_id:
                # 選択された本がある場合、編集フォームを表示
                selected_book = display_df[display_df['id'] == selected_book_id].iloc[0]
                
                # 編集フォームをカード風のコンテナに入れる
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #e9ecef;">
                        <h4 style="margin-top: 0;">✏️ 編集: {selected_book['title']}</h4>
                        <p style="color: #666; font-size: 0.9em; margin-bottom: 20px;">著者: {selected_book['author']} | カテゴリ: {selected_book['category']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.form(key=f"edit_form_{selected_book_id}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            # ステータス選択（日本語表示）
                            current_status_jp = get_status_jp(selected_book['status'])
                            status_options_jp = ["完了", "進行中", "未読", "購入済み"]
                            
                            new_status_jp = st.selectbox(
                                "ステータス",
                                status_options_jp,
                                index=status_options_jp.index(current_status_jp) if current_status_jp in status_options_jp else 0
                            )
                            # 日本語から内部コードへ変換
                            reverse_status_map = {
                                "完了": "completed",
                                "進行中": "in_progress",
                                "未読": "not_started",
                                "購入済み": "purchased"
                            }
                            new_status = reverse_status_map[new_status_jp]
                            
                        with c2:
                            new_remaining = st.text_input("残り時間", value=selected_book['remaining_time'] or "")
                        
                        new_notes = st.text_area("メモ", value=selected_book['notes'] or "", height=100)
                        
                        # ボタンは目立つようにprimaryで
                        submit = st.form_submit_button("💾 更新内容を保存", type="primary", use_container_width=True)
                        
                        if submit:
                            updates = {
                                'status': new_status,
                                'remaining_time': new_remaining if new_remaining else None,
                                'notes': new_notes if new_notes else None
                            }
                            db.update_book(selected_book_id, **updates)
                            st.success(f"✅ 「{selected_book['title']}」の情報を更新しました！")
                            st.rerun()
            else:
                # 何も選択されていない場合のメッセージ
                st.info("👆 上のリストから本を選択すると、ここに編集フォームが表示されます。")


def show_categories():
    """カテゴリ別表示ページ"""
    st.title("Categories")
    st.markdown("カテゴリ別の詳細")
    
    with BookDatabase() as db:
        # カテゴリ一覧を取得
        try:
            cursor = db.conn.execute("""
                SELECT category, total_books 
                FROM categories_summary 
                ORDER BY total_books DESC
            """)
            categories = cursor.fetchall()
        except Exception as e:
            st.error(f"エラー: カテゴリの取得に失敗しました: {str(e)}")
            categories = []
        
        cols = st.columns([1, 3])
        
        with cols[0]:
            st.markdown("#### Select Category")
            cat_names = [c[0] for c in categories]
            
            if cat_names:
                selected_cat = st.radio("Category", cat_names, label_visibility="collapsed")
            else:
                st.warning("カテゴリがありません。書籍にカテゴリが設定されていないか、categories_summaryビューが存在しません。")
                selected_cat = None
            
        with cols[1]:
            if selected_cat:
                st.markdown(f"## {selected_cat}")
                
                # そのカテゴリの本を取得
                books = db.search_books(category=selected_cat)
                books_df = pd.DataFrame(books)
                
                # タブ切り替え
                tab_options = ["All", "In Progress", "Not Started", "Completed"]
                active_tab = ui.tabs(options=tab_options, default_value="All", key="cat_tabs")
                
                filtered_df = books_df
                if active_tab == "In Progress":
                    filtered_df = books_df[books_df['status'] == 'in_progress']
                elif active_tab == "Not Started":
                    filtered_df = books_df[books_df['status'].isin(['not_started', 'purchased'])]
                elif active_tab == "Completed":
                    filtered_df = books_df[books_df['status'] == 'completed']
                
                if not filtered_df.empty:
                    for _, book in filtered_df.iterrows():
                        # カード風表示 (HTML/CSS)
                        st.markdown(f"""
                        <div style="border: 1px solid #e4e4e7; border-radius: 0.5rem; padding: 1.25rem; margin-bottom: 0.5rem; background-color: white;">
                            <div style="font-weight: 600; font-size: 1.1em; margin-bottom: 0.25rem; color: #09090b;">{book['title']}</div>
                            <div style="color: #71717a; font-size: 0.9em;">
                                {book['author']} • <span style="background-color: #f4f4f5; padding: 0.1rem 0.4rem; border-radius: 0.25rem; font-size: 0.8em; margin-left: 0.2rem;">{book['source']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if book['remaining_time']:
                            st.markdown(f"""
                            <div style="margin-top: -0.25rem; margin-bottom: 1rem; margin-left: 0.25rem; color: #2563eb; font-size: 0.9em; display: flex; align-items: center; gap: 0.25rem;">
                                ⏱ Remaining: {book['remaining_time']}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info(f"No books found in {active_tab}")
            else:
                st.info("カテゴリを選択してください")


def main():
    """メイン関数"""
    
    with st.sidebar:
        st.title("📚 Book Tracker")
        
        # ナビゲーション
        nav_options = ["Dashboard", "Books", "Categories"]
        page = st.radio("Navigation", nav_options, label_visibility="collapsed")
        
        st.markdown("---")
        
        # 簡易統計
        with BookDatabase() as db:
            stats = db.get_statistics()
            total = sum(s['count'] for s in stats)
            in_progress = sum(s['count'] for s in stats if s['status'] == 'in_progress')
            
            ui.metric_card(title="Total", content=f"{total}", key="side_total")
            ui.metric_card(title="Reading", content=f"{in_progress}", key="side_reading")

        if ui.button("Refresh Data", key="refresh_btn"):
            st.rerun()

    if page == "Dashboard":
        show_dashboard()
    elif page == "Books":
        show_books()
    elif page == "Categories":
        show_categories()


if __name__ == "__main__":
    main()
