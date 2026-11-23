"""
Script generator untuk membuat Dokumen PDF Komprehensif SiapKPR AI:
"Buku Putih Teknis & Dokumentasi Arsitektur SiapKPR AI"
Mencakup:
1. Cover & Executive Summary
2. Problem Statement & Market Opportunity
3. Arsitektur Solusi & Diagram Alur (End-to-End Pipeline)
4. Modul Privasi & Kepatuhan UU PDP (Client-side Redaction)
5. Arsitektur Hybrid: Deterministic Accounting + LLM Coaching
6. Formulasi Matematika & Scoring Engine KPR (DBR, Konsistensi, DP Coverage, Anuitas Plafon)
7. Desain Prompt LLM (System Prompt & Coaching Prompt)
8. What-If Simulator & Edukasi Biaya Akad (Closing Costs)
9. Integrasi Ekosistem Bank BTN & KPR Readiness Passport
10. Potongan Kode Kunci & Panduan Deployment
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group, Polygon


class NumberedCanvas(canvas.Canvas):
    """Canvas kustom untuk menambahkan header & running footer nomor halaman (Halaman X dari Y)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Lewati cover page
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Header
        self.drawString(36, 810, "DOKUMENTASI TEKNIS & ARSITEKTUR SISTEM — SIAPKPR AI")
        self.drawRightString(559, 810, "BANK BTN PARTNER ECOSYSTEM")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 804, 559, 804)

        # Running Footer
        self.line(36, 42, 559, 42)
        self.drawString(36, 30, "Rahasia & Hak Cipta © 2026 SiapKPR AI. Semua Hak Dilindungi.")
        page_text = f"Halaman {self._pageNumber} dari {page_count}"
        self.drawRightString(559, 30, page_text)
        self.restoreState()


