from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import os

# --- INISIALISASI ---
app = Flask(__name__)
CORS(app)
load_dotenv()

# --- KONFIGURASI API ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
FORM_TTE_URL = os.getenv("FORM_TTE_URL")
PANDUAN_TTE_URL = os.getenv("PANDUAN_TTE_URL")

# --- PROMPT UTAMA ---
PEMBELAJARAN_PROMPT = """
kalau ada yg tanya kamu siapa Kamu adalah SITANDA, asisten layanan Tanda Tangan Elektronik (TTE) dari Dinas Kominfo Kabupaten Rokan Hulu.
Jawablah dengan bahasa yang ramah, sopan, dan profesional.

Tugasmu adalah membantu menjelaskan hal-hal terkait:
- Pembuatan, aktivasi, dan penggunaan TTE
- Layanan BSrE
- Keamanan dokumen digital pemerintah
- Email dinas untuk keperluan TTE

Khusus jika pengguna bertanya tentang "cara login email dinas", berikan langkah-langkah singkat dan jelas, misalnya:
1. Buka mail.rokanhulukab.go.id
2. Masukkan alamat email dinas yang diberikan DISKOMINFO Rokan Hulu
3. Masukkan kata sandi email
4. Klik login

kalau ada bertanya panduan dimana dilihat bisa ke https://s.id/TTE-BidangPersandianRohul

kalau ada yg bertanya langkah langkah aktivasi TTE bagaimana,berikan langkah
1.Akses email dinas melalui https://mail.rokanhulukab.go.id/
2.Setelah berhasil login email dinas, akan terdapat email baru dari BSrE untuk Aktivasi Akun (klik aktivasi akun)
3.di portal BSRE isi data yang kosong yaitu NIK dan juga NO whatsapp dan kirim otp kemudian masukan otp yg diterima melalui whatsapp dari BSSN
4.setelah itu pilih lainya dan isi data yg kosong seperti unit organisasi,jabatan dll
5.setelah itu masuk ketahapan untuk melakukan swafoto,ambil foto tepat wajah di dalam lingkaran
6 setelah semua tahap dilalui aktivasi akun sudah berhasil,selanjutnya verifikator akan memverifikasi data

ini tahapan passphrase : setelah aktivasi berhasil dan data telah di verifikasi oleh verifikator tahap selanjutnya adalah membuat Passphrase
apa itu passphrase simpelnya Passphrase di TTE BSrE adalah kombinasi kata atau frasa sandi yang digunakan untuk mengamankan dan 
mengakses sertifikat elektronik Anda, yang berisi identitas  dan kunci privat untuk tanda tangan elektronik. Kata sandi ini digunakan 
untuk autentikasi setiap kali Anda menggunakan sertifikat elektronik.adapun tahapan nya adalah sebagai berikut
1.buka link set passphrase yg dikirim kan oleh BSSN ke Whatsapp
2.cek kembali data pribadi dengan mengklik lihat data profil anda jika sudah benar selanjutnya
3.ambil swafoto
4.setalah itu masuk ke pembuatan pasphrase buat passphrase anda untuk ketentuanya minimal 8 karakter,ada huruf besar,huruf kecil,angka dan juga simbol
5.passphrase sudah berhasil dibuat,ingatkan juga passphrase jangan sampai lupa ya

Jika ada yang bertanya tentang panduan lengkap, kirimkan link https://s.id/TTE-BidangPersandianRohul.

kalau ada yang nanya formulir surat permohonan atau pengajuan atau rekomendasi bisa bisa kirim link ini untuk di download https://s.id/TTE-BidangPersandianRohul

Jika ada yang bertanya formulir Surat Rekomendasi Permohonan penerbitan sertifikat Elektronik yg sudah di isi bisa dikirm ke link Gform https://forms.gle/yCs5UmLVNaaGEUYm9

Jika pertanyaan di luar topik tersebut, jawab dengan sopan bahwa kamu hanya fokus pada layanan TTE, BSrE, SPBE, dan email dinas.
"""

# --- MENU UTAMA ---
MENU_UTAMA = (
    "📋 Tahapan Registrasi dan Aktivasi Sertifikat Elektronik (SE) Bagi Pemerintah Desa\n\n"
    "1️⃣ Pengisian Formulir Surat Rekomendasi SE\n"
    "(ketik 1 untuk mengunduh formulir pengajuan)\n"
    "2️⃣ Pembuatan Email Dinas (email dinas pribadi dibuat oleh DISKOMINFO Rokan Hulu)\n"
    "3️⃣ Pendaftaran Calon Pengguna oleh Verifikator\n"
    "4️⃣ Aktivasi SE oleh Pengguna meliputi pengisian data\n"
    "5️⃣ Verifikasi Dokumen dan Data oleh Verifikator\n"
    "6️⃣ Pembuatan Passphrase\n"
)

