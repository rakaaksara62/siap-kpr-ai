CUSTOM_CSS = """
<style>
    .main-header {
        font-size: 7rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin-bottom: 0.3rem;
        line-height: 1.1;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 500;
        color: #E2E8F0 !important;
        margin-bottom: 2.2rem;
        line-height: 1.4;
    }
    .passport-box {
        background-color: #f0fdf4;
        border: 2px solid #16a34a;
        padding: 1.5rem;
        border-radius: 12px;
        color: #111827 !important;
    }
    .passport-box h4, .passport-box p, .passport-box strong, .passport-box span {
        color: #111827 !important;
    }
    .warning-box {
        background-color: #fefce8;
        border: 2px solid #ca8a04;
        padding: 1.5rem;
        border-radius: 12px;
        color: #111827 !important;
    }
    .warning-box h4, .warning-box p, .warning-box strong, .warning-box span {
        color: #111827 !important;
    }
    .danger-box {
        background-color: #fef2f2;
        border: 2px solid #dc2626;
        padding: 1.5rem;
        border-radius: 12px;
        color: #111827 !important;
    }
    .danger-box h4, .danger-box p, .danger-box strong, .danger-box span {
        color: #111827 !important;
    }
    /* Paksa semua elemen di dalam stMetric membungkus teks (wrap) dan hilangkan text-overflow ellipsis */
    [data-testid="stMetric"],
    [data-testid="stMetric"] * {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
        word-break: break-word !important;
    }
    [data-testid="stMetricLabel"] {
        white-space: normal !important;
        overflow: visible !important;
        line-height: 1.3 !important;
    }
    [data-testid="stMetricValue"] {
        white-space: normal !important;
        overflow: visible !important;
        line-height: 1.25 !important;
        font-size: 1.6rem !important;
    }
    [data-testid="stMetricDelta"] {
        white-space: normal !important;
        overflow: visible !important;
    }
</style>
"""

DUMMY_FREELANCER = """Tanggal,Keterangan,Tipe,Nominal
2026-08-05,Transfer Klien Desain Web PT Maju,CR,5500000
2026-08-10,Pembayaran SPayLater Tagihan,DR,1250000
2026-08-12,Pembayaran Kredivo Cicilan,DR,950000
2026-08-15,Transfer Klien UI/UX,CR,3500000
2026-08-20,Belanja Kopi & Hiburan,DR,1800000
2026-08-25,Biaya Kos & Listrik,DR,2200000
2026-09-04,Transfer Klien Desain Web PT Maju,CR,5500000
2026-09-10,Pembayaran SPayLater Tagihan,DR,1400000
2026-09-12,Pembayaran Kredivo Cicilan,DR,950000
2026-09-18,Transfer Project Freelance,CR,3000000
2026-09-22,Biaya Kos & Listrik,DR,2200000
2026-09-27,Belanja Online & Makanan,DR,2100000
2026-10-05,Transfer Klien Desain Web PT Maju,CR,5500000
2026-10-10,Pembayaran SPayLater Tagihan,DR,1350000
2026-10-12,Pembayaran Kredivo Cicilan,DR,950000
2026-10-16,Transfer Klien Aplikasi,CR,4000000
2026-10-21,Biaya Kos & Listrik,DR,2200000
2026-10-28,Topup E-Wallet & Gaya Hidup,DR,1900000"""

DUMMY_UMKM = """Tanggal,Keterangan,Tipe,Nominal
2026-08-03,Pencairan Dana Penjualan Shopee/Tokopedia,CR,6200000
2026-08-10,Listrik Air & Internet Rumah,DR,850000
2026-08-15,Setoran Tabungan Rencana DP Rumah,DR,2500000
2026-08-18,Pencairan Dana Penjualan Online,CR,5800000
2026-08-25,Belanja Kebutuhan Pokok & Dapur,DR,3200000
2026-09-02,Pencairan Dana Penjualan Shopee/Tokopedia,CR,6500000
2026-09-10,Listrik Air & Internet Rumah,DR,850000
2026-09-15,Setoran Tabungan Rencana DP Rumah,DR,2500000
2026-09-19,Pencairan Dana Penjualan Online,CR,6000000
2026-09-26,Belanja Kebutuhan Pokok & Dapur,DR,3100000
2026-10-04,Pencairan Dana Penjualan Shopee/Tokopedia,CR,6100000
2026-10-10,Listrik Air & Internet Rumah,DR,900000
2026-10-15,Setoran Tabungan Rencana DP Rumah,DR,2500000
2026-10-20,Pencairan Dana Penjualan Online,CR,6400000
2026-10-25,Belanja Kebutuhan Pokok & Dapur,DR,3300000"""

SYSTEM_PROMPT = """Anda adalah analis kredit KPR perbankan Indonesia untuk aplikasi "SiapKPR AI".
Analisis data mutasi rekening 3 bulan terakhir pekerja informal/freelancer/UMKM.

PANDUAN PERHITUNGAN & TERMINOLOGI PERBANKAN (SANGAT PENTING):
1. PEMASUKAN BERSIH: Hitung total seluruh mutasi kredit (CR) selama 3 bulan, lalu WAJIB DIBAGI 3 untuk menghasilkan rata-rata bulanan (rata_rata_pemasukan_bersih). DILARANG menjumlahkan total 3 bulan tanpa membaginya dengan 3.
2. TERMINOLOGI DBR: Gunakan istilah perbankan Indonesia "DBR (Debt Burden Ratio)" secara konsisten pada seluruh teks penjelasan `red_flags` dan `action_plan_3_bulan`. JANGAN gunakan istilah "DTI", selalu ganti dengan "DBR".
3. DETEKSI CICILAN: Deteksi fasilitas kredit konsumtif atau PayLater (misal: SPayLater, Kredivo, pinjol, kartu kredit) dan kelompokkan ke `detail_cicilan_terdeteksi`.

Keluarkan HANYA format JSON valid sesuai skema berikut tanpa markdown atau teks tambahan:
{
  "ringkasan_bulanan": {
    "rata_rata_pemasukan_bersih": 0,
    "rata_rata_pengeluaran_pokok": 0,
    "rata_rata_gaya_hidup": 0,
    "rata_rata_cicilan_eksisting": 0,
    "rata_rata_tabungan": 0,
    "fluktuasi_pemasukan_persen": 0
  },
  "detail_cicilan_terdeteksi": [
    {"nama_pemberi_pinjaman": "string", "estimasi_tagihan_bulanan": 0}
  ],
  "red_flags": [
    {"jenis": "string", "tingkat_risiko": "Tinggi | Sedang", "penjelasan": "string"}
  ],
  "action_plan_3_bulan": [
    {"judul": "string", "target_rupiah": 0, "deskripsi": "string", "dampak_ke_plafon_kpr": "string"}
  ],
  "rekomendasi_hunian_btn": {
    "produk_kpr_cocok": "string",
    "tipe_hunian_disarankan": "string",
    "catatan_kesiapan_penghuni": "string"
  }
}"""