def create_architecture_diagram():
    """Membuat diagram arsitektur hybrid menggunakan ReportLab Drawing primitives."""
    d = Drawing(520, 150)
    
    # Background Canvas
    d.add(Rect(0, 0, 520, 150, fillColor=colors.HexColor("#F8FAFC"), strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=1, rx=6, ry=6))
    
    # Box 1: Input Mutasi
    d.add(Rect(15, 80, 105, 50, fillColor=colors.HexColor("#003366"), strokeColor=None, rx=4, ry=4))
    d.add(String(67, 108, "1. INPUT MUTASI", fontName="Helvetica-Bold", fontSize=7.5, fillColor=colors.white, textAnchor="middle"))
    d.add(String(67, 95, "e-Statement / CSV", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor("#E2E8F0"), textAnchor="middle"))

    # Arrow 1 -> 2
    d.add(Line(120, 105, 140, 105, strokeColor=colors.HexColor("#003366"), strokeWidth=1.5))
    d.add(Polygon([140, 108, 145, 105, 140, 102], fillColor=colors.HexColor("#003366"), strokeColor=None))

    # Box 2: Privacy Filter (UU PDP)
    d.add(Rect(145, 80, 110, 50, fillColor=colors.HexColor("#0284C7"), strokeColor=None, rx=4, ry=4))
    d.add(String(200, 108, "2. FILTER PRIVASI", fontName="Helvetica-Bold", fontSize=7.5, fillColor=colors.white, textAnchor="middle"))
    d.add(String(200, 95, "UU PDP Redaction", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor("#E0F2FE"), textAnchor="middle"))

    # Branch Arrow ke Jalur Atas (Deterministic) & Jalur Bawah (Full LLM)
    d.add(Line(255, 105, 275, 105, strokeColor=colors.HexColor("#0284C7"), strokeWidth=1.5))
    d.add(Line(275, 120, 275, 45, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.5))
    
    # Branch Ke Jalur 1 (Deterministik)
    d.add(Line(275, 120, 295, 120, strokeColor=colors.HexColor("#16A34A"), strokeWidth=1.5))
    d.add(Polygon([295, 123, 300, 120, 295, 117], fillColor=colors.HexColor("#16A34A"), strokeColor=None))
    
    # Box 3A: Deterministic Engine
    d.add(Rect(300, 98, 100, 44, fillColor=colors.HexColor("#16A34A"), strokeColor=None, rx=4, ry=4))
    d.add(String(350, 123, "Jalur CSV (Pasti)", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.white, textAnchor="middle"))
    d.add(String(350, 111, "Python Accounting", fontName="Helvetica-Bold", fontSize=7.5, fillColor=colors.white, textAnchor="middle"))
    d.add(String(350, 101, "Akurasi 100% Bebas Halusinasi", fontName="Helvetica", fontSize=6, fillColor=colors.HexColor("#DCFCE7"), textAnchor="middle"))

    # Box 3B: LLM Coaching
    d.add(Rect(415, 98, 95, 44, fillColor=colors.HexColor("#7C3AED"), strokeColor=None, rx=4, ry=4))
    d.add(String(462, 123, "LLM Groq (Qwen)", fontName="Helvetica-Bold", fontSize=7.5, fillColor=colors.white, textAnchor="middle"))
    d.add(String(462, 111, "Narasi DBR & Plan", fontName="Helvetica", fontSize=7, fillColor=colors.white, textAnchor="middle"))
    d.add(String(462, 101, "Ekosistem Hunian BTN", fontName="Helvetica", fontSize=6, fillColor=colors.HexColor("#F3E8FF"), textAnchor="middle"))
    
    d.add(Line(400, 120, 415, 120, strokeColor=colors.HexColor("#7C3AED"), strokeWidth=1.5))
    d.add(Polygon([415, 123, 420, 120, 415, 117], fillColor=colors.HexColor("#7C3AED"), strokeColor=None))

    # Branch Ke Jalur 2 (PDF Bebas)
    d.add(Line(275, 45, 295, 45, strokeColor=colors.HexColor("#EA580C"), strokeWidth=1.5))
    d.add(Polygon([295, 48, 300, 45, 295, 42], fillColor=colors.HexColor("#EA580C"), strokeColor=None))

    d.add(Rect(300, 25, 210, 40, fillColor=colors.HexColor("#EA580C"), strokeColor=None, rx=4, ry=4))
    d.add(String(405, 48, "Jalur Dokumen PDF Tidak Terstruktur", fontName="Helvetica-Bold", fontSize=7.5, fillColor=colors.white, textAnchor="middle"))
    d.add(String(405, 36, "End-to-End Extraction: Qwen 3.8 27B / GPT-OSS 120B Fallback", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor("#FFEDD5"), textAnchor="middle"))

    # Final Convergence Box
    d.add(Rect(15, 12, 240, 52, fillColor=colors.HexColor("#1E293B"), strokeColor=None, rx=4, ry=4))
    d.add(String(135, 47, "OUTPUT RESMI PERBANKAN", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor("#FACC15"), textAnchor="middle"))
    d.add(String(135, 34, "1. Skor KPR 0-100 & Kapasitas DBR 35%", fontName="Helvetica", fontSize=7, fillColor=colors.white, textAnchor="middle"))
    d.add(String(135, 22, "2. KPR Readiness Passport (PDF) & What-If Simulator", fontName="Helvetica", fontSize=7, fillColor=colors.white, textAnchor="middle"))

    # Convergence line to output
    d.add(Line(510, 70, 510, 10, strokeColor=colors.HexColor("#1E293B"), strokeWidth=1))
    d.add(Line(510, 10, 260, 10, strokeColor=colors.HexColor("#1E293B"), strokeWidth=1))
    d.add(Line(260, 10, 260, 38, strokeColor=colors.HexColor("#1E293B"), strokeWidth=1))
    d.add(Polygon([257, 38, 255, 43, 253, 38], fillColor=colors.HexColor("#1E293B"), strokeColor=None))

    return d


