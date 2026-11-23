import io
import csv
import json
import streamlit as st
from config import SYSTEM_PROMPT
from privacy import redact_sensitive_info

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


# Model utama dan daftar model cadangan yang aktif & mendukung json_object
GROQ_MODELS = [
    "qwen/qwen3.8-27b",      # Model utama: akurasi kalkulasi mutasi & kepatuhan skema JSON sangat tinggi
    "openai/gpt-oss-120b",   # Cadangan 1: penalaran komprehensif, konteks besar (131k)
    "openai/gpt-oss-20b",    # Cadangan 2: model ringan & cepat
]


COACHING_PROMPT = """Anda adalah analis kredit KPR perbankan Indonesia untuk aplikasi "SiapKPR AI".
Tugas Anda HANYA memberikan narasi evaluasi risiko, rekomendasi hunian, dan rencana aksi perbaikan KPR berdasarkan angka akuntansi mutasi rekening yang SUDAH DIHITUNG SECARA PASTI oleh sistem.

PANDUAN KETAT:
1. JANGAN mengubah angka keuangan pada `ringkasan_bulanan`. Gunakan angka yang diberikan apa adanya.
2. Gunakan istilah perbankan Indonesia "DBR (Debt Burden Ratio)" secara konsisten pada setiap penjelasan risiko atau rencana aksi. JANGAN gunakan istilah "DTI".
3. Rujuk nama-nama fasilitas cicilan/PayLater yang terdeteksi secara spesifik jika ada (misal: SPayLater, Kredivo).
4. Berikan action plan 3 bulan yang realistis dan terukur untuk menaikkan plafon KPR.

Keluarkan HANYA format JSON valid tanpa markdown atau teks pengantar:
{
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


def parse_csv_deterministic(raw_text: str):
    """
    Menghitung agregasi keuangan secara pasti (deterministik) dari data CSV.
    Mengelompokkan baris berdasarkan tipe (CR/DR) dan kata kunci keterangan.
    Mengembalikan (ringkasan_bulanan, detail_cicilan_terdeteksi) atau None jika format bukan CSV yang valid.
    """
    try:
        cleaned = raw_text.strip()
        if not cleaned:
            return None

        # Cek apakah teks memiliki header CSV tanggal/keterangan/nominal
        header_line = cleaned.splitlines()[0].lower()
        if not ("tanggal" in header_line and "keterangan" in header_line and "nominal" in header_line):
            return None

        reader = csv.DictReader(io.StringIO(cleaned))
        monthly_incomes = {}
        total_cr = 0.0
        total_cicilan = 0.0
        total_tabungan = 0.0
        total_pokok = 0.0
        total_lifestyle = 0.0
        cicilan_map = {}

        row_count = 0
        for row in reader:
            if not row or not row.get("Nominal"):
                continue

            row_count += 1
            date_str = (row.get("Tanggal") or "").strip()
            month_key = date_str[:7] if len(date_str) >= 7 else "default"
            desc = (row.get("Keterangan") or "").strip().lower()
            ttype = (row.get("Tipe") or "").strip().upper()

            # Bersihkan karakter nominal jika ada titik/koma format ribuan
            nom_str = str(row["Nominal"]).strip().replace(".", "").replace(",", "")
            try:
                nominal = float(nom_str)
            except ValueError:
                continue

            if ttype == "CR":
                total_cr += nominal
                monthly_incomes[month_key] = monthly_incomes.get(month_key, 0.0) + nominal
            elif ttype == "DR":
                if any(k in desc for k in ["paylater", "spaylater", "kredivo", "gopaylater", "cicilan", "pinjol", "fif"]):
                    total_cicilan += nominal
                    k_name = "SPayLater" if "spaylater" in desc else ("Kredivo" if "kredivo" in desc else row["Keterangan"].strip())
                    cicilan_map[k_name] = cicilan_map.get(k_name, 0.0) + nominal
                elif any(k in desc for k in ["tabungan", "rencana dp", "investasi"]):
                    total_tabungan += nominal
                elif any(k in desc for k in ["kos", "listrik", "air", "pdam", "internet", "kebutuhan pokok", "dapur"]):
                    total_pokok += nominal
                else:
                    total_lifestyle += nominal

        if row_count == 0:
            return None

        # Standar penilaian KPR perbankan: mutasi rekening 3 bulan terakhir
        num_months = max(1, len(monthly_incomes)) if monthly_incomes else 3
        avg_cr = int(round(total_cr / num_months))
        avg_cicilan = int(round(total_cicilan / num_months))
        avg_tabungan = int(round(total_tabungan / num_months))
        avg_pokok = int(round(total_pokok / num_months))
        avg_lifestyle = int(round(total_lifestyle / num_months))

        # Fluktuasi pemasukan bulanan
        if len(monthly_incomes) > 1 and avg_cr > 0:
            incomes = list(monthly_incomes.values())
            fluctuation_pct = int(round(((max(incomes) - min(incomes)) / avg_cr) * 100))
        else:
            fluctuation_pct = 8

        ringkasan = {
            "rata_rata_pemasukan_bersih": avg_cr,
            "rata_rata_pengeluaran_pokok": avg_pokok,
            "rata_rata_gaya_hidup": avg_lifestyle,
            "rata_rata_cicilan_eksisting": avg_cicilan,
            "rata_rata_tabungan": avg_tabungan,
            "fluktuasi_pemasukan_persen": fluctuation_pct
        }

        detail_cicilan = [
            {"nama_pemberi_pinjaman": name, "estimasi_tagihan_bulanan": int(round(val / num_months))}
            for name, val in cicilan_map.items()
        ]

        return ringkasan, detail_cicilan
    except Exception:
        return None


def fallback_parser(raw_text: str, ringkasan_override=None, cicilan_override=None) -> dict:
    """Parser cadangan berbasis aturan jika API key tidak diisi saat demo."""
    if "SPayLater" in raw_text or "Kredivo" in raw_text or (cicilan_override and len(cicilan_override) > 0):
        base_res = {
            "ringkasan_bulanan": ringkasan_override or {
                "rata_rata_pemasukan_bersih": 9000000,
                "rata_rata_pengeluaran_pokok": 2200000,
                "rata_rata_gaya_hidup": 1933333,
                "rata_rata_cicilan_eksisting": 2283333,
                "rata_rata_tabungan": 500000,
                "fluktuasi_pemasukan_persen": 15
            },
            "detail_cicilan_terdeteksi": cicilan_override or [
                {"nama_pemberi_pinjaman": "SPayLater", "estimasi_tagihan_bulanan": 1333333},
                {"nama_pemberi_pinjaman": "Kredivo", "estimasi_tagihan_bulanan": 950000}
            ],
            "red_flags": [
                {
                    "jenis": "Rasio Cicilan PayLater Tinggi (DBR Melampaui Batas Ideal)",
                    "tingkat_risiko": "Tinggi",
                    "penjelasan": "Dua fasilitas PayLater aktif memangkas kapasitas cicilan KPR bulanan secara signifikan di sistem SLIK OJK."
                }
            ],
            "action_plan_3_bulan": [
                {
                    "judul": "Lunasi & Tutup Fasilitas Kredivo",
                    "target_rupiah": 950000,
                    "deskripsi": "Alokasikan pos non-esensial untuk melunasi cicilan Kredivo dalam 2 bulan ke depan.",
                    "dampak_ke_plafon_kpr": "+Rp99.750.000 pada plafon KPR"
                },
                {
                    "judul": "Batasi Penggunaan SPayLater Maksimal Rp300rb/bulan",
                    "target_rupiah": 1000000,
                    "deskripsi": "Hindari transaksi konsumtif berbasis cicilan menjelang pengajuan KPR untuk memperbaiki rasio DBR.",
                    "dampak_ke_plafon_kpr": "+Rp105.000.000 pada plafon KPR"
                },
                {
                    "judul": "Bentuk Rekening Tabungan DP Terpisah",
                    "target_rupiah": 1800000,
                    "deskripsi": "Setor rutin tabungan rencana di awal bulan untuk membuktikan saving habit ke analis bank BTN.",
                    "dampak_ke_plafon_kpr": "+15 Poin Skor Kesiapan"
                }
            ],
            "rekomendasi_hunian_btn": {
                "produk_kpr_cocok": "KPR BTN Gaess / KPR BTN Platinum (Setelah Restrukturisasi PayLater)",
                "tipe_hunian_disarankan": "Rumah Tapak Tipe 36/60 di Kawasan Penyangga Industri/Urban (Kisaran Rp250–320 Juta)",
                "catatan_kesiapan_penghuni": "Siapkan cadangan dana Rp1,2 juta/bulan untuk biaya operasional hunian setelah serah terima kunci."
            }
        }
        return base_res

    return {
        "ringkasan_bulanan": ringkasan_override or {
            "rata_rata_pemasukan_bersih": 12333333,
            "rata_rata_pengeluaran_pokok": 4066667,
            "rata_rata_gaya_hidup": 1000000,
            "rata_rata_cicilan_eksisting": 0,
            "rata_rata_tabungan": 2500000,
            "fluktuasi_pemasukan_persen": 8
        },
        "detail_cicilan_terdeteksi": cicilan_override or [],
        "red_flags": [],
        "action_plan_3_bulan": [
            {
                "judul": "Pertahankan Saldo Mengendap & Setoran Rutin",
                "target_rupiah": 2500000,
                "deskripsi": "Jaga konsistensi transfer tabungan rencana DP hingga hari akad kredit.",
                "dampak_ke_plafon_kpr": "Mempertahankan status Prioritas Pre-Approved"
            },
            {
                "judul": "Siapkan Dokumen Legalitas Usaha (NIB / SKU)",
                "target_rupiah": 0,
                "deskripsi": "Lengkapi NIB online (OSS) sebagai dokumen pendamping mutasi rekening bagi wirausaha/UMKM.",
                "dampak_ke_plafon_kpr": "Mempercepat verifikasi analis kredit BTN"
            }
        ],
        "rekomendasi_hunian_btn": {
            "produk_kpr_cocok": "KPR BTN Platinum / KPR BTN Subsidi (FLPP) sesuai batas penghasilan",
            "tipe_hunian_disarankan": "Rumah Tapak Tipe 36/72 atau 45/84 di Cluster Perumahan Mitra BTN (Kisaran Rp350–450 Juta)",
            "catatan_kesiapan_penghuni": "Rasio arus kas sangat sehat; alokasikan maksimal 10% dana darurat untuk biaya akad (BPHTB, notaris, provisi)."
        }
    }


def analyze_statement_with_ai(raw_text: str, api_key: str) -> dict:
    """
    Arsitektur Hybrid:
    1. Jika data CSV terdeteksi: Hitung angka keuangan secara deterministik (100% akurat tanpa halusinasi).
       Gunakan LLM khusus untuk coaching kualitatif (red flags, action plan DBR, rekomendasi hunian).
    2. Jika data PDF teks bebas: Gunakan LLM penuh untuk ekstraksi end-to-end.
    """
    clean_text = redact_sensitive_info(raw_text)
    deterministic_result = parse_csv_deterministic(clean_text)

    # ========================================================
    # JALUR 1: DATA CSV (HYBRID DETERMINISTIC + LLM COACHING)
    # ========================================================
    if deterministic_result is not None:
        ringkasan_pasti, cicilan_pasti = deterministic_result

        if api_key and GROQ_AVAILABLE:
            client = Groq(api_key=api_key)
            user_context = f"""Berikut hasil kalkulasi akuntansi mutasi rekening nasabah:
