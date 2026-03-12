import streamlit as st
import pandas as pd
import plotly.express as px
 
# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="BSI Hyperpersonalization Dashboard", layout="wide")
st.title("🏦 Dashboard BSI: Dynamic Ranking & Hyperpersonalization")
st.markdown("Dashboard ini menampilkan hasil klasifikasi chat nasabah, ranking prioritas produk, insight demografi, dan saran aksi (Action Tag) untuk tim Sales & CS.")
 
# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv("Data_Hyperpersonalization_Algoritma_Dipisah.csv")
    return df
 
df = load_data()
 
# ==========================================
# 1. FILTER INTERAKTIF
# ==========================================
st.subheader("🔍 Filter Data Nasabah")
col_filter1, col_filter2 = st.columns(2)
with col_filter1:
    pilih_kategori = st.multiselect("Filter Kategori Produk:", options=df['kategori_baru'].unique(), default=[])
with col_filter2:
    min_saldo = st.number_input("Filter Minimal Saldo (Rp):", min_value=0, value=0, step=1000000)
 
# Terapkan Filter
df_filtered = df.copy()
if pilih_kategori:
    df_filtered = df_filtered[df_filtered['kategori_baru'].isin(pilih_kategori)]
if min_saldo > 0:
    df_filtered = df_filtered[df_filtered['saldoavg'] >= min_saldo]
 
st.divider()
 
# ==========================================
# 2. TOP METRICS
# ==========================================
avg_saldo_val = df_filtered['saldoavg'].mean()
avg_saldo_str = f"Rp {avg_saldo_val:,.0f}" if pd.notna(avg_saldo_val) else "Rp 0"
 
if not df_filtered.empty:
    top_prioritas = str(df_filtered.sort_values('Priority_Rank')['kategori_baru'].iloc[0])
else:
    top_prioritas = "-"
 
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Percakapan", f"{len(df_filtered)} Chat")
col2.metric("Rata-rata Saldo 💰", avg_saldo_str)  
col3.metric("Top Prioritas Produk", top_prioritas)
col4.metric("Nasabah VIP (>50Jt)", len(df_filtered[df_filtered['saldoavg'] > 50000000]))
col5.metric("Keluhan/Helpdesk", len(df_filtered[df_filtered['kategori_baru'] == 'HELPDESK']))
 
st.divider()
 
# ==========================================
# 3. DEMOGRAFI & MARKET INSIGHTS
# ==========================================
st.subheader("👥 Demografi & Profil Nasabah")
if not df_filtered.empty and 'generation' in df_filtered.columns and 'job' in df_filtered.columns:
    col_demo1, col_demo2 = st.columns(2)
   
    with col_demo1:
        # Pie Chart Generasi
        fig_gen = px.pie(df_filtered, names='generation', title="Distribusi Generasi Nasabah", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_gen, use_container_width=True)
       
    with col_demo2:
        # Pie Chart Profesi (Top 7 + Lainnya)
        job_counts = df_filtered['job'].value_counts()
        top_7_jobs = job_counts.nlargest(7).index # Ambil 7 terbanyak
       
        # Buat dataframe sementara agar yang bukan top 7 menjadi "Lainnya"
        df_job = df_filtered.copy()
        df_job['job_grouped'] = df_job['job'].apply(lambda x: x if x in top_7_jobs else 'Lainnya')
       
        fig_job = px.pie(df_job, names='job_grouped', title="Distribusi Profesi Nasabah (Top 7)", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_job, use_container_width=True)
else:
    st.warning("Data kosong atau kolom 'generation' dan 'job' tidak ditemukan. Pastikan file CSV sudah diperbarui.")
 
st.divider()
 
# ==========================================
# 4. VISUALISASI VOLUME CHART (TREEMAP & BAR)
# ==========================================
st.subheader("📊 Analisis Volume & Prioritas Leads")
if not df_filtered.empty:
    chart_data = df_filtered.groupby(['kategori_baru', 'Priority_Rank']).size().reset_index(name='Jumlah Chat')
   
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        fig_tree = px.treemap(chart_data, path=['kategori_baru'], values='Jumlah Chat', color='Priority_Rank', color_continuous_scale='Reds_r', title="🎯 Peta Prioritas & Volume")
        fig_tree.update_traces(textinfo="label+value", textfont_size=14)
        st.plotly_chart(fig_tree, use_container_width=True)
   
    with col_chart2:
        chart_data_sorted = chart_data.sort_values('Jumlah Chat', ascending=True)
        # Menambahkan data label melalui parameter 'text'
        fig_bar = px.bar(chart_data_sorted, x='Jumlah Chat', y='kategori_baru', text='Jumlah Chat', orientation='h', color='Priority_Rank', color_continuous_scale='Reds_r', title="📈 Volume Leads Terbanyak")
       
        # PERBAIKAN: cliponaxis=False diletakkan di update_traces agar angka label tidak terpotong
        fig_bar.update_traces(textposition='outside', cliponaxis=False, textfont=dict(size=13, color='black', family='Arial Black'))
        fig_bar.update_layout(coloraxis_showscale=False)
       
        st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.warning("Data kosong berdasarkan filter yang dipilih.")
 
st.divider()
 
# ==========================================
# 5. TABEL INTERAKTIF UNTUK TIM SALES/CS
# ==========================================
st.subheader("🎯 Data Nasabah & Action Tag")
kolom_tabel = ['timestamp', 'user id', 'kategori_baru', 'Priority_Rank', 'saldoavg', 'rfm_segment', 'Action_Tag_Hyper']
if 'generation' in df_filtered.columns:
    kolom_tabel.insert(5, 'generation')
if 'job' in df_filtered.columns:
    kolom_tabel.insert(6, 'job')
 
st.dataframe(
    df_filtered[kolom_tabel],
    use_container_width=True,
    height=400
)
 
st.divider()
 
# ==========================================
# 6. DETAIL CHAT NASABAH
# ==========================================
st.subheader("💬 Intip Percakapan Nasabah")
if not df_filtered.empty:
    sample_chat = st.selectbox("Pilih User ID untuk melihat chat aslinya:", options=df_filtered['user id'].unique())
    if sample_chat:
        chat_text = df[df['user id'] == sample_chat]['user input'].iloc[0]
        st.info(f"**Chat Asli dari Nasabah ({sample_chat}):** \n\n {chat_text}")