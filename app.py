import os
from datetime import datetime
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from config import CUSTOM_CSS, DUMMY_FREELANCER, DUMMY_UMKM
from privacy import redact_sensitive_info, extract_text_from_file
from scoring_engine import calculate_kpr_score
from ai_parser import analyze_statement_with_ai
from pdf_generator import generate_passport_pdf

# ==========================================
# MUAT VARIABEL ENVIRONMENT (.env / Streamlit Secrets)
# ==========================================
load_dotenv()
DEFAULT_GROQ_KEY = os.getenv("GROQ_API_KEY", "")
# Cek apakah ada di st.secrets (Streamlit Cloud Secrets)
if not DEFAULT_GROQ_KEY and hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
    DEFAULT_GROQ_KEY = st.secrets["GROQ_API_KEY"]

# ==========================================
# FUNGSI FORMAT RUPIAH SINGKAT UNTUK METRIK
# ==========================================
def format_rupiah_singkat(nominal: float) -> str:
    """Format nominal angka menjadi representasi ringkas untuk st.metric agar tidak terpotong (...)."""
    abs_nom = abs(nominal)
    sign = "-" if nominal < 0 else ""
    if abs_nom >= 1_000_000_000:
        val = abs_nom / 1_000_000_000
        return f"{sign}Rp {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " M"
    elif abs_nom >= 1_000_000:
        val = abs_nom / 1_000_000
        return f"{sign}Rp {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " Jt"
    else:
        return f"{sign}Rp {abs_nom:,.0f}".replace(",", ".")


# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="SiapKPR AI | Pre-Underwriting & KPR Readiness Copilot",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==========================================
# SIDEBAR: KONFIGURASI & PROFIL TARGET
# ==========================================
with st.sidebar:
    st.markdown("## 🏠 **SiapKPR AI**")
    st.caption("KPR Readiness & Cash-Flow Underwriting")
    st.markdown("### ⚙️ Pengaturan Mesin AI")

    if DEFAULT_GROQ_KEY:
        groq_api_key = DEFAULT_GROQ_KEY
        st.success("✅ Groq API Key aktif dari server (Cloud Secrets)")
    else:
        groq_api_key = st.text_input(
            "Groq API Key (Opsional untuk Live LLM)",
            type="password",
            help="Jika dikosongkan, aplikasi otomatis menggunakan mesin analisis lokal untuk demo."
        )

    st.divider()
    st.markdown("### 🎯 Target Hunian Pengguna")
    nama_pemohon = st.text_input("Nama Calon Debitur", value="Raka Aksara")
    jenis_pekerjaan = st.selectbox(
        "Profil Pekerjaan",
        ["Freelancer / Pekerja Lepas", "Pelaku UMKM / Pedagang Online", "Konten Kreator / Agensi", "Karyawan Kontrak"]
    )
    harga_rumah_target = st.number_input("Target Harga Rumah (Rp)", min_value=100000000, max_value=2000000000, value=300000000, step=25000000)
    dp_tersedia = st.number_input("Dana DP Terkumpul (Rp)", min_value=0, max_value=1000000000, value=30000000, step=5000000)
    tenor_kpr = st.selectbox(
        "Rencana Tenor KPR",
        [10, 15, 20, 25, 30],
        index=2,
        format_func=lambda x: f"{x} Tahun (Program BTN)"
    )

    st.divider()
    st.caption("🔒 **Kepatuhan UU PDP:** Nomor rekening dan identitas sensitif disensor otomatis (*client-side redaction*) sebelum diproses.")