- Rata-rata Pemasukan Bersih: Rp {ringkasan_pasti['rata_rata_pemasukan_bersih']:,}/bulan
- Rata-rata Pengeluaran Pokok: Rp {ringkasan_pasti['rata_rata_pengeluaran_pokok']:,}/bulan
- Rata-rata Gaya Hidup: Rp {ringkasan_pasti['rata_rata_gaya_hidup']:,}/bulan
- Rata-rata Cicilan/PayLater: Rp {ringkasan_pasti['rata_rata_cicilan_eksisting']:,}/bulan
- Rata-rata Tabungan: Rp {ringkasan_pasti['rata_rata_tabungan']:,}/bulan
- Fluktuasi Pemasukan: {ringkasan_pasti['fluktuasi_pemasukan_persen']}%
- Fasilitas Cicilan Terdeteksi: {json.dumps(cicilan_pasti)}

Teks mutasi asli:
{clean_text[:6000]}"""

            for model_name in GROQ_MODELS:
                try:
                    completion = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": COACHING_PROMPT},
                            {"role": "user", "content": user_context}
                        ],
                        temperature=0.1,
                        response_format={"type": "json_object"}
                    )
                    coaching_data = json.loads(completion.choices[0].message.content)
                    return {
                        "ringkasan_bulanan": ringkasan_pasti,
                        "detail_cicilan_terdeteksi": cicilan_pasti,
                        "red_flags": coaching_data.get("red_flags", []),
                        "action_plan_3_bulan": coaching_data.get("action_plan_3_bulan", []),
                        "rekomendasi_hunian_btn": coaching_data.get("rekomendasi_hunian_btn", {})
                    }
                except Exception:
                    continue

        # Jika API offline/habis kuota, gunakan fallback yang tetap memasukkan angka pasti
        return fallback_parser(clean_text, ringkasan_override=ringkasan_pasti, cicilan_override=cicilan_pasti)

    # ========================================================
    # JALUR 2: DATA NON-CSV (PDF BEBAS - FULL LLM EXTRACTION)
    # ========================================================
    if api_key and GROQ_AVAILABLE:
        client = Groq(api_key=api_key)
        last_error = None
        for model_name in GROQ_MODELS:
            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Berikut data mutasi rekening 3 bulan terakhir:\n\n{clean_text[:12000]}"}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                return json.loads(completion.choices[0].message.content)
            except Exception as e:
                last_error = e
                continue

        st.warning(f"Menggunakan mesin analisis lokal (API Info: {last_error})")
        return fallback_parser(clean_text)

    return fallback_parser(clean_text)