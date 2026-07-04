"""
Dashboard Analisis Penjualan — Streamlit App
=============================================
Menjalankan:
    streamlit run dashboard_streamlit.py

Pastikan file dataset_penjualan_kotor.csv berada di folder yang sama,
atau upload file melalui sidebar saat aplikasi berjalan.
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import os

# -----------------------------------------------------------------------
# KONFIGURASI HALAMAN
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Analisis Penjualan",
    page_icon="📊",
    layout="wide",
)

# -----------------------------------------------------------------------
# FUNGSI: LOAD & CLEAN DATA
# -----------------------------------------------------------------------
@st.cache_data
def load_and_clean(file) -> pd.DataFrame:
    df = pd.read_csv(file)

    # 1. Hapus duplikasi penuh
    df = df.drop_duplicates()

    # 2. Perbaiki format tanggal campuran (YYYY-MM-DD & DD-MM-YYYY)
    def parse_mixed_date(x):
        x = str(x).strip()
        for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
            try:
                return pd.to_datetime(x, format=fmt)
            except ValueError:
                continue
        return pd.NaT

    df["date"] = df["date"].apply(parse_mixed_date)

    # 3. Rekonsiliasi missing value quantity / total_price
    mask_qty_missing = df["quantity"].isna() & df["total_price"].notna()
    df.loc[mask_qty_missing, "quantity"] = (
        df.loc[mask_qty_missing, "total_price"] / df.loc[mask_qty_missing, "price_per_unit"]
    ).round()

    mask_total_missing = df["total_price"].isna() & df["quantity"].notna()
    df.loc[mask_total_missing, "total_price"] = (
        df.loc[mask_total_missing, "quantity"] * df.loc[mask_total_missing, "price_per_unit"]
    )

    df = df.dropna(subset=["quantity", "total_price", "date"])
    df["quantity"] = df["quantity"].astype(int)

    # 4. Feature engineering
    df = df.reset_index(drop=True)
    df.insert(0, "row_id", df.index + 1)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%b")
    df["year_month"] = df["date"].dt.to_period("M").astype(str)

    return df


# -----------------------------------------------------------------------
# SIDEBAR: SUMBER DATA & FILTER
# -----------------------------------------------------------------------
st.sidebar.title("⚙️ Pengaturan Dashboard")

default_path = "data/dataset_penjualan_kotor.csv"
uploaded_file = st.sidebar.file_uploader("Upload dataset CSV (opsional)", type=["csv"])

if uploaded_file is not None:
    df = load_and_clean(uploaded_file)
elif os.path.exists(default_path):
    df = load_and_clean(default_path)
elif os.path.exists("dataset_penjualan_kotor.csv"):
    df = load_and_clean("dataset_penjualan_kotor.csv")
else:
    st.sidebar.warning("Silakan upload file dataset_penjualan_kotor.csv")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filter Data")

regions = sorted(df["region_name"].unique().tolist())
products = sorted(df["product_name"].unique().tolist())
months = sorted(df["year_month"].unique().tolist())

selected_regions = st.sidebar.multiselect("Wilayah", regions, default=regions)
selected_products = st.sidebar.multiselect("Produk", products, default=products)
selected_months = st.sidebar.select_slider(
    "Rentang Bulan",
    options=months,
    value=(months[0], months[-1]),
)

df_filtered = df[
    (df["region_name"].isin(selected_regions))
    & (df["product_name"].isin(selected_products))
    & (df["year_month"] >= selected_months[0])
    & (df["year_month"] <= selected_months[1])
]

if df_filtered.empty:
    st.warning("Tidak ada data untuk kombinasi filter ini. Silakan ubah filter di sidebar.")
    st.stop()

# -----------------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------------
st.title("📊 Dashboard Analisis Penjualan")
st.caption("Total penjualan per produk, wilayah, dan bulan — data telah dibersihkan otomatis (duplikasi, missing value, format tanggal).")

# -----------------------------------------------------------------------
# KPI CARDS
# -----------------------------------------------------------------------
total_revenue = df_filtered["total_price"].sum()
total_qty = df_filtered["quantity"].sum()
total_transaksi = df_filtered.shape[0]
aov = total_revenue / total_transaksi if total_transaksi else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"Rp {total_revenue:,.0f}")
col2.metric("📦 Total Quantity Terjual", f"{total_qty:,.0f}")
col3.metric("🧾 Jumlah Transaksi", f"{total_transaksi:,.0f}")
col4.metric("💳 Rata-rata Nilai Transaksi (AOV)", f"Rp {aov:,.0f}")

st.markdown("---")

# -----------------------------------------------------------------------
# ROW 1: TOP 5 PRODUK & PERMINTAAN WILAYAH
# -----------------------------------------------------------------------
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("🏆 5 Produk dengan Penjualan Tertinggi")
    top5 = (
        df_filtered.groupby("product_name")["total_price"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )
    fig1 = px.bar(
        top5,
        x="total_price",
        y="product_name",
        orientation="h",
        text="total_price",
        color="total_price",
        color_continuous_scale="Blues",
        labels={"total_price": "Total Revenue (Rp)", "product_name": "Produk"},
    )
    fig1.update_traces(texttemplate="Rp %{text:,.0f}", textposition="outside")
    fig1.update_layout(yaxis=dict(categoryorder="total ascending"), coloraxis_showscale=False)
    st.plotly_chart(fig1, use_container_width=True)

with row1_col2:
    st.subheader("🌍 Permintaan (Quantity) per Wilayah")
    wilayah = (
        df_filtered.groupby("region_name")
        .agg(total_quantity=("quantity", "sum"), total_revenue=("total_price", "sum"))
        .sort_values("total_quantity", ascending=False)
        .reset_index()
    )
    fig2 = px.bar(
        wilayah,
        x="region_name",
        y="total_quantity",
        text="total_quantity",
        color="total_quantity",
        color_continuous_scale="Greens",
        labels={"total_quantity": "Total Quantity", "region_name": "Wilayah"},
    )
    fig2.update_traces(textposition="outside")
    fig2.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------------------------------------------
# ROW 2: TREN BULANAN
# -----------------------------------------------------------------------
st.subheader("📈 Tren Penjualan Bulanan per Produk")
tren = (
    df_filtered.groupby(["year_month", "product_name"])["total_price"]
    .sum()
    .reset_index()
    .sort_values("year_month")
)
fig3 = px.line(
    tren,
    x="year_month",
    y="total_price",
    color="product_name",
    markers=True,
    labels={"total_price": "Total Revenue (Rp)", "year_month": "Bulan", "product_name": "Produk"},
)
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------------------------------------------------
# ROW 3: HEATMAP & AOV WILAYAH
# -----------------------------------------------------------------------
row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.subheader("🔥 Heatmap Revenue: Produk x Wilayah")
    heatmap_data = df_filtered.pivot_table(
        index="product_name", columns="region_name", values="total_price", aggfunc="sum", fill_value=0
    )
    fig4 = px.imshow(
        heatmap_data,
        text_auto=".2s",
        color_continuous_scale="YlOrRd",
        labels=dict(x="Wilayah", y="Produk", color="Revenue"),
    )
    st.plotly_chart(fig4, use_container_width=True)

with row3_col2:
    st.subheader("💳 Rata-rata Nilai Transaksi (AOV) per Wilayah")
    aov_wilayah = (
        df_filtered.groupby("region_name")["total_price"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"total_price": "avg_order_value"})
    )
    fig5 = px.bar(
        aov_wilayah,
        x="region_name",
        y="avg_order_value",
        text="avg_order_value",
        color="avg_order_value",
        color_continuous_scale="Purples",
        labels={"avg_order_value": "AOV (Rp)", "region_name": "Wilayah"},
    )
    fig5.update_traces(texttemplate="Rp %{text:,.0f}", textposition="outside")
    fig5.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# -----------------------------------------------------------------------
# TABEL DATA & INSIGHT
# -----------------------------------------------------------------------
with st.expander("📋 Lihat Data Bersih (hasil cleaning)"):
    st.dataframe(df_filtered, use_container_width=True)
    csv_download = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Data Bersih (CSV)",
        data=csv_download,
        file_name="dataset_penjualan_bersih.csv",
        mime="text/csv",
    )

st.subheader("💡 Kesimpulan Insight")
st.markdown(f"""
- Produk dengan revenue tertinggi saat ini adalah **{top5.iloc[0]['product_name']}**, menyumbang
  **Rp {top5.iloc[0]['total_price']:,.0f}** dari total revenue pada filter yang dipilih.
- Wilayah dengan permintaan (quantity) tertinggi adalah **{wilayah.iloc[0]['region_name']}**
  dengan total **{wilayah.iloc[0]['total_quantity']:,.0f} unit** terjual.
- Wilayah dengan rata-rata nilai transaksi (AOV) tertinggi adalah **{aov_wilayah.iloc[0]['region_name']}**
  sebesar **Rp {aov_wilayah.iloc[0]['avg_order_value']:,.0f}** per transaksi — berpotensi untuk strategi
  bundling/upsell, dibanding wilayah dengan AOV rendah yang lebih cocok didekati dengan strategi volume.
- Gunakan filter di sidebar untuk mengeksplorasi tren per wilayah/produk/bulan tertentu secara lebih spesifik.
""")

st.caption("Dashboard ini otomatis membersihkan data mentah (duplikasi, missing value, format tanggal campuran) setiap kali dataset diunggah/diganti.")
