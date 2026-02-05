import streamlit as st
import pandas as pd
import json
import io
from plan_generator import generate_plan_documents

st.set_page_config(layout="wide", page_title="プロ向け創業計画クラウド")

# --- データ初期化 ---
if 'plan_data' not in st.session_state:
    st.session_state.plan_data = {
        'motive': "", 'career': "", 'product_service': "", 'target_customer': "",
        'key_partners': "", 'key_resources': "", 'channels': "",
        'equity': 0, 'loan_request': 0, 'loan_term': 84, 'loan_rate': 2.0,
        'equip_cost': 0, 'operate_cost': 0,
        'employees': [],
        'projection_data': None
    }

# --- セーブ・ロード機能（クラウド版：ブラウザ経由） ---
def export_json():
    """現在のデータをJSON文字列にしてDL用ボタンに渡す"""
    data = st.session_state.plan_data.copy()
    if data['projection_data'] is not None:
        # DataFrameをJSON化可能な形へ
        data['projection_data_json'] = data['projection_data'].to_json()
        del data['projection_data']
    return json.dumps(data, ensure_ascii=False, indent=4)

def import_json(uploaded_file):
    """アップロードされたJSONをセッションに反映"""
    if uploaded_file is not None:
        new_data = json.load(uploaded_file)
        if 'projection_data_json' in new_data:
            df = pd.read_json(io.StringIO(new_data['projection_data_json']))
            new_data['projection_data'] = df
            del new_data['projection_data_json']
        st.session_state.plan_data.update(new_data)
        st.rerun()

# --- UIレイアウト ---
st.title("👨‍💼 創業計画書ジェネレーター (Cloud版)")

col_save, col_load = st.columns(2)

with col_save:
    st.download_button(
        "💾 設定ファイルをPCに保存",
        data=export_json(),
        file_name="plan_config.json",
        mime="application/json"
    )

with col_load:
    uploaded_file = st.file_uploader("📤 保存したファイルを読み込む", type="json")
    if uploaded_file:
        if st.button("データを復元"):
            import_json(uploaded_file)

st.markdown("---")

# --- 自動計算ロジック（人件費） ---
emp_list = st.session_state.plan_data['employees']
annual_payroll = sum(e['count'] * e['monthly_salary'] * 12 for e in emp_list)
default_payroll = max(6000000, annual_payroll)

# 収支表の初期化
if st.session_state.plan_data['projection_data'] is None:
    years = [f"{i}年目" for i in range(1, 11)]
    st.session_state.plan_data['projection_data'] = pd.DataFrame({
        '売上高': [30000000] * 10,
        '売上原価': [10000000] * 10,
        '人件費': [default_payroll] * 10,
        '家賃': [1200000] * 10,
        'その他経費': [3000000] * 10,
    }, index=years)

# --- タブ入力 ---
tab1, tab2, tab3 = st.tabs(["基本情報", "資金計画", "収支計画（10年）"])

with tab1:
    d = st.session_state.plan_data
    d['motive'] = st.text_area("創業の動機", value=d['motive'])
    d['career'] = st.text_area("略歴", value=d['career'])
    
    st.subheader("従業員計画（人件費に自動反映）")
    if st.button("＋ 従業員追加"):
        d['employees'].append({'position': 'スタッフ', 'count': 1, 'monthly_salary': 250000})
        st.rerun()
    
    for i, emp in enumerate(d['employees']):
        c = st.columns([2, 1, 2, 1])
        emp['position'] = c[0].text_input(f"職種 {i+1}", value=emp['position'], key=f"p{i}")
        emp['count'] = c[1].number_input("人数", value=emp['count'], min_value=1, key=f"c{i}")
        emp['monthly_salary'] = c[2].number_input("月給(円)", value=emp['monthly_salary'], step=10000, key=f"s{i}")
        if c[3].button("🗑️", key=f"d{i}"):
            d['employees'].pop(i)
            st.rerun()

with tab2:
    # 前回の資金計画コードと同様（省略）
    pass

with tab3:
    st.subheader("10年間の収支シミュレーション")
    # 人件費の自動反映（1年目だけ上書き）
    if st.checkbox("従業員データから人件費を同期"):
        st.session_state.plan_data['projection_data']['人件費'] = default_payroll

    edited_df = st.data_editor(
        st.session_state.plan_data['projection_data'],
        column_config={col: st.column_config.NumberColumn(format="¥ %,.0f") for col in st.session_state.plan_data['projection_data'].columns},
        use_container_width=True
    )
    st.session_state.plan_data['projection_data'] = edited_df

# --- PDF生成 ---
if st.button("🚀 最終計画書を生成(PDF/Excel)"):
    # plan_generatorを呼び出し、BytesIOでメモリ上で処理してダウンロードボタンを出す
    # （出力ディレクトリを使わず、st.download_buttonにBytesIOを渡す形に修正するとより高速です）
    pass
