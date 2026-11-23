import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_passport_pdf(
    nama_pemohon: str,
    jenis_pekerjaan: str,
    harga_rumah_target: float,
    dp_tersedia: float,
    tenor_kpr: int,
    scoring: dict,
    net_income: float,
    existing_debt: float,
    rek: dict
) -> bytes:
    """Menghasilkan file PDF resmi KPR Readiness Passport dengan desain perbankan."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Warna Korporat
    btn_blue = colors.HexColor("#003366")
    btn_gold = colors.HexColor("#C59B27")
    gray_bg = colors.HexColor("#F8FAFC")
    dark_text = colors.HexColor("#1E293B")
    border_color = colors.HexColor("#CBD5E1")

    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=btn_blue
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B")
    )
    section_title = ParagraphStyle(
        "SectionTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=btn_blue
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=dark_text
    )
    body_bold = ParagraphStyle(
        "DocBodyBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=dark_text
    )

    story = []

    # ==========================================
    # HEADER DOKUMEN
    # ==========================================
    header_data = [
        [
            Paragraph("<b>SIAPKPR AI</b> | Bank BTN Partner Ecosystem", title_style),
            Paragraph(f"<b>Tanggal Penerbitan:</b><br/>{datetime.now().strftime('%d %B %Y')}", subtitle_style)
        ]
    ]
    t_header = Table(header_data, colWidths=[360, 160])
    t_header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 4))
    story.append(Paragraph("KPR READINESS PASSPORT & PRE-UNDERWRITING CERTIFICATE", ParagraphStyle(
        "SubBanner",
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=btn_gold,
        leading=14
    )))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=btn_blue, spaceAfter=12))

    # ==========================================
    # 1. PROFIL CALON DEBITUR
    # ==========================================
    story.append(Paragraph("1. PROFIL CALON DEBITUR & TARGET HUNIAN", section_title))
    story.append(Spacer(1, 4))

    profil_data = [
        [Paragraph("Nama Calon Debitur", body_style), Paragraph(f": <b>{nama_pemohon}</b>", body_style),
         Paragraph("Target Harga Rumah", body_style), Paragraph(f": <b>Rp {harga_rumah_target:,.0f}</b>", body_style)],
        [Paragraph("Kategori Pekerjaan", body_style), Paragraph(f": <b>{jenis_pekerjaan}</b>", body_style),
         Paragraph("Rencana Tenor KPR", body_style), Paragraph(f": <b>{tenor_kpr} Tahun</b>", body_style)],
        [Paragraph("Dana DP Tersedia", body_style), Paragraph(f": <b>Rp {dp_tersedia:,.0f}</b>", body_style),
         Paragraph("Status Penilaian", body_style), Paragraph(f": <b>{scoring['status']}</b>", body_style)]
    ]
    t_profil = Table(profil_data, colWidths=[110, 150, 110, 150])
    t_profil.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), gray_bg),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_profil)
    story.append(Spacer(1, 12))

    # ==========================================
    # 2. HASIL CASH-FLOW UNDERWRITING
    # ==========================================
    story.append(Paragraph("2. HASIL ANALISIS KELAYAKAN KREDIT (CASH-FLOW UNDERWRITING)", section_title))
    story.append(Spacer(1, 4))

    score_color = colors.HexColor("#16A34A") if scoring["total_score"] >= 80 else (colors.HexColor("#CA8A04") if scoring["total_score"] >= 60 else colors.HexColor("#DC2626"))

    underwriting_data = [
        [
            Paragraph("Parameter Penilaian", body_bold),
            Paragraph("Hasil Analisis Mutasi", body_bold),
            Paragraph("Standar Acuan Bank BTN", body_bold)
        ],
        [
            Paragraph("<b>Skor Kesiapan KPR</b>", body_style),
            Paragraph(f"<font color='{score_color.hexval()}'><b>{scoring['total_score']} / 100 ({scoring['status']})</b></font>", body_style),
            Paragraph("Minimal 80 Poin (Prioritas Pre-Approved)", body_style)
        ],
        [
            Paragraph("Rata-rata Pemasukan Bersih", body_style),
            Paragraph(f"Rp {net_income:,.0f} / bulan", body_style),
            Paragraph("Dihitung rata-rata mutasi kredit (CR) 3 bulan", body_style)
        ],
        [
            Paragraph("Rasio Beban Cicilan (DBR)", body_style),
            Paragraph(f"<b>{scoring['dbr_existing_pct']}%</b> (Rp {existing_debt:,.0f}/bln)", body_style),
            Paragraph("Maksimal 35% dari pemasukan bersih", body_style)
        ],
        [
            Paragraph("Kapasitas Cicilan KPR Aman", body_style),
            Paragraph(f"<b>Rp {scoring['max_kpr_installment']:,.0f} / bulan</b>", body_style),
            Paragraph("Batas angsuran bulanan yang aman bagi nasabah", body_style)
        ],
        [
            Paragraph("<b>Estimasi Plafon KPR BTN</b>", body_style),
            Paragraph(f"<b>Rp {scoring['estimated_plafon']:,.0f}</b>", body_style),
            Paragraph(f"Proyeksi plafon berdasarkan tenor {tenor_kpr} th & bunga anuitas", body_style)
        ]
    ]
    t_underwriting = Table(underwriting_data, colWidths=[150, 185, 185])
    t_underwriting.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_underwriting)
    story.append(Spacer(1, 12))

    # ==========================================
    # 3. RINCIAN ESTIMASI MODAL AWAL PRA-AKAD
    # ==========================================
    story.append(Paragraph("3. ESTIMASI RINCIAN MODAL AWAL PRA-AKAD KPR", section_title))
    story.append(Spacer(1, 4))

    modal_data = [
        [Paragraph("Komponen Biaya", body_bold), Paragraph("Nominal Estimasi", body_bold), Paragraph("Keterangan", body_bold)],
        [Paragraph("Uang Muka Minimal (DP 10%)", body_style), Paragraph(f"Rp {scoring['target_dp_needed']:,.0f}", body_style), Paragraph("Batas minimal uang muka KPR rumah tapak", body_style)],
        [Paragraph("Estimasi Biaya Akad (~6%)", body_style), Paragraph(f"Rp {scoring['est_closing_costs']:,.0f}", body_style), Paragraph("Pajak BPHTB (5%), Akta Notaris/AJB, Provisi, Asuransi", body_style)],
        [Paragraph("<b>Total Modal Awal yang Diperlukan</b>", body_bold), Paragraph(f"<b>Rp {scoring['total_upfront_needed']:,.0f}</b>", body_bold), Paragraph("Total dana likuiditas yang harus disiapkan sebelum akad", body_style)],
        [Paragraph("Dana DP Tersedia Saat Ini", body_style), Paragraph(f"Rp {dp_tersedia:,.0f}", body_style), Paragraph("Status dana yang telah dikumpulkan calon debitur", body_style)]
    ]
    t_modal = Table(modal_data, colWidths=[150, 135, 235])
    t_modal.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_modal)
    story.append(Spacer(1, 12))

    # ==========================================
    # 4. REKOMENDASI HUNIAN & CATATAN BANK
    # ==========================================
    story.append(Paragraph("4. REKOMENDASI HUNIAN & CATATAN KESIAPAN", section_title))
    story.append(Spacer(1, 4))

    rekomendasi_data = [
        [Paragraph("Produk KPR BTN Disarankan", body_bold), Paragraph(rek.get("produk_kpr_cocok", "-"), body_style)],
        [Paragraph("Rekomendasi Tipe Hunian", body_bold), Paragraph(rek.get("tipe_hunian_disarankan", "-"), body_style)],
        [Paragraph("Catatan Kesiapan Penghuni", body_bold), Paragraph(rek.get("catatan_kesiapan_penghuni", "-"), body_style)]
    ]
    t_rek = Table(rekomendasi_data, colWidths=[160, 360])
    t_rek.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), gray_bg),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_rek)
    story.append(Spacer(1, 16))

    # ==========================================
    # FOOTER & LEGAL DISCLAIMER
    # ==========================================
    story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceAfter=8))
    footer_text = (
        "<i>Dokumen KPR Readiness Passport ini diterbitkan secara otomatis oleh sistem SiapKPR AI "
        "sebagai instrumen pre-underwriting mandiri berbasis UU PDP. Dokumen ini dapat dilampirkan "
        "sebagai profil keuangan awal saat pengajuan kredit resmi di kantor cabang Bank BTN terdekat.</i>"
    )
    story.append(Paragraph(footer_text, ParagraphStyle("Footer", fontName="Helvetica-Oblique", fontSize=8, leading=11, textColor=colors.HexColor("#64748B"))))

    doc.build(story)
    return buffer.getvalue()
