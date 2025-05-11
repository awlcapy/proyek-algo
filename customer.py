from utils import load_json, save_json, RUANGAN_FILE, CUSTOMER_FILE, ANTRIAN_FILE
from admin import add_to_antrian
from datetime import datetime, date

# Utility functions needed for customer operations
def validate_date(input_date):
    try:
        return datetime.strptime(input_date, "%Y-%m-%d").date()
    except ValueError:
        return None

def get_available_hours(antrian_list, ruangan_id, tanggal):
    booked_hours = [q['jam'] for q in antrian_list 
                   if q['ruangan_id'] == ruangan_id and q['tanggal'] == tanggal]
    return [h for h in range(7, 23) if h not in booked_hours]

def format_time_range(start_hour, duration):
    end_hour = start_hour + duration
    return f"{start_hour:02d}:00-{end_hour:02d}:00"

def view_customer(customer_list):
    if not customer_list:
        print("\nData customer kosong.\n")
        return
    print("\n--- Daftar Customer ---")
    print("{:<5} {:<20} {}".format("ID", "Nama", "Booking (ruangan_id:tanggal:jam)"))
    for c in customer_list:
        bookings = []
        for b in c.get('booking', []):
            booking_str = f"{b['ruangan_id']}:{b['tanggal']}:{b['jam']}"
            bookings.append(booking_str)
        print(f"{c['id']:<5} {c['nama']:<20} {', '.join(bookings)}")
    print()

def view_ruangan(ruangan_list):
    if not ruangan_list:
        print("\nData ruangan masih kosong.\n")
        return
    print("\n--- Daftar Ruangan ---")
    print("{:<5} {:<8} {:<10} {:<25}".format("ID", "Jenis", "Kapasitas", "Console"))
    for r in ruangan_list:
        console_str = ', '.join(r['console'])
        print(f"{r['id']:<5} {r['jenis']:<8} {r['kapasitas']:<10} {console_str:<25}")
    print()

def show_available_ruangan(ruangan_list, antrian_list):
    print("\n--- Ruangan Tersedia per Tanggal dan Jam ---")
    
    # Input tanggal
    while True:
        input_date = input("Tanggal yang ingin dicek (YYYY-MM-DD): ").strip()
        booking_date = validate_date(input_date)
        if booking_date:
            break
        print("Format tanggal salah. Gunakan YYYY-MM-DD.")
    
    print(f"\nRuangan yang tersedia pada {booking_date}:")
    print("{:<5} {:<8} {:<10} {:<15} {:<25}".format(
        "ID", "Jenis", "Kapasitas", "Jam Tersedia", "Console"))
    
    for r in ruangan_list:
        booked_hours = [q['jam'] for q in antrian_list 
                       if q['ruangan_id'] == r['id'] and q['tanggal'] == str(booking_date)]
        available_hours = [h for h in range(7, 23) if h not in booked_hours]
        
        # Format jam tersedia menjadi range yang lebih mudah dibaca
        available_slots = []
        if available_hours:
            start = available_hours[0]
            for i in range(1, len(available_hours)):
                if available_hours[i] != available_hours[i-1] + 1:
                    available_slots.append(f"{start:02d}:00-{available_hours[i-1]+1:02d}:00")
                    start = available_hours[i]
            available_slots.append(f"{start:02d}:00-{available_hours[-1]+1:02d}:00")
        
        console_str = ', '.join(r['console'])
        print(f"{r['id']:<5} {r['jenis']:<8} {r['kapasitas']:<10} "
              f"{', '.join(available_slots):<15} {console_str:<25}")
    print()

