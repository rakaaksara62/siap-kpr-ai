def calculate_kpr_score(
    net_income: float,
    existing_debt: float,
    monthly_savings: float,
    fluctuation_pct: float,
    red_flag_count: int,
    target_house_price: float = 300000000,
    current_dp: float = 30000000,
    tenor_years: int = 20,
    interest_rate_pct: float = 6.5
) -> dict:
    """Menghitung skor kesiapan KPR dan estimasi plafon kredit berdasarkan standar underwriting perbankan."""
    # Estimasi biaya pra-akad / closing costs (BPHTB, Notaris/AJB, Provisi, Asuransi jiwa/kebakaran: ~6% harga rumah)
    est_closing_costs = int(round(target_house_price * 0.06))
    target_dp = target_house_price * 0.10
    total_upfront_needed = int(round(target_dp + est_closing_costs))

    if net_income <= 0:
        return {
            "total_score": 0,
            "dbr_existing_pct": 100.0,
            "max_kpr_installment": 0,
            "estimated_plafon": 0,
            "target_dp_needed": int(target_dp),
            "est_closing_costs": est_closing_costs,
            "total_upfront_needed": total_upfront_needed,
            "dp_shortfall": max(0, int(target_dp - current_dp)),
            "months_to_ready_dp": 999,
            "status": "Belum Layak",
            "breakdown": {"dbr": 0, "consistency": 0, "savings": 0, "cleanliness": 0}
        }

    # 1. Skor DBR Eksisting (Maks 40 Poin) - Penilaian Kapasitas Utang
    dbr_ratio = (existing_debt / net_income) * 100
    if dbr_ratio <= 10:
        score_dbr = 40
    elif dbr_ratio <= 20:
        score_dbr = 30
    elif dbr_ratio <= 30:
        score_dbr = 15
    elif dbr_ratio <= 35:
        score_dbr = 8
    else:
        score_dbr = 0

    # 2. Skor Konsistensi Arus Kas (Maks 25 Poin) - Stabilitas Pekerja Informal
    if fluctuation_pct <= 10:
        score_consistency = 25
    elif fluctuation_pct <= 20:
        score_consistency = 20
    elif fluctuation_pct <= 35:
        score_consistency = 12
    else:
        score_consistency = 5

    # 3. Skor Kesiapan Likuiditas & DP (Maks 25 Poin)
    # Realistis perbankan: Menggabungkan saving rate + rasio pemenuhan DP minimum (10% harga rumah)
    dp_shortfall = max(0.0, target_dp - current_dp)
    
    # Rasio tabungan bulanan terhadap pemasukan (Maks 15 poin)
    savings_ratio = (monthly_savings / net_income) * 100
    score_saving_rate = min(15.0, (savings_ratio / 30.0) * 15.0)

    # Rasio kecukupan DP saat ini (Maks 10 poin)
    dp_coverage = min(1.0, current_dp / target_dp) if target_dp > 0 else 1.0
    score_dp_coverage = dp_coverage * 10.0

    score_savings = int(round(score_saving_rate + score_dp_coverage))

    # Estimasi bulan untuk melunasi kekurangan DP
    if dp_shortfall <= 0:
        months_to_ready = 0
    elif monthly_savings > 0:
        months_to_ready = max(1, int(round(dp_shortfall / monthly_savings)))
    else:
        months_to_ready = 99

    # 4. Skor Kebersihan Riwayat / Bebas Red Flag (Maks 10 Poin)
    if red_flag_count == 0:
        score_clean = 10
    elif red_flag_count == 1:
        score_clean = 4
    else:
        score_clean = 0

    total_score = min(100, score_dbr + score_consistency + score_savings + score_clean)

    # Kapasitas Cicilan KPR Maksimal (Batas aman bank DBR 35%)
    max_total_debt = 0.35 * net_income
    max_kpr_installment = max(0, max_total_debt - existing_debt)
    
    # Kalkulasi Plafon KPR berdasarkan rumus anuitas bunga perbankan (P = A * [ (1 - (1+r)^-n) / r ])
    months = max(12, tenor_years * 12)
    monthly_rate = (interest_rate_pct / 100.0) / 12.0
    if monthly_rate > 0 and max_kpr_installment >= 900000:
        annuity_factor = (1.0 - ((1.0 + monthly_rate) ** (-months))) / monthly_rate
        estimated_plafon = max_kpr_installment * annuity_factor
    else:
        estimated_plafon = max_kpr_installment * 105 if max_kpr_installment >= 900000 else 0

    if total_score >= 80 and estimated_plafon > 0 and months_to_ready <= 3:
        status = "Siap Akad (KPR Ready)"
    elif total_score >= 60:
        status = "Perlu Pembinaan 1–3 Bulan"
    else:
        status = "Belum Siap / Risiko Tinggi"

    return {
        "total_score": total_score,
        "dbr_existing_pct": round(dbr_ratio, 1),
        "max_kpr_installment": int(max_kpr_installment),
        "estimated_plafon": int(round(estimated_plafon)),
        "target_dp_needed": int(target_dp),
        "est_closing_costs": est_closing_costs,
        "total_upfront_needed": total_upfront_needed,
        "dp_shortfall": int(dp_shortfall),
        "months_to_ready_dp": months_to_ready,
        "status": status,
        "breakdown": {
            "dbr": score_dbr,
            "consistency": score_consistency,
            "savings": score_savings,
            "cleanliness": score_clean
        }
    }