# Import modul yang diperlukan
import json  # Untuk bekerja dengan file JSON
import os    # Untuk operasi sistem file

# Nama file untuk menyimpan kredensial admin
ADMIN_FILE = 'admin.json'

# Fungsi untuk memuat kredensial admin
def load_admin_credentials():
    # Kredensial admin default jika file tidak ada
    default_admin = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # Mencoba membuka dan membaca file admin
        with open(ADMIN_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Jika file tidak ditemukan atau error baca JSON,
        # buat file baru dengan kredensial default
        with open(ADMIN_FILE, 'w') as f:
            json.dump(default_admin, f, indent=4)
        return default_admin

# Fungsi untuk menyimpan kredensial admin
def save_admin_credentials(credentials):
    with open(ADMIN_FILE, 'w') as f:
        json.dump(credentials, f, indent=4)  # indent=4 untuk format yang rapi

# Konstanta nama file untuk penyimpanan data
RUANGAN_FILE = 'ruangan.json'         # File data ruangan
CUSTOMER_FILE = 'customer.json'       # File data customer
HISTORY_FILE = 'riwayat.json'         # File riwayat transaksi
ONLINE_FILE ='online_bookings.json'   # File booking online
QUEUE_FILE = 'queue_today.json'       # File antrian hari ini

# Fungsi untuk memuat data dari file JSON
def load_json(file_name):
    # Jika file tidak ada, kembalikan list kosong
    if not os.path.isfile(file_name):
        return []
    
    # Buka file dan baca isinya
    with open(file_name, 'r') as f:
        try:
            return json.load(f)  # Parse data JSON
        except json.JSONDecodeError:
            return []  # Jika error parsing, kembalikan list kosong

# Fungsi untuk menyimpan data ke file JSON
def save_json(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)  # Simpan dengan format rapi

# Fungsi untuk menghasilkan ID berikutnya
def next_id(data_list):
    # Jika list kosong, mulai dari ID 1
    if not data_list:
        return 1
    # Ambil ID tertinggi dari list dan tambah 1
    return max(item['id'] for item in data_list) + 1