def booking_ruangan_online(customer_list, ruangan_list, antrian_list):
    print("\n--- Booking Ruangan Online ---")
    
    # Verifikasi customer
    if not customer_list:
        print("Belum ada data customer, silakan daftar via admin.")
        return
    
    view_customer(customer_list)
    try:
        customer_id = int(input("Masukkan ID customer anda: "))
    except ValueError:
        print("Input harus angka.")
        return
    
    cust = next((c for c in customer_list if c['id'] == customer_id), None)
    if not cust:
        print("Customer tidak ditemukan.")
        return
    
    # Input tanggal booking
    while True:
        input_date = input("Tanggal booking (YYYY-MM-DD): ").strip()
        booking_date = validate_date(input_date)
        if booking_date:
            if booking_date >= date.today():
                break
            print("Tanggal tidak boleh di masa lalu.")
        else:
            print("Format tanggal salah. Gunakan YYYY-MM-DD.")
    
    # Tampilkan ruangan tersedia
    print("\nDaftar Ruangan:")
    view_ruangan(ruangan_list)
    
    try:
        ruangan_id = int(input("Pilih ID ruangan untuk booking: "))
    except ValueError:
        print("Input harus angka.")
        return
    
    selected_room = next((r for r in ruangan_list if r['id'] == ruangan_id), None)
    if not selected_room:
        print("Ruangan tidak ditemukan.")
        return
    
    # Tampilkan jam tersedia
    available_hours = get_available_hours(antrian_list, ruangan_id, str(booking_date))
    
    if not available_hours:
        print(f"Ruangan ini sudah penuh pada tanggal {booking_date}.")
        return
    
    print(f"\nJam tersedia pada {booking_date}:")
    print(", ".join(map(str, available_hours)))
    
    # Input jam dan durasi
    try:
        jam_mulai = int(input("Jam mulai (7-22): "))
        durasi = int(input("Durasi (jam, max 3 jam): "))
        durasi = min(durasi, 3)  # Batasi lebih ketat untuk online booking
    except ValueError:
        print("Input harus angka.")
        return
    
    if jam_mulai < 7 or jam_mulai > 22:
        print("Jam harus antara 7-22.")
        return
    
    if durasi < 1:
        print("Durasi minimal 1 jam.")
        return
    
    # Validasi slot waktu
    selected_hours = range(jam_mulai, jam_mulai + durasi)
    for hour in selected_hours:
        if hour > 22:
            print("Melebihi jam operasional (22:00).")
            return
        if hour not in available_hours:
            print(f"Jam {hour} sudah dipesan.")
            return
    
    # Tambahkan booking ke customer
    booking_entries = [{
        'ruangan_id': ruangan_id,
        'tanggal': str(booking_date),
        'jam': hour
    } for hour in selected_hours]
    
    cust.setdefault('booking', []).extend(booking_entries)
    
    # Tambahkan ke antrian
    for hour in selected_hours:
        add_to_antrian(antrian_list, customer_id, ruangan_id, str(booking_date), hour, online=True)
    
    save_json(CUSTOMER_FILE, customer_list)
    save_json(ANTRIAN_FILE, antrian_list)
    
    print("\n=== Booking Berhasil ===")
    print(f"Customer: {cust['nama']}")
    print(f"Ruangan: {selected_room['jenis']} (ID: {ruangan_id})")
    print(f"Tanggal: {booking_date}")
    print(f"Waktu: {format_time_range(jam_mulai, durasi)}")
    print("Status: Online Booking\n")

def customer_menu():
    ruangan_list = load_json(RUANGAN_FILE)
    customer_list = load_json(CUSTOMER_FILE)
    antrian_list = load_json(ANTRIAN_FILE)

    while True:
        print("\n=== MENU CUSTOMER ===")
        print("1. Lihat Ruangan Tersedia per Jam")
        print("2. Booking Ruangan Online")
        print("0. Kembali ke Menu Utama")
        choice = input("Pilih menu: ")

        if choice == '1':
            show_available_ruangan(ruangan_list, antrian_list)
        elif choice == '2':
            booking_ruangan_online(customer_list, ruangan_list, antrian_list)
        elif choice == '0':
            break
        else:
            print("Pilihan tidak valid.")
        save_json(CUSTOMER_FILE, customer_list)
        save_json(ANTRIAN_FILE, antrian_list)