# ==========================================
# HEADER UTAMA
# ==========================================
st.markdown(
    """
    <div style="margin-bottom: 2rem;">
        <h1 style="font-size: 4.5rem; font-weight: 900; color: #FFFFFF !important; margin-bottom: 0.2rem; line-height: 1.1;">
            🏠 SiapKPR AI
        </h1>
        <p style="font-size: 1.5rem; font-weight: 500; color: #E2E8F0 !important; margin-top: 0; line-height: 1.4;">
            AI KPR Readiness Copilot & Cash-Flow Underwriting untuk Pekerja Informal & Gen Z
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================
# INPUT DATA MUTASI (UPLOAD ATAU DEMO MODE)
# ==========================================
st.markdown("#### Unggah Mutasi Rekening (3 Bulan Terakhir) atau Pilih Mode Demo")
col_up1, col_up2 = st.columns([2, 1])

with col_up1:
    uploaded_file = st.file_uploader("Unggah e-Statement Rekening Koran (PDF atau CSV)", type=["pdf", "csv"])

with col_up2:
    st.markdown("**Mode Demo Cepat (Untuk Pengujian Juri):**")
    demo_choice = st.radio(
        "Pilih Profil Sampel:",
        ["Tidak Ada (Gunakan File Unggahan)", "Profil A: Freelancer (Terkendala PayLater)", "Profil B: UMKM Online (Siap Akad KPR)"],
        index=1
    )

raw_data_text = None
if uploaded_file is not None:
    raw_data_text = extract_text_from_file(uploaded_file)
elif demo_choice == "Profil A: Freelancer (Terkendala PayLater)":
    raw_data_text = DUMMY_FREELANCER
elif demo_choice == "Profil B: UMKM Online (Siap Akad KPR)":
    raw_data_text = DUMMY_UMKM

if raw_data_text:
    with st.expander("🔍 Pratinjau Data Mutasi Terdeteksi (Setelah Sensor Privasi UU PDP)"):
        st.code(redact_sensitive_info(raw_data_text), language="csv")

    if st.button("🚀 Analisis Kelayakan KPR Sekarang", type="primary", use_container_width=True):
        with st.spinner("AI sedang mengklasifikasikan arus kas, mendeteksi kewajiban SLIK/PayLater, dan menghitung rasio DBR..."):
            st.session_state["ai_result"] = analyze_statement_with_ai(raw_data_text, groq_api_key)

# ==========================================
# DASHBOARD HASIL ANALISIS & SIMULATOR
# ==========================================
if "ai_result" in st.session_state:
    res = st.session_state["ai_result"]
    ringkasan = res["ringkasan_bulanan"]

    net_income = ringkasan["rata_rata_pemasukan_bersih"]
    existing_debt = ringkasan["rata_rata_cicilan_eksisting"]
    monthly_savings = ringkasan["rata_rata_tabungan"]
    fluctuation = ringkasan["fluktuasi_pemasukan_persen"]
    red_flags = res.get("red_flags", [])

    scoring = calculate_kpr_score(
        net_income,
        existing_debt,
        monthly_savings,
        fluctuation,
        len(red_flags),
        target_house_price=harga_rumah_target,
        current_dp=dp_tersedia,
        tenor_years=tenor_kpr
    )

    st.divider()
    st.markdown("## 📊 Hasil Analisis *Cash-Flow Underwriting*")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Skor Kesiapan KPR", f"{scoring['total_score']} / 100", scoring["status"])
    m2.metric("Rata-rata Pemasukan", format_rupiah_singkat(net_income), "Per Bulan")
    m3.metric("Rasio Cicilan Eksisting (DBR)", f"{scoring['dbr_existing_pct']}%", "Batas Aman Bank: ≤ 35%", delta_color="inverse")
    m4.metric("Estimasi Plafon KPR Aman", format_rupiah_singkat(scoring['estimated_plafon']), f"Max Cicilan: {format_rupiah_singkat(scoring['max_kpr_installment'])}/bln")

    c_left, c_right = st.columns([1.2, 1])

    with c_left:
        st.markdown("#### Komposisi Arus Kas Bulanan")
        chart_df = pd.DataFrame({
            "Kategori": ["Pemasukan Bersih", "Kebutuhan Pokok", "Gaya Hidup", "Cicilan/PayLater", "Tabungan DP"],
            "Nominal (Rp)": [
                net_income,
                ringkasan["rata_rata_pengeluaran_pokok"],
                ringkasan["rata_rata_gaya_hidup"],
                existing_debt,
                monthly_savings
            ]
        }).set_index("Kategori")
        st.bar_chart(chart_df, color="#00529B")

    with c_right:
        st.markdown("#### Rincian Penilaian Kredit Perbankan")
        st.progress(scoring["breakdown"]["dbr"] / 40, text=f"Kapasitas Utang / DBR ({scoring['breakdown']['dbr']}/40 poin)")
        st.progress(scoring["breakdown"]["consistency"] / 25, text=f"Stabilitas Pemasukan ({scoring['breakdown']['consistency']}/25 poin)")
        st.progress(scoring["breakdown"]["savings"] / 25, text=f"Kesiapan Likuiditas & DP ({scoring['breakdown']['savings']}/25 poin)")
        st.progress(scoring["breakdown"]["cleanliness"] / 10, text=f"Kebersihan Transaksi / Bebas Red Flag ({scoring['breakdown']['cleanliness']}/10 poin)")

        if red_flags:
            st.error("⚠️ **Deteksi Risiko Perbankan (Red Flags):**")
            for rf in red_flags:
                st.write(f"- **{rf['jenis']} ({rf['tingkat_risiko']}):** {rf['penjelasan']}")
        else:
            st.success("✅ **Tidak ditemukan transaksi berisiko tinggi (Red Flag) pada mutasi rekening.**")

    # ==========================================
    # WHAT-IF COACHING SIMULATOR
    # ==========================================
    st.divider()
    st.markdown("## 🎛️ *What-If Simulator*: Simulasi Perbaikan Skor Sebelum Akad")
    st.caption("Geser slider di bawah ini untuk melihat bagaimana pelunasan PayLater atau penambahan tabungan meningkatkan plafon KPR BTN Anda secara instan.")

    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        if existing_debt > 0:
            debt_reduction = st.slider(
                "Kurangi Beban Cicilan / PayLater Bulanan sebesar (Rp):",
                min_value=0,
                max_value=int(existing_debt),
                value=int(existing_debt),
                step=100000 if existing_debt >= 100000 else int(existing_debt)
            )
        else:
            debt_reduction = 0
            st.info("✅ **Beban Utang Rp0:** Nasabah tidak memiliki tanggungan cicilan/PayLater yang perlu dikurangi.")
    with sim_col2:
        extra_savings = st.slider(
            "Tambah Alokasi Tabungan DP Bulanan sebesar (Rp):",
            min_value=0,
            max_value=5000000,
            value=1000000,
            step=250000
        )

    sim_debt = max(0, existing_debt - debt_reduction)
    sim_savings = monthly_savings + extra_savings
    sim_red_flags = 0 if sim_debt == 0 else len(red_flags)
    sim_scoring = calculate_kpr_score(
        net_income,
        sim_debt,
        sim_savings,
        fluctuation,
        sim_red_flags,
        target_house_price=harga_rumah_target,
        current_dp=dp_tersedia,
        tenor_years=tenor_kpr
    )

    diff_installment = sim_scoring['max_kpr_installment'] - scoring['max_kpr_installment']
    diff_plafon = sim_scoring['estimated_plafon'] - scoring['estimated_plafon']
    prefix_inst = "+" if diff_installment >= 0 else ""
    prefix_plaf = "+" if diff_plafon >= 0 else ""

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Proyeksi Skor Baru", f"{sim_scoring['total_score']} / 100", f"{sim_scoring['total_score'] - scoring['total_score']:+d} poin")
    s2.metric(
        "Proyeksi Kapasitas Cicilan KPR",
        f"{format_rupiah_singkat(sim_scoring['max_kpr_installment'])}/bln",
        f"{prefix_inst}{format_rupiah_singkat(diff_installment)}"
    )
    s3.metric(
        "Proyeksi Plafon KPR Baru",
        format_rupiah_singkat(sim_scoring['estimated_plafon']),
        f"{prefix_plaf}{format_rupiah_singkat(diff_plafon)}"
    )
    
    # Metrik percepatan waktu pengumpulan DP rumah
    delta_months = scoring['months_to_ready_dp'] - sim_scoring['months_to_ready_dp']
    time_label = "Siap Sekarang" if sim_scoring['months_to_ready_dp'] == 0 else f"{sim_scoring['months_to_ready_dp']} Bulan"
    delta_label = f"{delta_months} bln lebih cepat" if delta_months > 0 else ("DP Cukup" if sim_scoring['months_to_ready_dp'] == 0 else "Stabil")
    s4.metric("Waktu Kesiapan DP Akad", time_label, delta_label)

    # ==========================================
    # ACTION PLAN & REKOMENDASI HUNIAN BTN
    # ==========================================
    st.divider()
    col_act, col_house = st.columns([1.1, 1])

    with col_act:
        st.markdown("### 📋 Rencana Aksi 3 Bulan (*AI Coaching Plan*)")
        for idx, act in enumerate(res.get("action_plan_3_bulan", []), 1):
            with st.container(border=True):
                st.markdown(f"**{idx}. {act['judul']}**")
                st.write(act["deskripsi"])
                st.caption(f"🎯 Dampak: **{act['dampak_ke_plafon_kpr']}**")

    with col_house:
        st.markdown("### 🏡 Rekomendasi Skema KPR & Hunian BTN")
        rek = res.get("rekomendasi_hunian_btn", {})
        
        status_badge = "🟢" if scoring["total_score"] >= 80 else ("🟡" if scoring["total_score"] >= 60 else "🔴")

        with st.container(border=True):
            st.markdown(f"#### 🎫 KPR Readiness Passport {status_badge}")
            st.markdown(f"**Nama Pemohon:** {nama_pemohon} ({jenis_pekerjaan})")
            st.markdown(f"**Status Kelayakan:** {scoring['status']} (Skor: {scoring['total_score']}/100)")
            st.markdown(f"**Tenor Rencana:** {tenor_kpr} Tahun | **Plafon Aman:** {format_rupiah_singkat(scoring['estimated_plafon'])}")
            st.markdown(f"**Produk KPR Disarankan:** {rek.get('produk_kpr_cocok', '-')}")
            st.markdown(f"**Rekomendasi Tipe Hunian:** {rek.get('tipe_hunian_disarankan', '-')}")
            
            st.divider()
            st.markdown("💰 **Estimasi Rincian Modal Awal (Pra-Akad):**")
            st.caption(
                f"- Uang Muka Minimal (10%): **Rp {scoring['target_dp_needed']:,.0f}**\n"
                f"- Estimasi Biaya Akad (~6% BPHTB, Notaris, Asuransi): **Rp {scoring['est_closing_costs']:,.0f}**\n"
                f"- Total Modal Awal yang Diperlukan: **Rp {scoring['total_upfront_needed']:,.0f}**\n"
                f"- Dana Tersedia Saat Ini: **Rp {dp_tersedia:,.0f}**"
            )
            st.markdown(f"**Catatan Kesiapan Penghuni:** {rek.get('catatan_kesiapan_penghuni', '-')}")

        passport_report = f"""====================================================
SIAPKPR AI - KPR READINESS PASSPORT (RINGKASAN ANALISIS)
====================================================
Tanggal Penerbitan : {datetime.now().strftime('%d %B %Y')}
Nama Calon Debitur : {nama_pemohon}
Profil Pekerjaan   : {jenis_pekerjaan}
Target Harga Rumah : Rp {harga_rumah_target:,.0f}
Rencana Tenor KPR  : {tenor_kpr} Tahun
Dana DP Tersedia   : Rp {dp_tersedia:,.0f}

ESTIMASI KEBUTUHAN MODAL AWAL PRA-AKAD
- Target Minimal DP (10%)    : Rp {scoring['target_dp_needed']:,.0f}
- Estimasi Biaya Akad (~6%)  : Rp {scoring['est_closing_costs']:,.0f} (Pajak BPHTB, AJB/Notaris, Asuransi)
- Total Modal Awal Wajib     : Rp {scoring['total_upfront_needed']:,.0f}

HASIL CASH-FLOW UNDERWRITING (3 BULAN TERAKHIR)
- Skor Kesiapan KPR          : {scoring['total_score']} / 100 ({scoring['status']})
- Rata-rata Pemasukan Bersih : Rp {net_income:,.0f} / bulan
- Beban Cicilan Eksisting    : Rp {existing_debt:,.0f} / bulan (DBR: {scoring['dbr_existing_pct']}%)
- Kapasitas Cicilan KPR Aman : Rp {scoring['max_kpr_installment']:,.0f} / bulan
- Estimasi Plafon KPR BTN    : Rp {scoring['estimated_plafon']:,.0f}

REKOMENDASI EKOSISTEM HUNIAN BTN
- Produk KPR Cocok           : {rek.get('produk_kpr_cocok', '-')}
- Tipe Hunian Disarankan     : {rek.get('tipe_hunian_disarankan', '-')}
- Kesiapan Biaya Penghuni    : {rek.get('catatan_kesiapan_penghuni', '-')}
====================================================
Dokumen ini dihasilkan oleh SiapKPR AI sebagai instrumen 
pre-underwriting mandiri sebelum pengajuan resmi ke Bank BTN.
"""
        # Generate PDF resmi
        pdf_bytes = generate_passport_pdf(
            nama_pemohon=nama_pemohon,
            jenis_pekerjaan=jenis_pekerjaan,
            harga_rumah_target=harga_rumah_target,
            dp_tersedia=dp_tersedia,
            tenor_kpr=tenor_kpr,
            scoring=scoring,
            net_income=net_income,
            existing_debt=existing_debt,
            rek=rek
        )

        col_dl1, col_dl2 = st.columns([1.2, 1])
        with col_dl1:
            st.download_button(
                label="📄 Unduh KPR Readiness Passport (PDF Resmi)",
                data=pdf_bytes,
                file_name=f"KPR_Passport_{nama_pemohon.replace(' ', '_')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        with col_dl2:
            st.download_button(
                label="📝 Unduh Ringkasan (.txt)",
                data=passport_report,
                file_name=f"KPR_Readiness_Passport_{nama_pemohon.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.link_button(
                "🔎 Cari Hunian di BTN Properti",
                url=f"https://www.btnproperti.co.id/search?price_max={int(harga_rumah_target)}",
                use_container_width=True
            )
        with col_btn2:
            st.link_button(
                "🏦 Buka Tabungan BTN Perumahan",
                url="https://www.btn.co.id/id/conventional/product/saving/tabungan-btn-perumahan",
                use_container_width=True
            )