# PROMPT MIGRASI & RINGKASAN ARSITEKTUR SIAPKPR AI

Salin seluruh isi dokumen di bawah ini dan tempelkan (*copy-paste*) ke sesi chat Gemini Anda untuk melanjutkan pembelajaran atau pengembangan fitur.

---

```markdown
Halo Gemini, saya sedang membangun aplikasi bernama "SiapKPR AI" (Pre-Underwriting & KPR Readiness Copilot untuk Pekerja Informal & Gen Z). 

Tolong pahami arsitektur, kondisi kode saat ini, serta progres fitur yang telah selesai dibangun untuk membantu saya mempelajari dan mengembangkan sistem ini lebih lanjut.

Berikut adalah rangkuman teknis proyek saat ini:

---

### 1. Deskripsi & Nilai Solusi Aplikasi
* **Nama Produk**: SiapKPR AI
* **Fungsi Utama**: AI Cash-Flow Underwriting & KPR Readiness Copilot berbasis Streamlit & LLM. 
* **Target Pengguna**: Pekerja gig/freelancer, pelaku UMKM online, dan kreator konten yang sering ditolak perbankan konvensional karena tidak punya slip gaji tetap (unbankable/underserved), memiliki riwayat transaksi PayLater, atau pemasukan fluktuatif.
* **Tujuan**: Menganalisis mutasi rekening 3 bulan, membersihkan data sensitif (kepatuhan UU PDP), mendeteksi kewajiban tersembunyi (PayLater/pinjol), menghitung skor kesiapan KPR berbasis rasio DBR (Debt Burden Ratio), menyediakan simulator perbaikan skor (What-If Simulator), dan menerbitkan rekomendasi produk KPR (khususnya ekosistem Bank BTN) serta "KPR Readiness Passport".

---

### 2. Struktur Proyek & Peran File
1. `app.py`:
   - Dashboard utama Streamlit (`st.set_page_config`, layout wide).
   - Sidebar: Input data pemohon (Nama, Pekerjaan, Target Harga Rumah, Dana DP Terkumpul) & input/deteksi otomatis Groq API Key.
   - Modul Unggah Mutasi (PDF/CSV) dan Demo Mode Cepat (Profil A: Freelancer terkendala PayLater, Profil B: UMKM Online siap akad).
   - Visualisasi: Metrik skor, bar chart arus kas, rincian skor kredit (progress bar), What-If Simulator dinamis, Rencana Aksi 3 Bulan, KPR Readiness Passport, dan tombol unduh laporan `.txt`.
2. `ai_parser.py`:
   - Ekstraksi dan klasifikasi mutasi rekening ke format terstruktur JSON menggunakan Groq API.
   - Model AI Utama: `qwen/qwen3.8-27b` (terpilih karena akurasi kalkulasi pos kredit/debit mutasi sangat tinggi).
   - Multi-Model Fallback: `qwen/qwen3.8-27b` -> `openai/gpt-oss-120b` -> `openai/gpt-oss-20b` -> Local Rule-based Parser (jika API offline/kuota habis).
3. `scoring_engine.py`:
   - Logika kalkulasi kredit perbankan realistis (Total Skor 0–100):
     * **Kapasitas Utang / DBR** (Maks 40 poin): Rasio cicilan bulanan vs pemasukan bersih (ambang aman bank ≤ 35%).
     * **Konsistensi Arus Kas** (Maks 25 poin): Penilaian tingkat fluktuasi pemasukan bulanan pekerja informal.
     * **Kesiapan Likuiditas & DP** (Maks 25 poin): Gabungan *saving rate* bulanan (maks 15 poin) dan kecukupan dana DP terhadap target DP 10% harga rumah (maks 10 poin).
     * **Kebersihan Riwayat / Bebas Red Flag** (Maks 10 poin): Pengurangan skor jika terdeteksi pinjaman konsumtif/PayLater aktif.
   - Menghitung kapasitas cicilan aman per bulan, estimasi plafon KPR BTN (`max_installment * 105`), serta estimasi bulan menuju kesiapan akad KPR.
4. `privacy.py`:
   - Kepatuhan UU Perlindungan Data Pribadi (UU PDP).
   - Menyensor secara otomatis nomor rekening, nomor kartu debit/kredit, NIK, nomor HP, email, dan nama nasabah sebelum data mutasi dikirimkan ke model LLM.
5. `config.py`:
   - System prompt LLM terstandarisasi untuk mengeluarkan output JSON ketat (`ringkasan_bulanan`, `detail_cicilan_terdeteksi`, `red_flags`, `action_plan_3_bulan`, `rekomendasi_hunian_btn`).
   - Dataset sintetis untuk demo juri: `DUMMY_FREELANCER` & `DUMMY_UMKM`.
   - Konfigurasi styling kustom CSS.
6. `.env`:
   - Menyimpan konfigurasi `GROQ_API_KEY`.

---

### 3. Fitur yang Telah Selesai Diimplementasikan & Diuji
- [x] Deteksi otomatis file `.env` di server/lokal sehingga pengguna tidak wajib menginput API key manual saat demo.
- [x] Sensor privasi otomatis berbasis regex (UU PDP) sebelum pemrosesan LLM.
- [x] Integrasi LLM Groq dengan mekanisme rotasi model otomatis (*automatic fallback*).
- [x] Penanganan aman kasus nasabah tanpa cicilan (`existing_debt = 0`) pada slider Streamlit untuk mencegah error `StreamlitInvalidMinMaxError`.
- [x] Perbaikan tampilan kartu *KPR Readiness Passport* menjadi adaptif menggunakan `st.container(border=True)` agar kontras dan serasi dengan tema gelap/terang.
- [x] *What-If Simulator* Realistis:
  * Slider pelunasan cicilan/PayLater langsung menaikkan kapasitas cicilan bulanan & plafon KPR.
  * Slider penambahan tabungan langsung menaikkan skor likuiditas secara proporsional serta mempercepat estimasi "Waktu Kesiapan DP Akad" (dalam hitungan bulan).
- [x] Ekspor laporan KPR Readiness Passport ke file `.txt` yang siap diunduh.

---

Berdasarkan konteks proyek di atas, bantu saya:
1. Menjelaskan secara ringkas bagaimana alur data mengalir dari saat pengguna mengunggah mutasi rekening hingga diterbitkannya skor KPR.
2. Memberikan masukan atau rekomendasi jika ada celah/fitur penting dari sudut pandang perbankan nyata yang masih bisa ditingkatkan di tahap berikutnya.
```