# --- FUNGSI FLOW DASAR ---
def sitanda_flow(message):
    msg = message.strip().lower()

    if msg in ["hi", "halo", "menu", "mulai", "start"]:
        return {"reply": MENU_UTAMA, "mode": "menu"}

    elif msg == "1":
        return {
            "reply": (
                "Tahap 1: Pengisian Formulir Pengajuan SE\n\n"
                f"Unduh formulir pengajuan di tautan berikut: [Formulir Rekomendasi Permohonan]({FORM_TTE_URL})\n"
                "Isi dengan lengkap, lalu kirim melalui tautan: [Formulir Online](https://forms.gle/yCs5UmLVNaaGEUYm9)\n"
                "Tunggu sekitar 1x24 jam. Anda akan menerima balasan melalui WhatsApp berisi email dinas. "
                "Setelah menerima balasan, lanjutkan ke tahap berikutnya."
            ),
            "mode": "menu",
        }

    elif msg == "2":
        return {
            "reply": "📧 Tahap 2: Pembuatan Email Dinas\n\n"
                     "Email dinas dibuat oleh Dinas Kominfo Rokan Hulu untuk masing-masing perangkat desa.\n"
                     "Setelah mendapatkan email dinas dari balasan formulir, Anda dapat mengakses email dinas dengan mengetika mail.rokanhulukab.go.id di browser, "
                     "masukkan email dan kata sandi untuk login.",
            "mode": "menu",
        }

    elif msg == "3":
        return {
            "reply": "👩‍💻 Tahap 3: Pendaftaran Calon Pengguna oleh Verifikator\n\n"
                     "Setelah formulir diterima, verifikator dari Dinas Kominfo akan mendaftarkan calon pengguna "
                     "ke sistem BSrE untuk proses penerbitan Sertifikat Elektronik.",
            "mode": "menu",
        }

    elif msg == "4":
        return {
            "reply": "⚙️Tahap 4: Aktivasi Sertifikat Elektronik oleh Pengguna\n\n"
                     "Pengguna akan menerima email aktivasi dari BSrE.\n"
                     "Langkah-langkahnya:\n"
                     "1️⃣ Buka email aktivasi dari BSrE\n"
                     "2️⃣ Klik tautan aktivasi\n"
                     "3️⃣ Lakukan verifikasi wajah\n"
                     "4️⃣ Isi data pribadi dengan benar\n"
                     "✅ Setelah selesai, akun siap diverifikasi oleh verifikator.",
            "mode": "menu",
        }

    elif msg == "5":
        return {
            "reply": "🧾 Tahap 5: Verifikasi Dokumen dan Data oleh Verifikator\n\n"
                     "Verifikator akan memastikan data dan dokumen yang dikirim sudah sesuai dan valid.\n"
                     "Jika semua data sudah benar, maka proses dapat dilanjutkan ke tahap pembuatan passphrase.",
            "mode": "menu",
        }

    elif msg == "6":
        return {
            "reply": "🔒Tahap 6: Pembuatan Passphrase\n\n"
                     "Passphrase adalah kata sandi rahasia yang digunakan untuk setiap proses penandatanganan elektronik.\n"
                     "Pastikan passphrase mudah diingat, namun tidak mudah ditebak oleh orang lain dan TTE sudah dapat digunakan\n\n",
            "mode": "menu",
        }

    elif "terima kasih" in msg or "makasih" in msg:
        return {"reply": "💙 Sama-sama! Ketik *menu* untuk kembali ke pilihan utama.", "mode": "menu"}

    return None


# --- ROUTE CHAT ---
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "⚠️ Pesan tidak boleh kosong."})

    flow = sitanda_flow(user_message)
    if flow:
        return jsonify(flow)

    try:
        model = genai.GenerativeModel("models/gemini-2.0-flash")
        prompt = f"{PEMBELAJARAN_PROMPT}\n\nPertanyaan pengguna: {user_message}"
        response = model.generate_content(prompt)

        if response and response.text:
            return jsonify({"reply": response.text, "mode": "ask"})
        else:
            raise ValueError("Response kosong dari Gemini")

    except Exception as e:
        print("❌ Error Gemini:", e)
        return jsonify({
            "reply": f"⚠️ Maaf, sistem AI sedang bermasalah. "
                     f"Anda bisa melihat panduan di sini 👉 {PANDUAN_TTE_URL}",
            "mode": "menu"
        })


# --- ROUTE UTAMA UNTUK TES SERVER ---
@app.route("/")
def home():
    return """
    <html>
        <head><title>SITANDA Flask Server</title></head>
        <body style="font-family: Arial; background: #f5f5f5; text-align: center; padding-top: 80px;">
            <h1>✅ Server Flask SITANDA Berjalan dengan Baik</h1>
            <p>Server siap menerima permintaan di endpoint <code>/chat</code>.</p>
            <p>Gunakan POST request ke <code>/chat</code> untuk berinteraksi dengan chatbot.</p>
        </body>
    </html>
    """


# --- MAIN ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