def generate_comprehensive_documentation_pdf(output_path: str):
    """Membuat seluruh buku putih dokumentasi teknis SiapKPR AI dalam bentuk PDF."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    # Warna Tema Korporat
    btn_blue = colors.HexColor("#003366")
    btn_gold = colors.HexColor("#C59B27")
    slate_dark = colors.HexColor("#1E293B")
    slate_light = colors.HexColor("#F8FAFC")
    border_slate = colors.HexColor("#CBD5E1")
    code_bg = colors.HexColor("#0F172A")
    code_text = colors.HexColor("#38BDF8")

    # Paragraph Styles
    cover_title = ParagraphStyle(
        "CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=32,
        textColor=btn_blue,
        alignment=0
    )
    cover_subtitle = ParagraphStyle(
        "CoverSubtitle",
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        alignment=0
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=btn_blue,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=btn_gold,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    body = ParagraphStyle(
        "Body_Custom",
        fontName="Helvetica",
        fontSize=9,
        leading=13.5,
        textColor=slate_dark,
        spaceAfter=6
    )
    body_bold = ParagraphStyle(
        "BodyBold_Custom",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13.5,
        textColor=slate_dark
    )
    callout = ParagraphStyle(
        "Callout_Custom",
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#0369A1")
    )
    code_style = ParagraphStyle(
        "Code_Custom",
        fontName="Courier",
        fontSize=7.5,
        leading=10.5,
        textColor=code_text
    )

    story = []

    # =========================================================================
    # HALAMAN 1: COVER & EXECUTIVE SUMMARY
    # =========================================================================
    story.append(Spacer(1, 25))
    story.append(Paragraph("<b>SIAPKPR AI</b>", ParagraphStyle("BrandPre", fontName="Helvetica-Bold", fontSize=13, textColor=btn_gold, leading=16)))
    story.append(Spacer(1, 4))
    story.append(Paragraph("DOKUMENTASI TEKNIS & BUKU PUTIH ARSITEKTUR SISTEM", cover_title))
    story.append(Spacer(1, 6))
    story.append(Paragraph("AI-Powered Cash-Flow Underwriting & KPR Readiness Copilot untuk Pekerja Informal & Gen Z dalam Ekosistem Bank BTN", cover_subtitle))
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=2.5, color=btn_blue, spaceAfter=16))

    # Meta Table Cover
    meta_info = [
        [Paragraph("<b>Status Proyek</b>", body_bold), Paragraph(": Production-Ready / Competition Finalist Pitching", body)],
        [Paragraph("<b>Versi Sistem</b>", body_bold), Paragraph(": 2.4.0 (Hybrid Accounting + Multimodel LLM Coaching)", body)],
        [Paragraph("<b>Fokus Ekosistem</b>", body_bold), Paragraph(": Bank BTN (KPR Gaess, KPR Platinum, BTN Properti, Tabungan Perumahan)", body)],
        [Paragraph("<b>Kepatuhan Regulasi</b>", body_bold), Paragraph(": UU No. 27 Tahun 2022 (Pelindungan Data Pribadi / UU PDP)", body)],
        [Paragraph("<b>Arsitektur Inti</b>", body_bold), Paragraph(": Streamlit + Deterministic Accounting + Groq Cloud (Qwen 3.8 / GPT-OSS)", body)],
        [Paragraph("<b>Tanggal Rilis</b>", body_bold), Paragraph(": November 2026", body)]
    ]
    t_meta = Table(meta_info, colWidths=[130, 390])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), slate_light),
        ("BOX", (0, 0), (-1, -1), 0.5, border_slate),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_slate),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 16))

    # Executive Summary Box
    summary_html = (
        "<b>RINGKASAN EKSEKUTIF (EXECUTIVE SUMMARY)</b><br/>"
        "Lebih dari 60% angkatan kerja di Indonesia (~84 juta orang) bekerja di sektor informal (gig economy, freelancer, kreator digital, "
        "dan pedagang e-commerce). Kelompok ini memiliki kapasitas finansial nyata namun kerap ditolak dalam pengajuan Kredit Pemilikan Rumah (KPR) "
        "karena tidak memiliki slip gaji formal, memiliki arus kas fluktuatif, serta terjerat riwayat transaksi PayLater/fintech konsumtif di SLIK OJK.<br/><br/>"
        "<b>SiapKPR AI</b> hadir sebagai platform <i>pre-underwriting</i> dan pembinaan mandiri pertama yang menjembatani pekerja informal dengan "
        "Bank BTN. Sistem mengekstrak e-statement mutasi rekening 3 bulan, melakukan enkripsi/redaksi data pribadi sesuai UU PDP, menghitung rasio utang "
        "(DBR) secara deterministik tanpa halusinasi matematis LLM, menyediakan <i>What-If Coaching Simulator</i> interaktif, dan menerbitkan "
        "<b>KPR Readiness Passport</b> resmi dalam format PDF berstandar perbankan."
    )
    t_sum = Table([[Paragraph(summary_html, body)]], colWidths=[520])
    t_sum.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#3B82F6")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(t_sum)

    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 2: LATAR BELAKANG, MASALAH, & ARSITEKTUR SOLUSI
    # =========================================================================
    story.append(Paragraph("1. LATAR BELAKANG & PROBLEM STATEMENT", h1_style))
    story.append(Paragraph(
        "KPR konvensional dirancang dengan paradigma lama: mensyaratkan slip gaji bulanan tetap dan Surat Keterangan Kerja (SKK). "
        "Kondisi ini menciptakan <i>credit invisible gap</i> yang memiskinkan akses kepemilikan hunian bagi generasi muda dan pekerja lepas.",
        body
    ))

    prob_data = [
        [Paragraph("Pilar Tantangan", body_bold), Paragraph("Kondisi di Lapangan (Fakta)", body_bold), Paragraph("Solusi SiapKPR AI", body_bold)],
        [
            Paragraph("<b>Unbankable / Non-Fixed Income</b>", body),
            Paragraph("Penghasilan freelancer bulanan naik-turun sehingga dianggap berisiko tinggi oleh sistem credit scoring lama.", body),
            Paragraph("AI menganalisis tren mutasi rekening 3 bulan dan mengukur konsistensi kas masuk (variasi &lt;20% mendapat skor tinggi).", body)
        ],
        [
            Paragraph("<b>Jeratan PayLater (SLIK OJK)</b>", body),
            Paragraph("Penggunaan SPayLater, Kredivo, dan GopayLater memangkas kapasitas angsuran DBR hingga &gt;25% tanpa disadari nasabah.", body),
            Paragraph("Deteksi otomatis transaksi cicilan konsumtif dan simulasi pelunasan langsung untuk meningkatkan plafon hingga ratusan juta.", body)
        ],
        [
            Paragraph("<b>Asimetri Biaya Akad</b>", body),
            Paragraph("Calon pembeli mengira hanya butuh uang DP, lalu gagal akad karena ketiadaan dana BPHTB, notaris, dan provisi (5-8%).", body),
            Paragraph("Kalkulasi transparan komponen modal awal (DP 10% + biaya akad 6%) di kartu passport.", body)
        ]
    ]
    t_prob = Table(prob_data, colWidths=[130, 195, 195])
    t_prob.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOX", (0, 0), (-1, -1), 0.5, border_slate),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_slate),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_prob)
    story.append(Spacer(1, 12))

    story.append(Paragraph("2. ARSITEKTUR SISTEM & DIAGRAM PIPELINE HYBRID", h1_style))
    story.append(Paragraph(
        "SiapKPR AI memelopori pendekatan <b>Hybrid Deterministic Accounting + LLM Coaching</b>. Pendekatan ini memisahkan secara ketat "
        "tugas kalkulasi aritmetika mutasi rekening (yang ditangani oleh Python Accounting Engine) dengan tugas penalaran kualitatif narasi "
        "risiko kredit (yang ditangani oleh Large Language Model berkonteks besar).",
        body
    ))
    story.append(Spacer(1, 4))
    story.append(create_architecture_diagram())
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<i>Diagram 1: Alur Pemrosesan Data End-to-End SiapKPR AI dari Input Berkas Mutasi hingga Terbitnya Paspor KPR.</i>",
        callout
    ))

    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 3: PRIVASI UU PDP & ARSITEKTUR HYBRID ACCOUNTING
    # =========================================================================
    story.append(Paragraph("3. MODUL PRIVASI & KEPATUHAN UU PDP (UU No. 27/2022)", h1_style))
    story.append(Paragraph(
        "Sesuai mandat UU Perlindungan Data Pribadi (UU PDP), bank dan pihak ketiga dilarang mentransfer data identitas keuangan sensitif "
        "ke penyedia layanan cloud pihak ketiga tanpa sanitasi. SiapKPR AI menyertakan modul <b>Client-Side Redaction Engine</b> pada "
        "<code>privacy.py</code> yang menyaring seluruh nomor rekening, kartu debit, NIK, dan kontak sebelum teks masuk ke memori analisis AI.",
        body
    ))

    code_privacy = (
        "# Potongan Kode Sanitasi Regex - privacy.py\n"
        "import re\n\n"
        "def redact_sensitive_info(text: str) -> str:\n"
        "    \"\"\"Menyensor nomor rekening / identitas numerik (10-16 digit) sebelum diproses LLM.\"\"\"\n"
        "    # Sensor nomor rekening dan kartu ATM/Debit\n"
        "    sanitized = re.sub(r'\\b\\d{10,16}\\b', '[NO_REK_DISENSOR]', text)\n"
        "    return sanitized\n"
    )
    t_code1 = Table([[Paragraph(code_privacy.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)]], colWidths=[520])
    t_code1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), code_bg),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#1E293B")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_code1)
    story.append(Spacer(1, 12))

    story.append(Paragraph("4. ARSITEKTUR HYBRID DETERMINISTIC ACCOUNTING", h1_style))
    story.append(Paragraph(
        "Salah satu kelemahan terbesar sistem berbasis LLM murni dalam dunia perbankan adalah <i>stochastic fluctuation</i> (halusinasi hitungan "
        "aritmatika penjumlahan dan pembagian). SiapKPR AI mengatasi hal ini dengan menerapkan <code>parse_csv_deterministic()</code>:",
        body
    ))

    hybrid_steps = [
        [Paragraph("Langkah Pipeline", body_bold), Paragraph("Logika Implementasi", body_bold), Paragraph("Output Terjamin", body_bold)],
        [
            Paragraph("<b>Klasifikasi Arus Kas</b>", body),
            Paragraph("Menyaring kolom <code>Tipe</code>: <code>CR</code> untuk seluruh kas masuk, <code>DR</code> untuk seluruh pengeluaran.", body),
            Paragraph("100% konsisten antar run", body)
        ],
        [
            Paragraph("<b>Deteksi Kata Kunci</b>", body),
            Paragraph("Penyaringan berbasis kamus kata: <code>paylater, kredivo, spaylater, pinjol</code> untuk beban utang; <code>tabungan, dp</code> untuk investasi.", body),
            Paragraph("Pemetaan pos akuntansi presisi", body)
        ],
        [
            Paragraph("<b>Normalisasi 3 Bulan</b>", body),
            Paragraph("Jumlah total kredit dibagi tepat 3 periode kalender untuk memperoleh rerata bulanan sejati.", body),
            Paragraph("Menghilangkan eror penjumlahan LLM", body)
        ],
        [
            Paragraph("<b>LLM Narrative Bridge</b>", body),
            Paragraph("Angka hasil Python diinjeksikan ke dalam <code>COACHING_PROMPT</code> sebagai parameter paten tanpa hak edit oleh LLM.", body),
            Paragraph("Narasi cerdas berangka mutlak", body)
        ]
    ]
    t_hybrid = Table(hybrid_steps, colWidths=[120, 240, 160])
    t_hybrid.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOX", (0, 0), (-1, -1), 0.5, border_slate),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_slate),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_hybrid)

    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 4: FORMULASI MATEMATIKA & CREDIT SCORING ENGINE
    # =========================================================================
    story.append(Paragraph("5. FORMULASI MATEMATIKA & SCORING ENGINE PERBANKAN", h1_style))
    story.append(Paragraph(
        "Scoring Engine pada <code>scoring_engine.py</code> mengadopsi standar credit underwriting Bank BTN dan pedoman Bank Indonesia (BI), "
        "yang memadukan rasio beban utang, konsistensi arus kas, rasio likuiditas tabungan, dan kebersihan riwayat SLIK OJK (Skor Maksimal = 100 Poin).",
        body
    ))

    # Rumus DBR
    story.append(Paragraph("A. Formulasi Debt Burden Ratio (DBR) — Bobot Maksimal 40 Poin", h2_style))
    story.append(Paragraph(
        "Rasio DBR mengukur porsi pendapatan bersih yang telah terserap untuk mencicil kewajiban berjalan (PayLater, KTA, leasing motor):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>DBR Ratio (%) = (Total Cicilan Eksisting Bulanan / Rata-rata Pemasukan Bersih) × 100%</b><br/>"
        "• DBR ≤ 10% : 40 Poin (Sangat Sehat)<br/>"
        "• 10% &lt; DBR ≤ 20% : 30 Poin (Sehat)<br/>"
        "• 20% &lt; DBR ≤ 30% : 15 Poin (Waspada)<br/>"
        "• 30% &lt; DBR ≤ 35% : 8 Poin (Ambang Batas Maksimal Bank)<br/>"
        "• DBR &gt; 35% : 0 Poin (Risiko Tinggi / Reject Bank)",
        body
    ))

    # Rumus Fluktuasi
    story.append(Paragraph("B. Formulasi Stabilitas & Konsistensi Kas — Bobot Maksimal 25 Poin", h2_style))
    story.append(Paragraph(
        "Mengukur volatilitas pemasukan pekerja informal selama 3 bulan pemantauan:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Fluktuasi Pemasukan (%) = [(Pemasukan Tertinggi - Pemasukan Terendah) / Rata-rata Pemasukan] × 100%</b><br/>"
        "• Fluktuasi ≤ 10% : 25 Poin | 10% - 20% : 20 Poin | 20% - 35% : 12 Poin | &gt;35% : 5 Poin",
        body
    ))

    # Rumus Likuiditas & DP
    story.append(Paragraph("C. Formulasi Kesiapan Likuiditas & DP — Bobot Maksimal 25 Poin", h2_style))
    story.append(Paragraph(
        "Menggabungkan rasio tabungan rutin (*Saving Habit*, maks 15 poin) dan rasio kecukupan modal uang muka (*DP Coverage*, maks 10 poin):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Target DP Minimum = 10% × Target Harga Rumah</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Saving Rate Score = Min(15.0, (Tabungan Bulanan / Pemasukan Bersih / 30%) × 15.0)</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>DP Coverage Score = Min(1.0, Dana DP Terkumpul / Target DP Minimum) × 10.0</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Estimasi Bulan Siap DP = Max(0, Target DP - Dana DP) / Tabungan Bulanan</b>",
        body
    ))

    # Rumus Anuitas Plafon KPR
    story.append(Paragraph("D. Formulasi Kapasitas Angsuran & Plafon KPR Berbasis Anuitas", h2_style))
    story.append(Paragraph(
        "Plafon kredit dihitung menggunakan rumus anuitas suku bunga perbankan komersial:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Batas Angsuran KPR Bulanan (A) = (35% × Pemasukan Bersih) - Cicilan Eksisting</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Plafon KPR (P) = A × [ (1 - (1 + r)^(-n)) / r ]</b><br/>"
        "Dimana <i>r</i> adalah suku bunga bulanan (misal 6.5% / 12 = 0.005417) dan <i>n</i> adalah total bulan tenor (misal 20 tahun = 240 bulan).",
        body
    ))

    score_matrix = [
        [Paragraph("Rentang Skor Total", body_bold), Paragraph("Predikat Kesiapan KPR", body_bold), Paragraph("Implikasi Perbankan (Bank BTN)", body_bold)],
        [Paragraph("<b>80 – 100 Poin</b>", body), Paragraph("<font color='#16A34A'><b>Siap Akad (KPR Ready)</b></font>", body), Paragraph("Lolos pre-underwriting otomatis; diprioritaskan untuk peninjauan berkas kilat.", body)],
        [Paragraph("<b>60 – 79 Poin</b>", body), Paragraph("<font color='#CA8A04'><b>Perlu Pembinaan 1-3 Bulan</b></font>", body), Paragraph("Wajib mengikuti rekomendasi What-If Simulator (pelunasan PayLater / tambah tabungan).", body)],
        [Paragraph("<b>&lt; 60 Poin</b>", body), Paragraph("<font color='#DC2626'><b>Belum Siap / Risiko Tinggi</b></font>", body), Paragraph("Kapasitas DBR terlampaui atau riwayat red-flags menuntut restrukturisasi total.", body)]
    ]
    t_matrix = Table(score_matrix, colWidths=[120, 160, 240])
    t_matrix.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOX", (0, 0), (-1, -1), 0.5, border_slate),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_slate),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_matrix)

    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 5: PROMPT ENGINEERING & LLM CONFIGURATION
    # =========================================================================
    story.append(Paragraph("6. DESAIN PROMPT & MULTI-MODEL FALLBACK ENGINE", h1_style))
    story.append(Paragraph(
        "SiapKPR AI mengimplementasikan arsitektur LLM tingkat industri dengan mekanisme <i>failover</i> berlapis di <code>ai_parser.py</code>. "
        "Jika model utama mengalami limit kuota atau latensi tinggi, permintaan dialihkan secara otomatis tanpa mengganggu pengalaman pengguna.",
        body
    ))

    models_table = [
        [Paragraph("Tingkatan (Tier)", body_bold), Paragraph("Model Name (Groq Cloud)", body_bold), Paragraph("Alasan Pemilihan & Karakteristik", body_bold)],
        [
            Paragraph("<b>Tier 1 (Utama)</b>", body),
            Paragraph("<code>qwen/qwen3.8-27b</code>", body),
            Paragraph("Akurasi kepatuhan skema JSON tertinggi, penalaran nuansa lokal perbankan Indonesia tajam, latensi &lt;1.2 detik.", body)
        ],
        [
            Paragraph("<b>Tier 2 (Backup 1)</b>", body),
            Paragraph("<code>openai/gpt-oss-120b</code>", body),
            Paragraph("Model bernalar besar dengan kapasitas konteks 131k token untuk menangani e-statement multi-halaman kompleks.", body)
        ],
        [
            Paragraph("<b>Tier 3 (Backup 2)</b>", body),
            Paragraph("<code>openai/gpt-oss-20b</code>", body),
            Paragraph("Model ultra-ringan dan responsif sebagai jaring pengaman terakhir jika trafik jaringan global mengalami degradasi.", body)
        ],
        [
            Paragraph("<b>Tier 4 (Offline)</b>", body),
            Paragraph("<code>Local Rule-based Engine</code>", body),
            Paragraph("Parser berbasis algoritma lokal jika koneksi internet terputus total saat demonstrasi panggung juri.", body)
        ]
    ]
    t_models = Table(models_table, colWidths=[100, 160, 260])
    t_models.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOX", (0, 0), (-1, -1), 0.5, border_slate),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_slate),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_models)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Struktur Prompt LLM: Coaching & Underwriting Prompt", h2_style))
    prompt_snippet = (
        "# SYSTEM & COACHING PROMPT STRUCTURE (config.py & ai_parser.py)\n"
        "Anda adalah analis kredit KPR perbankan Indonesia untuk aplikasi 'SiapKPR AI'.\n"
        "PANDUAN KETAT:\n"
        "1. JANGAN mengubah angka keuangan yang SUDAH DIHITUNG SECARA PASTI oleh sistem.\n"
        "2. Gunakan istilah perbankan Indonesia 'DBR (Debt Burden Ratio)' secara konsisten.\n"
        "   DILARANG KERAS menggunakan istilah asing 'DTI'.\n"
        "3. Rujuk fasilitas kredit konsumtif terdeteksi secara spesifik (SPayLater, Kredivo).\n"
        "4. Action plan 3 bulan wajib terukur nominal rupiahnya terhadap kenaikan plafon KPR BTN.\n"
        "5. Keluarkan output HANYA dalam format JSON valid tanpa markdown tambahan."
    )
    t_prompt = Table([[Paragraph(prompt_snippet.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)]], colWidths=[520])
    t_prompt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), code_bg),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#1E293B")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_prompt)

    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 6: WHAT-IF SIMULATOR, BIAYA AKAD, & EKOSISTEM BTN
    # =========================================================================
    story.append(Paragraph("7. WHAT-IF COACHING SIMULATOR & BIAYA PRA-AKAD", h1_style))
    story.append(Paragraph(
        "Fitur <b>What-If Coaching Simulator</b> adalah inti nilai tambah aplikasi ini. Alih-alih hanya memberikan vonis penolakan, "
        "aplikasi mendidik nasabah secara interaktif tentang bagaimana tindakan finansial mereka hari ini dapat mengubah status kredit mereka.",
        body
    ))

    sim_features = [
        [Paragraph("Komponen Simulator", body_bold), Paragraph("Mekanisme & Formula", body_bold), Paragraph("Dampak Terhadap Calon Debitur", body_bold)],
        [
            Paragraph("<b>Slider Pelunasan Utang / PayLater</b>", body),
            Paragraph("<code>sim_debt = max(0, debt - reduction)</code><br/>Mengurangi pembagi rasio DBR secara instan.", body),
            Paragraph("Menaikkan kapasitas angsuran bulanan dan membuka plafon pinjaman puluhan hingga ratusan juta rupiah.", body)
        ],
        [
            Paragraph("<b>Slider Alokasi Tabungan DP</b>", body),
            Paragraph("<code>sim_savings = savings + extra</code><br/>Menghitung ulang saving habit & kecukupan likuiditas.", body),
            Paragraph("Mempercepat waktu kesiapan akad dari hitungan tahun/bulan menjadi status 'Siap Sekarang'.", body)
        ],
        [
            Paragraph("<b>Transparansi Biaya Akad (Closing Costs)</b>", body),
            Paragraph("<code>target_dp (10%) + closing_costs (6%) = Total Modal Awal Wajib</code>", body),
            Paragraph("Menghilangkan risiko nasabah gagal akad akibat tidak memiliki dana BPHTB, notaris, dan provisi bank.", body)
        ]
    ]
    t_sim = Table(sim_features, colWidths=[130, 195, 195])
    t_sim.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOX", (0, 0), (-1, -1), 0.5, border_slate),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_slate),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_sim)
    story.append(Spacer(1, 14))

    story.append(Paragraph("8. INTEGRASI EKOSISTEM BANK BTN & KPR READINESS PASSPORT", h1_style))
    story.append(Paragraph(
        "SiapKPR AI tidak berdiri sebagai aplikasi tertutup, melainkan terhubung langsung ke rantai nilai produk Bank BTN:",
        body
    ))

    btn_items = [
        [Paragraph("Saluran Integrasi", body_bold), Paragraph("Bentuk Sinergi Bisnis", body_bold)],
        [
            Paragraph("<b>KPR BTN Gaess & Platinum</b>", body),
            Paragraph("Rekomendasi skema KPR disesuaikan dengan profil usia dan jenis pekerjaan nasabah (tenor fleksibel hingga 30 tahun).", body)
        ],
        [
            Paragraph("<b>Portal BTN Properti (btnproperti.co.id)</b>", body),
            Paragraph("Tombol tautan cerdas membawa calon pembeli langsung ke katalog listing rumah rekanan BTN sesuai batas plafon maksimal hasil analisis.", body)
        ],
        [
            Paragraph("<b>Tabungan BTN Perumahan</b>", body),
            Paragraph("Nasabah yang memerlukan pembinaan 1-3 bulan diarahkan untuk membuka rekening autodebet tabungan rencana DP di Bank BTN.", body)
        ],
        [
            Paragraph("<b>KPR Readiness Passport (PDF Resmi)</b>", body),
            Paragraph("Sertifikat pre-underwriting berformat PDF lengkap dengan rincian rasio DBR, kapasitas angsuran, dan legal disclaimer untuk dibawa ke kantor cabang.", body)
        ]
    ]
    t_btn = Table(btn_items, colWidths=[160, 360])
    t_btn.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOX", (0, 0), (-1, -1), 0.5, border_slate),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_slate),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_btn)

    story.append(PageBreak())

    # =========================================================================
    # HALAMAN 7: STRUKTUR DIREKTORI, POTONGAN KODE KUNCI, & PANDUAN RUNNING
    # =========================================================================
    story.append(Paragraph("9. STRUKTUR DIREKTORI & MODUL KODE UTAMA", h1_style))
    story.append(Paragraph(
        "Kode disusun secara modular untuk memudahkan pemeliharaan, pengujian unit, serta integrasi API perbankan lanjutan:",
        body
    ))

    file_structure = [
        [Paragraph("File / Direktori", body_bold), Paragraph("Tanggung Jawab Teknis", body_bold)],
        [Paragraph("<code>app.py</code>", body), Paragraph("Antarmuka pengguna (Streamlit), manajemen state session, visualisasi metrik, What-If simulator, dan integrasi tombol unduh.", body)],
        [Paragraph("<code>ai_parser.py</code>", body), Paragraph("Engine hybrid: kalkulasi deterministik Python untuk CSV + inferensi LLM Groq (Qwen 3.8 / GPT-OSS) untuk narasi coaching.", body)],
        [Paragraph("<code>scoring_engine.py</code>", body), Paragraph("Implementasi matematis credit scoring perbankan (DBR, konsistensi pemasukan, likuiditas DP, dan anuitas plafon KPR).", body)],
        [Paragraph("<code>privacy.py</code>", body), Paragraph("Sanitasi data pribadi (UU PDP) dengan deteksi regex pada nomor rekening bank dan identitas sensitif pengguna.", body)],
        [Paragraph("<code>pdf_generator.py</code>", body), Paragraph("Mesin penerbit sertifikat KPR Readiness Passport resmi berformat PDF berbasis ReportLab canvas.", body)],
        [Paragraph("<code>config.py</code>", body), Paragraph("Definisi system prompts, dataset sintetis demo (Freelancer & UMKM), dan kustomisasi CSS tampilan.", body)],
        [Paragraph("<code>sample_statements/</code>", body), Paragraph("Kumpulan berkas mutasi rekening uji coba (PDF resmi e-Statement Bank BTN dan CSV) untuk simulasi live demo.", body)]
    ]
    t_files = Table(file_structure, colWidths=[140, 380])
    t_files.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOX", (0, 0), (-1, -1), 0.5, border_slate),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_slate),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
    ]))
    story.append(t_files)
    story.append(Spacer(1, 10))

    story.append(Paragraph("10. PANDUAN INSTALASI & MENJALANKAN APLIKASI", h1_style))
    
    run_guide = (
        "# 1. Kloning / Buka Direktori Repositori\n"
        "cd C:\\Users\\User\\siapkpr-ai\n\n"
        "# 2. Aktifkan Virtual Environment Python\n"
        ".\\venv\\Scripts\\Activate.ps1\n\n"
        "# 3. Instal Dependensi yang Dibutuhkan\n"
        "pip install streamlit groq pandas pypdf python-dotenv reportlab\n\n"
        "# 4. Konfigurasi Variabel Lingkungan (.env)\n"
        "echo \"GROQ_API_KEY=gsk_your_groq_api_key_here\" > .env\n\n"
        "# 5. Jalankan Web App Streamlit\n"
        "streamlit run app.py\n"
    )
    t_run = Table([[Paragraph(run_guide.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)]], colWidths=[520])
    t_run.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), code_bg),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#1E293B")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_run)
    story.append(Spacer(1, 12))

    story.append(Paragraph(
        "<b>Pernyataan Penutup & Kesiapan Pitching:</b><br/>"
        "SiapKPR AI telah diuji secara komprehensif pada skenario freelancer dan pelaku UMKM. Seluruh komponen—mulai dari kepatuhan privasi, "
        "kalkulasi bebas eror aritmetika, pemodelan anuitas KPR riil, hingga penerbitan sertifikat PDF—telah siap 100% untuk didemokan di hadapan "
        "dewan juri, investor, maupun perwakilan Bank BTN.",
        ParagraphStyle("FinalClosing", fontName="Helvetica-Oblique", fontSize=8.5, leading=12, textColor=colors.HexColor("#334155"))
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Buku Putih Dokumentasi berhasil dibuat: {output_path}")


if __name__ == "__main__":
    target_file = r"C:\Users\User\siapkpr-ai\DOKUMENTASI_LENGKAP_SIAPKPR_AI.pdf"
    generate_comprehensive_documentation_pdf(target_file)
