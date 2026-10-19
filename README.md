# XTRADE KING — Streamlit AI Studio

## Jalankan di komputer/server
1. Install Python 3.10 atau lebih baru.
2. Simpan `app.py` dan `requirements.txt` dalam satu folder.
3. Install dependency:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan:
   ```bash
   streamlit run app.py
   ```
5. Di sidebar, pilih provider, tempel API key resmi, lalu tekan **Simpan key**.

## Penyimpanan
- Chat dan pengaturan: `.xtrade_king/xtrade_king.db`
- Kunci enkripsi lokal: `.xtrade_king/.vault.key`
- Jangan commit folder `.xtrade_king` ke GitHub.
- Untuk server publik, set `XTRADE_MASTER_KEY` sebagai secret environment variable dan gunakan penyimpanan persisten.

## Deployment
Streamlit Community Cloud: upload `app.py` dan `requirements.txt` ke repo privat/publik sesuai kebutuhan, lalu deploy. Untuk data yang harus bertahan melewati redeploy, gunakan database persisten eksternal. Jangan mengandalkan filesystem sementara cloud untuk riwayat permanen.

## Catatan
Model, nama model, endpoint, kuota, dan kebijakan konten mengikuti penyedia API. Perbarui daftar model sesuai dokumentasi resmi provider.
