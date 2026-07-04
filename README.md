# Proyek Analisis Data Penjualan — Associate Data Analyst

Proyek ini menjawab studi kasus "Soal Pratik Skema Analis Data Muda" menggunakan dataset
`dataset_penjualan_kotor.csv`.

## Isi Folder

```
├── data/
│   └── dataset_penjualan_kotor.csv     # dataset mentah
├── output/
│   ├── dataset_penjualan_bersih.csv    # hasil cleaning dari notebook
│   └── chart1..5_*.png                 # chart hasil ekspor notebook
├── analisis_penjualan.ipynb            # notebook lengkap: cleaning, EDA, visualisasi, insight
├── dashboard_streamlit.py              # dashboard interaktif (Streamlit)
├── requirements.txt
└── README.md
```

## Cara Menjalankan

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Menjalankan Notebook (analisis lengkap)
```bash
jupyter notebook analisis_penjualan.ipynb
```
Notebook berisi:
- Data understanding (struktur, tipe data, kualitas data)
- Data cleaning (duplikasi, missing value, format tanggal campuran `YYYY-MM-DD` vs `DD-MM-YYYY`)
- Feature engineering (kolom bulan/tahun)
- 5 produk terlaris, ringkasan wilayah, tren bulanan per produk, dan analisis tambahan (AOV & produk favorit per wilayah)
- 5 visualisasi (bar chart, line chart, heatmap)
- Kesimpulan insight & rekomendasi

### 3. Menjalankan Dashboard Streamlit
```bash
streamlit run dashboard_streamlit.py
```
Dashboard akan otomatis membaca `data/dataset_penjualan_kotor.csv`. Anda juga bisa mengunggah
file CSV lain melalui sidebar. Fitur dashboard:
- KPI cards (total revenue, quantity, jumlah transaksi, AOV)
- Filter interaktif: wilayah, produk, rentang bulan
- 5 chart interaktif (Plotly): top produk, permintaan wilayah, tren bulanan, heatmap produk x wilayah, AOV wilayah
- Tabel data bersih + tombol download CSV
- Ringkasan insight otomatis mengikuti filter yang dipilih

## Catatan Kualitas Data (Data Mentah)
- Terdapat baris duplikat penuh.
- Terdapat `transaction_id` yang sama namun datanya berbeda (indikasi human error input ID).
- Missing value pada kolom `quantity` dan `total_price` (direkonstruksi memakai relasi
  `total_price = quantity x price_per_unit`).
- Format tanggal campuran (`YYYY-MM-DD` dan `DD-MM-YYYY`), diseragamkan menjadi tipe datetime.
