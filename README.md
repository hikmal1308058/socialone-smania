# 🏫 Socialone Smania — XII IPS 1 SMAN 14 Pandeglang

Website kelas fullstack dengan Flask + SQLite.

---

## 📁 Struktur Folder

```
socialone/
├── app.py                  ← Backend utama (Flask)
├── requirements.txt        ← Daftar library Python
├── socialone.db            ← Database (auto-dibuat)
├── templates/
│   └── index.html          ← Halaman utama
└── static/
    ├── photos/             ← Foto profil siswa
    └── gallery/            ← Foto galeri kelas
```

---

## 🚀 Cara Menjalankan

### 1. Install Python (jika belum)
Download di: https://python.org/downloads

### 2. Buat virtual environment (disarankan)
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Jalankan aplikasi
```bash
python app.py
```

### 5. Buka di browser
```
http://localhost:5000
```

---

## ✨ Fitur

| Fitur | Keterangan |
|-------|-----------|
| 👥 Daftar Anggota | 33 siswa lengkap dengan foto & peran |
| 📸 Upload Foto Profil | Hover kartu siswa → klik "Ganti Foto" |
| 🖼️ Galeri Foto | Upload foto kenangan kelas, bisa hapus |
| 💬 Komentar/Pesan | Klik tombol "Pesan" di kartu siswa |
| 🏆 Prestasi | Daftar penghargaan kelas |

---

## 📸 Cara Tambah Foto Profil Siswa

Taruh foto di folder `static/photos/` dengan nama:
- `1.jpg` → Rivan (id 1)
- `2.jpg` → Waseh (id 2)
- `hikmal1.jpeg` → bisa juga nama custom, edit di `app.py`

Atau langsung klik kartu siswa di website untuk upload!

---

## 🌐 Deploy ke Internet (Gratis)

### Opsi 1: Railway.app
1. Daftar di railway.app
2. Klik "New Project" → "Deploy from GitHub"
3. Push kode ke GitHub dulu
4. Railway otomatis detect Flask dan deploy!

### Opsi 2: Render.com
1. Daftar di render.com
2. New → Web Service → connect GitHub repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `python app.py`

### Opsi 3: PythonAnywhere (mudah untuk pemula)
1. Daftar di pythonanywhere.com (gratis)
2. Upload semua file
3. Ikuti panduan Flask di dashboard mereka

---

## 🔧 Pindah ke MySQL (opsional)

Ganti baris ini di `app.py`:
```python
# Dari SQLite:
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///socialone.db'

# Ke MySQL:
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@localhost/socialone_db'
```

Install tambahan: `pip install pymysql`

---

## 💡 Tips

- Database SQLite otomatis dibuat saat pertama jalan
- Data 33 siswa otomatis ter-seed
- Upload foto maks 5 MB per file
- Format foto: JPG, PNG, WEBP, GIF
