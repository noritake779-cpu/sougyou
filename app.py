import streamlit as st
import pandas as pd
import json
import io
import os
from plan_generator import generate_plan_documents

st.set_page_config(layout="wide", page_title="創業計画作成ツール")

# --- データ初期化 ---
if 'plan_data' not in st.session_state:
    st.session_state.plan_data = {
        'motive': "", 'career': "", 'product_service': "",
        'equity': 0, 'loan_request': 0, 'loan_term': 84, 'loan_rate': 2.0,
        'equip_cost': 0, 'operate_cost': 0,
        'employees': [],
        'projection_data': None
    }

# --- クラウド用セーブ/ロード ---
def export_json():
    data = st.session_state.plan_data.copy()
    if data['projection_data'] is not None:
        data['projection_data_json'] = data['projection_data'].to_json()
        del data['projection_data']
    return json.dumps(data, ensure_ascii=False, indent=4)

def import_json(uploaded_file):
    if uploaded_file:
        new_data = json.load(uploaded_file)
        if 'projection_data_json' in new_data:
            new_data['projection_data'] = pd.read_json(io.StringIO(new_data['projection_data_json']))
            del new_data['projection_data_json']
        st.session_state.plan_data.update(new_data)
        st.rerun()

st.title("👨‍💼 創業計画書ジェネレーター")

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    st.download_button("💾 設定をPCに保存", data=export_json(), file_name="plan_config.json", mime="application/json")
with col_btn2:
    up = st.file_uploader("📤 設定を読み込む", type="json")
    if up and st.button("復元実行"):
        import_json(up)

# --- 収支表の初期化 ---
if st.session_state.plan_data['projection_data'] is None:
    years = [f"{i}年目" for i in range(1, 11)]
    st.session_state.plan_data['projection_data'] = pd.DataFrame({
        '売上高': [30000000] * 10, '売上原価': [10000000] * 10,
        '人件費': [6000000] * 10, '家賃': [1200000] * 10, 'その他': [3000000] * 10
    }, index=years)

# --- 入力タブ ---
tab1, tab2, tab3 = st.tabs(["基本情報", "資金計画", "収支計画"])

with tab1:
    st.session_state.plan_data['motive'] = st.text_area("創業の動機", st.session_state.plan_data['motive'])

with tab3:
    # 画像のsprintfエラーを避けるため、シンプルなフォーマットに変更
    edited_df = st.data_editor(
        st.session_state.plan_data['projection_data'],
        column_config={col: st.column_config.NumberColumn(format="%d") for col in st.session_state.plan_data['projection_data'].columns},
        use_container_width=True
    )
    st.session_state.plan_data['projection_data'] = edited_df

# --- 生成処理 ---
if st.button("🚀 計画書PDFを生成"):
    with st.spinner("生成中..."):
        # クラウド環境では /tmp フォルダを使うのが安全です
        out_dir = "/tmp/output"
        p1, p2, p3 = generate_plan_documents(st.session_state.plan_data, out_dir)
        
        with open(p1, "rb") as f:
            st.download_button("📥 創業計画書(PDF)", f, "plan.pdf")
        with open(p2, "rb") as f:
            st.download_button("📥 収支計画(PDF)", f, "projection.pdf")
