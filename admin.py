from utils import load_json, save_json, next_id, RUANGAN_FILE, CUSTOMER_FILE, HISTORY_FILE, ONLINE_FILE, QUEUE_FILE
from datetime import datetime, date
import os
import sys
import time

# bagian UI/UX untuk clear screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# untuk delay text supaya terkesan seperti animasi
def typewriter(text, delay=0.001):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# import fungsi dari auth.py untuk mengubah password admin
def manage_admin_account():
    from auth import change_admin_password
    change_admin_password()

# validasi data input (tahun, bulan, dan hari)
def validate_date(input_date):
    try:
        return datetime.strptime(input_date, "%Y-%m-%d").date()
    except ValueError:
        return None

# fungsi untuk mengecek ketersediaan jam (apabila jam di ruangan & tanggal itu sudah di booking, maka tidak akan muncul dalam pilihan)
def get_available_hours(history_list, ruangan_id, tanggal):
    booked_hours = [q['jam'] for q in history_list 
                   if q['ruangan_id'] == ruangan_id and q['tanggal'] == tanggal]
    return [h for h in range(7, 23) if h not in booked_hours]

def format_time_range(start_hour, duration):
    end_hour = start_hour + duration
    return f"{start_hour:02d}:00-{end_hour:02d}:00"

# --- OPRASI UNTUK RUANGAN ---

# fungsi untuk menambah ruangan
def add_ruangan(ruangan_list):
    clear_screen()
    print("\033[1;36m" + "═"*50)
    print(" "*20 + "➕ TAMBAH RUANGAN")
    print("═"*50 + "\033[0m")
    
    print("\n\033[1;34mPilih Jenis Ruangan:\033[0m")
    print("\033[1;32m1. 🎮 Regular Room (Kapasitas: 2)\033[0m")
    print("\033[1;33m2. 💎 VIP Room (Kapasitas: 3)\033[0m")
    print("\033[1;35m3. ✨ VVIP Room (Kapasitas: 6)\033[0m")
    
    jenis_options = {1: 'Regular', 2: 'VIP', 3: 'VVIP'} #memilih jenis ruangan
    while True:
        try:
            jenis_choice = int(input("\n\033[1;34m⌨ Pilih jenis ruangan (1-3): \033[0m")) #user input jenis ruangan (1-3)
            if jenis_choice in jenis_options:
                jenis = jenis_options[jenis_choice]
                break
            else:
                print("\033[1;31m❌ Pilihan tidak valid! Harap pilih 1-3.\033[0m") # apabila input tidak valid
        except ValueError:
            print("\033[1;31m❌ Input harus berupa angka!\033[0m") # apabila input tidak berupa angka

    # pilihan ruangan sesuai input, beserta pilihan jenis consolenya
    if jenis == 'Regular':
        kapasitas = 2
        console_options = ['PS4', 'PS5']
    elif jenis == 'VIP':
        kapasitas = 3
        console_options = ['Nintendo Switch', 'PS5']
    else:  # VVIP
        kapasitas = 6
        console_options = ['Nintendo Switch', 'PS5']

    print("\n\033[1;34m🕹️ Console yang tersedia:\033[0m")
    for i, c in enumerate(console_options, 1):
        print(f"\033[1;33m{i}. {c}\033[0m") # menampilkan console yang tersedia
    
    chosen_console = []
    while True:
        choices = input("\n\033[1;34m🎮 Pilih console (pisahkan dengan koma jika lebih dari satu): \033[0m") # user input console sesuai yang ditampilkan
        try:
            nums = [int(x.strip()) for x in choices.split(',') if x.strip()]
            valid = all(1 <= n <= len(console_options) for n in nums)
            if not valid:
                print("\033[1;31m❌ Pilihan tidak valid! Harap pilih angka yang tersedia.\033[0m")
                continue
            chosen_console = [console_options[n-1] for n in nums]
            break
        except ValueError:
            print("\033[1;31m❌ Input harus berupa angka! Pisahkan dengan koma jika memilih lebih dari satu.\033[0m")

    # SIMPAN DATA RUANGAN
    ruangan_id = next_id(ruangan_list)
    new_room = {
        'id': ruangan_id,
        'jenis': jenis,
        'kapasitas': kapasitas,
        'console': chosen_console
    }
    ruangan_list.append(new_room)
    save_json(RUANGAN_FILE, ruangan_list) # simpan data di ruangan.json
    
    # ruangan berhasil ditambah
    print("\n\033[1;32m✓ Ruangan berhasil ditambahkan!\033[0m")
    print(f"\033[1;36mID Ruangan: {ruangan_id}")
    print(f"Jenis: {jenis}")
    print(f"Kapasitas: {kapasitas} orang")
    print(f"Console: {', '.join(chosen_console)}\033[0m\n")
    time.sleep(1.5)

# fungsi lihat ruangan
def view_ruangan(ruangan_list):
    clear_screen()
    print("\033[1;36m" + "═"*50)
    print(" "*20 + "📋 DAFTAR RUANGAN")
    print("═"*50 + "\033[0m")
    
    if not ruangan_list:
        print("\n\033[1;31m⚠ Tidak ada ruangan yang tersedia!\033[0m\n")
        time.sleep(1)
        return
    
    # menampilkan ruangan yang tersedia
    print("\n\033[1;35m{:<5} {:<10} {:<12} {:<25}\033[0m".format(
        "ID", "Jenis", "Kapasitas", "Console"))
    print("\033[1;34m" + "-"*52 + "\033[0m")
    
    for r in ruangan_list:
        console_str = ', '.join(r['console'])
        print("\033[1;32m{:<5}\033[0m {:<10} {:<12} \033[1;33m{:<25}\033[0m".format(
            r['id'], r['jenis'], f"{r['kapasitas']} orang", console_str))
    
    print("\033[1;34m" + "-"*52 + "\033[0m\n")
    time.sleep(1)

#fungsi edit data ruangan
def edit_ruangan(ruangan_list):
    view_ruangan(ruangan_list) #menampilkan ruangan yang tersedia di database
    if not ruangan_list:
        return
    
    try:
        ruangan_id = int(input("\n\033[1;34m⌨ Masukkan ID ruangan yang ingin diedit: \033[0m")) # input id ruangan
    except ValueError:
        print("\033[1;31m❌ Input harus berupa angka!\033[0m")
        time.sleep(1)
        return
    
    room = next((r for r in ruangan_list if r['id'] == ruangan_id), None) # mencari id ruangan
    if not room:
        print("\033[1;31m❌ Ruangan tidak ditemukan!\033[0m") # apabila id ruangan tidak ditemukan
        time.sleep(1)
        return
    
    print(f"\n\033[1;36m✏ Mengedit Ruangan ID {ruangan_id}\033[0m")
    print("\033[1;35m" + "-"*50 + "\033[0m")
    
    jenis_options = ['Regular', 'VIP', 'VVIP']
    jenis_input = input(f"\033[1;34mJenis ruangan ({room['jenis']}) [kosongkan jika tidak berubah]: \033[0m").strip() # user bisa mengedit jenis ruangan
    if jenis_input:
        if jenis_input in jenis_options:
            room['jenis'] = jenis_input
            print("\033[1;32m✓ Jenis ruangan diperbarui\033[0m")
        else:
            print("\033[1;31m❌ Jenis ruangan tidak valid! (Regular/VIP/VVIP)\033[0m")

    kapasitas_input = input(f"\033[1;34mKapasitas ({room['kapasitas']}) [kosongkan jika tidak berubah]: \033[0m").strip() # user bisa mengedit kapasitas ruangan
    if kapasitas_input:
        try:
            k = int(kapasitas_input)
            if k > 0:
                room['kapasitas'] = k
                print("\033[1;32m✓ Kapasitas diperbarui\033[0m")
            else:
                print("\033[1;31m❌ Kapasitas harus lebih dari 0!\033[0m")
        except ValueError:
            print("\033[1;31m❌ Input harus berupa angka!\033[0m")

    console_input = input(f"\033[1;34mConsole ({', '.join(room['console'])}) [pisahkan dengan koma, kosongkan jika tidak berubah]: \033[0m").strip() # user bisa mengedit console yang tersedia
    if console_input:
        consoles = [c.strip() for c in console_input.split(',') if c.strip()]
        if consoles:
            room['console'] = consoles
            print("\033[1;32m✓ Console diperbarui\033[0m")
        else:
            print("\033[1;31m❌ Daftar console tidak boleh kosong!\033[0m")
    
    save_json(RUANGAN_FILE, ruangan_list) # menyimpan data ruangan yang telah diedit ke file ruangan.json
    print("\n\033[1;32m✓ Data ruangan berhasil diperbarui!\033[0m") # data berhasil di perbaharui
    time.sleep(1.5)

# fungsi untuk menghapus ruangan
def delete_ruangan(ruangan_list, history_list, customer_list):
    view_ruangan(ruangan_list) #menampilkan ruangan yang tersedia di database
    if not ruangan_list:
        return
    
    try:
        ruangan_id = int(input("\n\033[1;34m⌨ Masukkan ID ruangan yang ingin dihapus: \033[0m")) #input id ruangan yang diingin dihapus
    except ValueError:
        print("\033[1;31m❌ Input harus berupa angka!\033[0m")
        time.sleep(1)
        return
    
    room = next((r for r in ruangan_list if r['id'] == ruangan_id), None) #mencari id ruangan yang diinpu
    if not room:
        print("\033[1;31m❌ Ruangan tidak ditemukan!\033[0m")
        time.sleep(1)
        return
    
    booked = any(q['ruangan_id'] == ruangan_id for q in history_list) #cek apakah terdapat booking aktif
    if booked:
        print("\033[1;31m❌ Ruangan ini memiliki booking aktif dan tidak dapat dihapus!\033[0m") #jika iya, maka ruangan tidak dapat dihapus
        time.sleep(1.5)
        return
    
    # konfirmasi penghapusan
    print(f"\n\033[1;31m⚠ ANDA AKAN MENGHAPUS:\033[0m")
    print(f"\033[1;33mID: {room['id']}")
    print(f"Jenis: {room['jenis']}")
    print(f"Kapasitas: {room['kapasitas']} orang")
    print(f"Console: {', '.join(room['console'])}\033[0m")
    
    confirm = input("\n\033[1;31mApakah Anda yakin? (y/n): \033[0m").lower() #konfimrasi (yes/no)
    if confirm != 'y':
        print("\033[1;33m🛑 Penghapusan dibatalkan\033[0m") #apabila input selain y, penghapusan dibatalkan
        time.sleep(1)
        return
    
    for cust in customer_list:
        cust['booking'] = [b for b in cust.get('booking', []) if b['ruangan_id'] != ruangan_id]
    
    ruangan_list.remove(room) #hapus ruangan 
    save_json(RUANGAN_FILE, ruangan_list)
    save_json(CUSTOMER_FILE, customer_list) #simpan data terbaru (setelah dihapus)
    
    print("\n\033[1;32m✓ Ruangan berhasil dihapus!\033[0m")
    time.sleep(1.5)

#fungsi monitor customer hari ini
def monitor_today_customers(customer_list, ruangan_list):
    """Monitor today's customers with status management"""
    clear_screen()
    print("\033[1;36m" + "═"*80)
    print(" "*25 + "👥 MONITOR CUSTOMER HARI INI")
    print("═"*80 + "\033[0m")
    
    #ambil file queue
    try:
        queue_today = load_json(QUEUE_FILE)
    except FileNotFoundError:
        queue_today = []
    
    today = datetime.now().strftime('%Y-%m-%d') #definisikan hari ini
    today_bookings = [q for q in queue_today if q['tanggal'] == today]  #definisikan booking hari ini
    
    if not today_bookings:
        print("\n\033[1;31m⚠ Tidak ada booking untuk hari ini!\033[0m\n")
        input("\n\033[1;36mTekan Enter untuk kembali...\033[0m")
        return
    
    # Sort by status priority (Sedang Bermain -> Belum Masuk -> Selesai) then by time
    today_bookings.sort(key=lambda x: (
        {'sedang_bermain': 0, 'belum_masuk': 1, 'selesai': 2}.get(x.get('status', 'belum_masuk')),
        x['jam_mulai']
    ))
    
    # Print table header
    print("\n\033[1;35m{:<10} {:<25} {:<15} {:<15} {:<20} {:<10}\033[0m".format( 
        "id", "Nama Customer", "Jam Booking", "Ruangan", "Status", "Aksi"))
    print("\033[1;34m" + "─"*90 + "\033[0m")
    
    for booking in today_bookings:
        #dapatkan info customer
        customer = next((c for c in customer_list if c['id'] == booking['customer_id']), None)
        customer_id = customer['id'] if customer else "Unknown"
        customer_name = customer['nama'] if customer else "Unknown"
        
        #dapatkan info ruangan
        room = next((r for r in ruangan_list if r['id'] == booking['ruangan_id']), None)
        room_name = f"{room['jenis']} {room['id']}" if room else "Unknown"
        
        # Format waktu
        time_range = f"{booking['jam_mulai']:02d}:00-{(booking['jam_mulai']+booking['durasi']):02d}:00"
        
        # Status display
        status = booking.get('status', 'belum_masuk')
        if status == 'belum_masuk':
            status_display = "\033[1;33m✅ Belum Masuk\033[0m"
            action = "[Masuk Ruangan]"
        elif status == 'sedang_bermain':
            status_display = "\033[1;32m🟢 Sedang Bermain\033[0m"
            action = "[Selesai]"
        else:
            status_display = "\033[1;31m🔴 Selesai\033[0m"
            action = "-"
        
        # Highlight status "sedang bermain"
        row_prefix = "\033[1;42m" if status == 'sedang_bermain' else ""
        row_suffix = "\033[0m" if status == 'sedang_bermain' else ""
        
        print(f"{row_prefix}{customer_id:<10} {customer_name:<25} {time_range:<15} {room_name:<15} {status_display:<20} {action:<10}{row_suffix}")
    
    print("\033[1;34m" + "─"*90 + "\033[0m")
    
    # Action menu
    print("\n\033[1;34mPilih Aksi:\033[0m")
    print("\033[1;32m1. Update Status Customer")
    print("\033[1;33m0. Kembali ke Menu Utama\033[0m")
    
    #update status customer
    while True:
        choice = input("\n\033[1;34m⌨ Pilihan Anda (0-1): \033[0m")
        if choice == '1':
            update_booking_status(queue_today, customer_list)
            break
        elif choice == '0':
            break
        else:
            print("\033[1;31m❌ Pilihan tidak valid!\033[0m")

#fungsi update status customer       
def update_booking_status(queue_today, customer_list):
    """Update booking status (belum_masuk -> sedang_bermain -> selesai)"""
    try:
        customer_id = int(input("\n\033[1;34m⌨ Masukkan ID Customer yang akan diupdate: \033[0m")) #input id customer hari ini yang ingin diupdate
    except ValueError:
        print("\033[1;31m❌ ID harus berupa angka!\033[0m")
        time.sleep(1)
        return
    
    booking = next((q for q in queue_today if q['customer_id'] == customer_id), None) #ambil data id customer yg dicari
    if not booking:
        print("\033[1;31m❌ Booking tidak ditemukan!\033[0m")
        time.sleep(1)
        return
    
    customer = next((c for c in customer_list if c['id'] == customer_id), None)
    if not customer:
        print("\033[1;31m❌ Customer tidak ditemukan!\033[0m")
        time.sleep(1)
        return
    
    current_status = booking.get('status', 'belum_masuk')
    
    #update status dan aksi
    if current_status == 'belum_masuk':
        new_status = 'sedang_bermain'
        action = "masuk ruangan"
    elif current_status == 'sedang_bermain':
        new_status = 'selesai'
        action = "selesai bermain"
    else: #SELESAI
        print("\033[1;31m❌ Status sudah selesai, tidak bisa diubah!\033[0m") #jika statusnya selesai, maka status tidak bisa diubah
        time.sleep(1)
        return
    
    #konfirmasi update status
    confirm = input(f"\n\033[1;34mKonfirmasi {action} untuk {customer['nama']}? (y/n): \033[0m").lower()
    if confirm == 'y':
        booking['status'] = new_status
        save_json(QUEUE_FILE, queue_today)
        print("\033[1;32m✓ Status berhasil diupdate!\033[0m")
    else:
        print("\033[1;33m✖ Update dibatalkan\033[0m")
    
    time.sleep(1)

#menghapus queue status customer hari ini
def cleanup_queue_today():
    """Bersihkan hanya booking dari hari sebelumnya (jika ada)"""
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        queue = load_json(QUEUE_FILE)
        # Hanya hapus data yang BUKAN hari ini (expired)
        updated = [q for q in queue if q['tanggal'] == today]
        if len(updated) != len(queue):
            save_json(QUEUE_FILE, updated)
    except FileNotFoundError:
        pass

#fungsi menambah customer
def add_customer(customer_list, ruangan_list, history_list):
    clear_screen()
    # Header 
    print("\033[1;36m" + "═"*60)
    print(" "*20 + "🌟 TAMBAH CUSTOMER BARU")
    print("═"*60 + "\033[0m")

    # --- SECTION 1: CUSTOMER DETAILS ---
    print("\n\033[1;34m📝 DATA CUSTOMER\033[0m")
    print("\033[1;35m" + "─"*60 + "\033[0m")

    #input nama dengan mengecek duplikat nama
    while True:
        nama = input("\033[1;34m⌨ Nama Customer: \033[0m").strip()
        if not nama:
            print("\033[1;31m❌ Nama tidak boleh kosong!\033[0m")
            continue
            
        # cek apakah input nama duplikat
        duplicates = [c for c in customer_list if c['nama'].lower() == nama.lower()]
        if duplicates:
            print("\n\033[1;33m⚠️ Peringatan: Nama sudah terdaftar!\033[0m")
            print("\033[1;35m" + "─"*40 + "\033[0m")
            for dup in duplicates:
                booking_count = len(dup.get('booking', []))
                print(f"\033[1;36mID: {dup['id']}\033[0m | Booking: \033[1;33m{booking_count}x\033[0m")
            print("\033[1;35m" + "─"*40 + "\033[0m")
            #jika nama tersebut adalah orang yang sama, data akan ditambhakan ke id lama, sedangkan jika berbeda orang, akan dibuat id baru
            confirm = input("\n\033[1;34mTetap buat customer baru? (y/t): \033[0m").lower() 
            if confirm != 'y':
                print("\033[1;33m✖ Proses dibatalkan\033[0m")
                time.sleep(1)
                return None
        break

    # --- SECTION 2: BOOKING DETAILS ---
    print("\n\033[1;34m📅 DETAIL BOOKING\033[0m")
    print("\033[1;35m" + "─"*60 + "\033[0m")

    # input data dengan validasi
    while True:
        input_date = input("\033[1;34m⌨ Tanggal booking (YYYY-MM-DD): \033[0m").strip()
        booking_date = validate_date(input_date)
        if not booking_date:
            print("\033[1;31m❌ Format tanggal salah. Gunakan format YYYY-MM-DD\033[0m")
            continue
        if booking_date < date.today():
            print("\033[1;31m❌ Tanggal tidak boleh di masa lalu!\033[0m")
            continue
        break

    # menampilkan ruangan
    print("\n\033[1;34m🏠 PILIH RUANGAN\033[0m")
    view_ruangan(ruangan_list)
    
    try:
        ruangan_id = int(input("\n\033[1;34m⌨ Masukkan ID ruangan: \033[0m")) #input id ruangan
    except ValueError:
        print("\033[1;31m❌ Harap masukkan angka ID ruangan!\033[0m")
        time.sleep(1.5)
        return None

    selected_room = next((r for r in ruangan_list if r['id'] == ruangan_id), None)
    if not selected_room:
        print("\033[1;31m❌ Ruangan tidak ditemukan! Silakan cek ID yang tersedia.\033[0m")
        time.sleep(1.5)
        return None

    # tampilan ruangan yang dipilih
    print("\n\033[1;32m✓ RUANGAN DIPILIH:\033[0m")
    print("\033[1;36m" + "─"*40 + "\033[0m")
    print(f"\033[1;33mTipe     : {selected_room['jenis']}")
    print(f"ID       : {ruangan_id}")
    print(f"Kapasitas: {selected_room['kapasitas']} orang")
    print(f"Console  : {', '.join(selected_room['console'])}\033[0m")
    print("\033[1;36m" + "─"*40 + "\033[0m")

    # menampilkan jam yang tersedia
    available_hours = get_available_hours(history_list, ruangan_id, str(booking_date))
    if not available_hours:
        print(f"\n\033[1;31m❌ Ruangan penuh pada {booking_date}!\033[0m")
        time.sleep(1.5)
        return None

    # menampilkan jam yang tersedia
    print(f"\n\033[1;34m⏰ JAM TERSEDIA ({booking_date})\033[0m")
    print("\033[1;35m" + "─"*50 + "\033[0m")
    for i, hour in enumerate(available_hours, 1):
        print(f"\033[1;33m{i:>2}. {hour:02d}:00 - {hour+1:02d}:00\033[0m")
    print("\033[1;35m" + "─"*50 + "\033[0m")

    #pilih jam 
    while True:
        try:
            choice = int(input("\n\033[1;34m⌨ Pilih jam mulai (nomor): \033[0m"))
            if 1 <= choice <= len(available_hours):
                jam_mulai = available_hours[choice - 1]
                break
            else:
                print(f"\033[1;31m❌ Harap pilih nomor antara 1 - {len(available_hours)}!\033[0m")
        except ValueError:
            print("\033[1;31m❌ Input tidak valid!\033[0m")

    #pilih durasi
    while True:
        try:
            durasi = int(input("\033[1;34m⌨ Mau booking berapa jam?: \033[0m"))
            if durasi < 1:
                print("\033[1;31m❌ Durasi minimal 1 jam!\033[0m")
                continue
            selected_hours = range(jam_mulai, jam_mulai + durasi)
            if jam_mulai + durasi > 23:
                print("\033[1;31m❌ Melebihi jam operasional (22:00)!\033[0m")
                continue
            if all(hour in available_hours for hour in selected_hours):
                break
            else:
                print("\033[1;31m❌ Salah satu jam sudah dibooking. Coba durasi lebih pendek!\033[0m")
        except ValueError:
            print("\033[1;31m❌ Input tidak valid!\033[0m")


    # validasi jam dan durasi apakah sudah dibooking atau melebihi batas
    selected_hours = range(jam_mulai, jam_mulai + durasi)
    for hour in selected_hours:
        if hour > 22:
            print("\033[1;31m❌ Melebihi jam operasional (22:00)!\033[0m")
            time.sleep(1)
            return None
        if hour not in available_hours:
            print(f"\033[1;31m❌ Jam {hour:02d}:00 sudah dipesan!\033[0m")
            time.sleep(1)
            return None

    # --- SECTION 3: CONFIRMATION ---
    print("\n\033[1;34m🔍 RINGKASAN BOOKING\033[0m")
    print("\033[1;36m" + "═"*60 + "\033[0m")
    print(f"\033[1;33m{'Nama':<10}: {nama}")
    print(f"{'Ruangan':<10}: {selected_room['jenis']} (ID: {ruangan_id})")
    print(f"{'Tanggal':<10}: {booking_date}")
    print(f"{'Jam':<10}: {jam_mulai:02d}:00-{jam_mulai+durasi:02d}:00")
    print(f"{'Durasi':<10}: {durasi} jam\033[0m")
    print("\033[1;36m" + "═"*60 + "\033[0m")

    #konfirmasi
    confirm = input("\n\033[1;34mKonfirmasi booking? (y/n): \033[0m").lower()
    if confirm != 'y':
        print("\033[1;33m⚠️ Booking dibatalkan\033[0m")
        time.sleep(1)
        return None

    # --- SECTION 4: SAVE DATA ---
    cust_id = next_id(customer_list)
    new_customer = {
        'id': cust_id,
        'nama': nama,
        'booking': [{
            'ruangan_id': ruangan_id,
            'tanggal': str(booking_date),
            'jam': hour,
            'online': False
        } for hour in selected_hours]
    }
    customer_list.append(new_customer)

    for hour in selected_hours:
        add_to_history(history_list, cust_id, ruangan_id, str(booking_date), hour, False)

    today = datetime.now().strftime('%Y-%m-%d')
    if str(booking_date) == today:
        try:
            queue_today = load_json(QUEUE_FILE)
        except FileNotFoundError:
            queue_today = []
            
        new_booking = {
            'customer_id': cust_id,
            'ruangan_id': ruangan_id,
            'tanggal': str(booking_date),
            'jam_mulai': jam_mulai,
            'durasi': durasi,
            'status': 'belum_masuk',
            'waktu_booking': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        queue_today.append(new_booking)
        save_json(QUEUE_FILE, queue_today)


    save_json(CUSTOMER_FILE, customer_list)
    save_json(HISTORY_FILE, history_list) #simpan data di file json

    # menampilkan ringkasan booking
    print("\n\033[1;32m" + "═"*60)
    print(" "*20 + "✅ BOOKING BERHASIL!")
    print("═"*60 + "\033[0m")
    print(f"\033[1;36m{'ID Customer':<15}: {cust_id}")
    print(f"{'Nama':<15}: {nama}")
    print(f"{'Ruangan':<15}: {selected_room['jenis']} (ID: {ruangan_id})")
    print(f"{'Tanggal':<15}: {booking_date}")
    print(f"{'Waktu':<15}: {jam_mulai:02d}:00-{jam_mulai+durasi:02d}:00\033[0m")
    print("\033[1;32m" + "═"*60 + "\033[0m")
    
    time.sleep(3)
    return cust_id

#fungsi lihat customer
def view_customer(customer_list, ruangan_list):
    # Dapatkan tanggal hari ini
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Filter customer yang memiliki booking hari ini
    today_customers = []
    for customer in customer_list:
        today_bookings = [
            booking for booking in customer.get('booking', [])
            if booking.get('tanggal') == today
        ]
        
        if today_bookings:
            # Hitung waktu mulai dan selesai
            jam_list = sorted([b['jam'] for b in today_bookings])
            jam_mulai = min(jam_list)
            jam_selesai = max(jam_list) + 1
            durasi = jam_selesai - jam_mulai
            
            # Dapatkan info ruangan
            room_id = today_bookings[0]['ruangan_id']
            room = next((r for r in ruangan_list if r['id'] == room_id), None)
            tipe = room['jenis'] if room else 'Unknown'
            
            # Tentukan status
            status = "Online" if any(b.get('online', False) for b in today_bookings) else "Offline"
            
            today_customers.append({
                'id': customer['id'],
                'nama': customer['nama'],
                'ruangan': room_id,
                'tipe': tipe,
                'jam_mulai': jam_mulai,
                'jam_selesai': jam_selesai,
                'durasi': durasi,
                'status': status
            })
    
    # Tampilkan header
    print("\n\033[1;36m╔══════════════════════════════════════════════════════════════════════════════════╗")
    print("║" + " " * 27 + "📋 DAFTAR CUSTOMER HARI INI" + " " * 28 + "║")
    print("╚══════════════════════════════════════════════════════════════════════════════════╝\033[0m")
    
    if not today_customers:
        print("\n\033[1;31mTidak ada booking untuk hari ini.\033[0m\n")
        return
    
    # Definisi lebar kolom yang disesuaikan
    col_width = {
        'id': 5,
        'nama': 20, 
        'ruangan': 10,
        'tipe': 18,
        'waktu': 19,
        'durasi': 8,  # Lebar untuk "X jam"
        'status': 10  # Lebar untuk status
    }

    # Header tabel dengan alignment yang tepat
    header = (
        f"\033[1;35m{'ID':<{col_width['id']}} "
        f"{'Nama':<{col_width['nama']}} "
        f"{'Ruangan':<{col_width['ruangan']}} "
        f"{'Tipe Ruangan':<{col_width['tipe']}} "
        f"{'Waktu Booking':<{col_width['waktu']}} "
        f"{'Durasi':^{col_width['durasi']}} "
        f"{'Status':^{col_width['status']}}\033[0m"
    )

    
    print(header)
    print("\033[1;34m" + "─" * (sum(col_width.values()) + 6) + "\033[0m")
    
    # Tampilkan data
    for customer in today_customers:
        time_range = f"{customer['jam_mulai']:02d}:00-{customer['jam_selesai']:02d}:00"
        color = '32' if customer['status'] == "Online" else '31'
        durasi_text = f"{customer['durasi']} jam" 
        
        # Perbaikan bagian formatting row
        row = (
            f"\033[1;32m{customer['id']:<{col_width['id']}}\033[0m "
            f"\033[1;33m{customer['nama']:<{col_width['nama']}}\033[0m "
            f"\033[1;36m{customer['ruangan']:<{col_width['ruangan']}}\033[0m "
            f"{customer['tipe']:<{col_width['tipe']}} "
            f"\033[1;35m{time_range:<{col_width['waktu']}}\033[0m "
            f"{durasi_text:<{col_width['durasi']}}"  # Center align durasi
            f"\033[1;{color}m{customer['status']:^{col_width['status']}}\033[0m"  # Center align status
        ).format(
            id=customer['id'],
            nama=customer['nama'],
            ruangan=customer['ruangan'],
            tipe=customer['tipe'],
            waktu=time_range,
            durasi=customer['durasi'],
            status=customer['status'],
            color=color,
            id_w=col_width['id'],
            nama_w=col_width['nama'],
            ruangan_w=col_width['ruangan'],
            tipe_w=col_width['tipe'],
            waktu_w=col_width['waktu'],
            durasi_w=col_width['durasi']-5,  # dikurangi untuk menyesuaikan dengan teks " jam"
            status_w=col_width['status']
        )

        print(row)

    print("\033[1;34m" + "─" * (sum(col_width.values()) + 6) + "\033[0m")

def view_online_bookings(ruangan_list):
    """Menampilkan daftar booking online dengan format tabel"""
    try:
        online_bookings = load_json(ONLINE_FILE)
    except FileNotFoundError:
        online_bookings = []
    
    clear_screen()
    print("\033[1;36m" + "═"*80)
    print(" "*25 + "📱 BOOKING ONLINE")
    print("═"*80 + "\033[0m")
    
    if not online_bookings:
        print("\n\033[1;31m⚠ Tidak ada booking online yang tersedia!\033[0m\n")
        time.sleep(1)
        return
    
    # Urutkan berdasarkan tanggal dan jam
    sorted_bookings = sorted(online_bookings, key=lambda x: (x['tanggal'], x['jam_mulai']))
    
    # Header tabel
    print("\n\033[1;35m{:<5} {:<15} {:<15} {:<12} {:<20} {:<15}\033[0m".format(
        "ID", "Nama", "Telepon", "Ruangan", "Tanggal & Waktu", "Status"))
    print("\033[1;34m" + "─"*80 + "\033[0m")
    
    for booking in sorted_bookings:
        # Dapatkan info ruangan
        room = next((r for r in ruangan_list if r['id'] == booking['ruangan_id']), None)
        room_type = room['jenis'] if room else "Unknown"
        
        # Format waktu
        waktu = f"{booking['jam_mulai']:02d}:00-{booking['jam_mulai']+booking['durasi']:02d}:00"
        
        # Warna status
        status_color = "32" if booking['status'] == "confirmed" else "33"  # Hijau untuk confirmed, kuning untuk lainnya
        
        print("{:<5} \033[1;33m{:<15}\033[0m {:<15} {:<12} {:<20} \033[1;{}m{:<15}\033[0m".format(
            booking['customer_id'],
            booking['nama'],
            booking['telepon'],
            room_type,
            f"{booking['tanggal']} {waktu}",
            status_color,
            booking['status'].upper()))
    
    print("\033[1;34m" + "─"*80 + "\033[0m")
    print(f"\n\033[1;36mTotal booking online: {len(online_bookings)}\033[0m")
    
    # Tampilkan menu aksi
    print("\n\033[1;34mPilih Aksi:\033[0m")
    print("\033[1;32m1. Konfirmasi Booking")
    print("\033[1;31m2. Batalkan Booking")
    print("\033[1;33m0. Kembali\033[0m")
    
    while True:
        choice = input("\n\033[1;34m⌨ Pilihan Anda (0-2): \033[0m")
        
        if choice == '1':
            confirm_booking(online_bookings, ruangan_list)
            break
        elif choice == '2':
            cancel_booking(online_bookings)
            break
        elif choice == '0':
            break
        else:
            print("\033[1;31m❌ Pilihan tidak valid!\033[0m")
    
    time.sleep(1)

#fungsi konfirmasi booking online
def confirm_booking(online_bookings, ruangan_list):
    try:
        booking_id = int(input("\n\033[1;34m⌨ Masukkan ID Customer yang akan dikonfirmasi: \033[0m")) #input id customer yang ingin di konfirmasi
    except ValueError:
        print("\033[1;31m❌ ID harus berupa angka!\033[0m")
        return
    
    booking = next((b for b in online_bookings if b['customer_id'] == booking_id), None)
    if not booking:
        print("\033[1;31m❌ Booking tidak ditemukan!\033[0m")
        return
    
    # Tampilkan detail booking
    room = next((r for r in ruangan_list if r['id'] == booking['ruangan_id']), None)
    print("\n\033[1;36mDetail Booking:\033[0m")
    print(f"\033[1;33mNama    : {booking['nama']}")
    print(f"Telepon : {booking['telepon']}")
    print(f"Ruangan : {room['jenis'] if room else 'Unknown'} (ID: {booking['ruangan_id']})")
    print(f"Tanggal : {booking['tanggal']}")
    print(f"Waktu   : {booking['jam_mulai']:02d}:00-{booking['jam_mulai']+booking['durasi']:02d}:00")
    print(f"Durasi  : {booking['durasi']} jam\033[0m")
    
    #konfirmasi booking
    confirm = input("\n\033[1;34mKonfirmasi booking ini? (y/n): \033[0m").lower()
    if confirm == 'y':
        booking['status'] = "confirmed"
        save_json(ONLINE_FILE, online_bookings) #simpan ke file json
        print("\033[1;32m✓ Booking berhasil dikonfirmasi!\033[0m")
    else:
        print("\033[1;33m✖ Konfirmasi dibatalkan\033[0m")

#fungsi batalkan booking online
def cancel_booking(online_bookings):
    try:
        booking_id = int(input("\n\033[1;34m⌨ Masukkan ID Customer yang akan dibatalkan: \033[0m"))
    except ValueError:
        print("\033[1;31m❌ ID harus berupa angka!\033[0m")
        return
    
    booking = next((b for b in online_bookings if b['customer_id'] == booking_id), None) #dapatkan data id customer yang dipilih
    if not booking:
        print("\033[1;31m❌ Booking tidak ditemukan!\033[0m") #apabila data tidak ada
        return
    
    #konfirmasi
    confirm = input("\n\033[1;31mYakin ingin membatalkan booking ini? (y/n): \033[0m").lower()
    if confirm == 'y':
        online_bookings.remove(booking)
        save_json(ONLINE_FILE, online_bookings) #simpan data terbaru ke json
        print("\033[1;32m✓ Booking berhasil dibatalkan!\033[0m")
    else:
        print("\033[1;33m✖ Pembatalan dibatalkan\033[0m")

#fungsi mencari ruangan berdasarkan id
def find_room(ruangan_list, room_id):
    return next((r for r in ruangan_list if r['id'] == room_id), {})

#Memformat jam booking ke format waktu
def format_time(hour):
    return f"{hour:02d}:00-{hour+1:02d}:00"

#fungsi edit customer
def edit_customer(customer_list, ruangan_list):
    clear_screen()
    print("\033[1;36m" + "="*50)
    print(" "*18 + "✏️ EDIT CUSTOMER")
    print("="*50 + "\033[0m")
    
    # Tampilkan daftar customer
    print("\n\033[1;35mLoading customer data...\033[0m")
    time.sleep(0.5)
    view_customer(customer_list, ruangan_list)
    
    #jika tidak ada customer
    if not customer_list:
        print("\n\033[1;31m⚠️ Tidak ada data customer yang tersedia!\033[0m")
        time.sleep(1.5)
        return
    
    #input
    try:
        print("\n\033[1;33m" + "─"*50 + "\033[0m")
        cust_id = int(input("\033[1;34m⌨ Masukkan ID customer yang ingin diedit: \033[0m"))
    except ValueError:
        print("\n\033[1;31m❌ Error: Input harus berupa angka!\033[0m")
        time.sleep(1.5)
        return
    
    cust = next((c for c in customer_list if c['id'] == cust_id), None) #dapatkan data customer
    if not cust:
        print("\n\033[1;31m❌ Customer dengan ID tersebut tidak ditemukan!\033[0m") #jika tidak ada
        time.sleep(1.5)
        return
    
    print("\n\033[1;32m✓ Customer ditemukan:\033[0m")
    print(f"\033[1;33mNama saat ini: {cust['nama']}\033[0m")
    print("\033[1;35m" + "─"*50 + "\033[0m")
    
    #update nama customer
    new_name = input("\033[1;34m✨ Masukkan nama baru (kosongkan untuk batal): \033[0m").strip()
    
    if new_name:
        cust['nama'] = new_name
        save_json(CUSTOMER_FILE, customer_list) #simpan data ke json
        print("\n\033[1;32m✓ Data customer berhasil diperbarui!\033[0m")
        print(f"\033[1;36mID: {cust['id']} | Nama baru: {cust['nama']}\033[0m")
    else:
        print("\n\033[1;33m⚠️ Perubahan dibatalkan, nama tidak berubah.\033[0m")
    
    time.sleep(1.5)

#fungsi customer
def delete_customer(customer_list, history_list, ruangan_list=None):
    clear_screen()
    print("\033[1;36m" + "═"*50)
    print(" "*18 + "🗑️ HAPUS CUSTOMER")
    print("═"*50 + "\033[0m")
    
    # dapatkan data ruangan
    if ruangan_list is None:
        ruangan_list = load_json(RUANGAN_FILE)
    
    #dapatkan queue hari ini
    try:
        queue_today = load_json(QUEUE_FILE)
    except FileNotFoundError:
        queue_today = []
    
    #tampilkan list customer
    print("\n\033[1;33mMemuat data customer...\033[0m")
    time.sleep(0.5)
    view_customer(customer_list, ruangan_list)
    
    if not customer_list:
        print("\n\033[1;31m⚠️ Tidak ada customer yang tersedia!\033[0m")
        time.sleep(1.5)
        return
    
    #input id 
    print("\n\033[1;35m" + "─"*50 + "\033[0m")
    try:
        cust_id = int(input("\033[1;34m⌨ Masukkan ID customer yang akan dihapus: \033[0m"))
    except ValueError:
        print("\n\033[1;31m❌ Error: ID harus berupa angka!\033[0m")
        time.sleep(1.5)
        return
    
    #cari customer yang diinput
    cust = next((c for c in customer_list if c['id'] == cust_id), None)
    if not cust:
        print("\n\033[1;31m❌ Customer tidak ditemukan!\033[0m")
        time.sleep(1.5)
        return
    
    #tampilkan detail customer
    print("\n\033[1;31m⚠️ DATA CUSTOMER YANG AKAN DIHAPUS:\033[0m")
    print(f"\033[1;33mID     : {cust['id']}")
    print(f"Nama   : {cust['nama']}")
    
    #tampilkan info booking
    if cust.get('booking'):
        print("\n\033[1;36mBOOKING AKTIF:\033[0m")
        for booking in cust['booking']:
            room = next((r for r in ruangan_list if r['id'] == booking['ruangan_id']), None)
            room_type = room['jenis'] if room else "Unknown"
            print(f"- {room_type} | {booking['tanggal']} | {booking['jam']:02d}:00-{booking['jam']+1:02d}:00")
    
    print("\033[1;35m" + "─"*50 + "\033[0m")
    
    # konfirmasi
    confirm = input("\033[1;31mApakah Anda yakin ingin menghapus? (y/n): \033[0m").lower()
    if confirm != 'y':
        print("\n\033[1;33m🛑 Penghapusan dibatalkan\033[0m")
        time.sleep(1)
        return
    
    #penghapusan
    try:
        # 1. hapus dari customer list
        customer_list.remove(cust)
        
        # 2. hapus dari history
        history_list[:] = [h for h in history_list if h.get('customer_id') != cust_id]
        
        # 3. hapus dari queue hari ini dan booking selanjutnya (jika ada)
        queue_today[:] = [q for q in queue_today if q.get('customer_id') != cust_id]
        
        # 4. simpan
        save_json(CUSTOMER_FILE, customer_list)
        save_json(HISTORY_FILE, history_list)
        save_json(QUEUE_FILE, queue_today)
        
        print("\n\033[1;32m✓ Customer berhasil dihapus!\033[0m")
        print(f"\033[1;36mID {cust_id} - {cust['nama']} telah dihapus dari sistem\033[0m")
        
    except Exception as e:
        print("\n\033[1;31m❌ Gagal menghapus customer:\033[0m")
        print(f"\033[1;33mError: {str(e)}\033[0m")
    
    time.sleep(1.5)

# --- HISTORY MANAGEMENT ---
#fungsi melihat histori
def view_riwayat(history_list, customer_list, ruangan_list):
    clear_screen()
    print("\033[1;36m" + "═"*80)
    print(" "*30 + "📋 DAFTAR BOOKING")
    print("═"*80 + "\033[0m")
    
    if not history_list:
        print("\n\033[1;31m⚠ Tidak ada riwayat booking yang tersedia!\033[0m\n")
        time.sleep(1)
        return
    
    # Urutkan riwayat berdasarkan tanggal dan jam
    sorted_queue = sorted(history_list, key=lambda x: (x['tanggal'], x['jam']))
    
    print("\n\033[1;35m{:<5} {:<12} {:<25} {:<15} {:<15} {:<10}\033[0m".format(
        "No", "Tanggal", "Customer", "Ruangan", "Jam", "Status"))
    print("\033[1;34m" + "─"*80 + "\033[0m")
    
    for idx, q in enumerate(sorted_queue, 1):
        cust_name = next((c['nama'] for c in customer_list if c['id'] == q['customer_id']), "Unknown")
        room_type = next((r['jenis'] for r in ruangan_list if r['id'] == q['ruangan_id']), "Unknown")
        
        status_color = "32" if q['online'] else "31"  # Green for online, red for offline
        status_text = "Online" if q['online'] else "Offline"
        
        print("{:<5} {:<12} \033[1;33m{:<25}\033[0m {:<15} {:<15} \033[1;{}m{:<10}\033[0m".format(
            idx,
            q['tanggal'],
            cust_name,
            room_type,
            f"{q['jam']:02d}:00-{q['jam']+1:02d}:00",
            status_color,
            status_text))
    
    print("\033[1;34m" + "─"*80 + "\033[0m")
    print(f"\n\033[1;36mTotal riwayat: {len(history_list)}\033[0m")
    time.sleep(1.5)

#fungsi tambah ke history
def add_to_history(history_list, customer_id, ruangan_id, tanggal, jam, online):
    # Cek apakah ruangan sudah dipesan di tanggal dan jam yang sama
    for q in history_list:
        if (q['ruangan_id'] == ruangan_id and 
            q['tanggal'] == tanggal and 
            q['jam'] == jam):
            print("\033[1;31m❌ Ruangan sudah dipesan pada jam tersebut!\033[0m")
            return False
    
    #tambah data
    history_list.append({
        'customer_id': customer_id,
        'ruangan_id': ruangan_id,
        'tanggal': tanggal,
        'jam': jam,
        'online': online,
        'waktu_booking': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_json(HISTORY_FILE, history_list) #simpan data di json
    print("\033[1;32m✓ Booking berhasil ditambahkan ke riwayat!\033[0m")
    return True

# --- SEARCH & SORT FUNCTIONS ---
# Fungsi untuk mencari dan mengurutkan data ruangan
def search_sort_ruangan(ruangan_list):
    # Membersihkan layar console
    clear_screen()
    
    # Menampilkan header menu
    print("\033[1;36m" + "═"*60)
    print(" "*20 + "🔍 CARI & URUTKAN RUANGAN")
    print("═"*60 + "\033[0m")
    
    # Memeriksa apakah list ruangan kosong
    if not ruangan_list:
        print("\n\033[1;31m⚠ Tidak ada data ruangan yang tersedia!\033[0m")
        time.sleep(1.5)
        return
    
    # Menampilkan pilihan menu
    print("\n\033[1;34mPilih Menu:\033[0m")
    print("\033[1;32m1. Cari berdasarkan Jenis Ruangan\033[0m")
    print("\033[1;33m2. Urutkan berdasarkan Kapasitas\033[0m")
    print("\033[1;31m0. Kembali ke Menu Utama\033[0m")
    
    # Loop untuk memproses pilihan user
    while True:
        choice = input("\n\033[1;34m⌨ Pilihan Anda (0-2): \033[0m")
        
        # Pilihan 1: Pencarian berdasarkan jenis ruangan
        if choice == '1':
            # Meminta input jenis ruangan dari user
            keyword = input("\n\033[1;34m⌨ Masukkan jenis ruangan (Regular/VIP/VVIP): \033[0m").lower()
            
            # Mencari ruangan yang sesuai dengan keyword
            hasil = [r for r in ruangan_list if r['jenis'].lower() == keyword]
            
            # Jika tidak ada hasil pencarian
            if not hasil:
                print("\n\033[1;31m❌ Tidak ada ruangan dengan jenis tersebut!\033[0m")
            else:
                # Menampilkan hasil pencarian dalam format tabel
                print("\n\033[1;32m✓ Hasil Pencarian:\033[0m")
                print("\033[1;35m{:<5} {:<10} {:<12} {:<25}\033[0m".format(
                    "ID", "Jenis", "Kapasitas", "Console"))
                print("\033[1;34m" + "─"*60 + "\033[0m")
                for r in hasil:
                    print("\033[1;36m{:<5}\033[0m {:<10} {:<12} \033[1;33m{:<25}\033[0m".format(
                        r['id'], r['jenis'], f"{r['kapasitas']} orang", ', '.join(r['console'])))
            break
            
        # Pilihan 2: Pengurutan berdasarkan kapasitas
        elif choice == '2':
            # Menampilkan pilihan pengurutan
            print("\n\033[1;34mPilih Urutan:\033[0m")
            print("\033[1;32m1. Kapasitas Terkecil ke Terbesar\033[0m")
            print("\033[1;33m2. Kapasitas Terbesar ke Terkecil\033[0m")
            
            # Meminta input pilihan pengurutan dari user
            sort_choice = input("\n\033[1;34m⌨ Pilihan Anda (1-2): \033[0m")
            
            # Pengurutan ascending (kecil ke besar)
            if sort_choice == '1':
                sorted_ruangan = sorted(ruangan_list, key=lambda r: r['kapasitas'])
                print("\n\033[1;32m✓ Urutkan dari Kapasitas Terkecil:\033[0m")
            # Pengurutan descending (besar ke kecil)
            elif sort_choice == '2':
                sorted_ruangan = sorted(ruangan_list, key=lambda r: r['kapasitas'], reverse=True)
                print("\n\033[1;32m✓ Urutkan dari Kapasitas Terbesar:\033[0m")
            else:
                print("\033[1;31m❌ Pilihan tidak valid!\033[0m")
                continue
                
            # Menampilkan hasil pengurutan dalam format tabel
            print("\033[1;35m{:<5} {:<10} {:<12} {:<25}\033[0m".format(
                "ID", "Jenis", "Kapasitas", "Console"))
            print("\033[1;34m" + "─"*60 + "\033[0m")
            for r in sorted_ruangan:
                print("\033[1;36m{:<5}\033[0m {:<10} {:<12} \033[1;33m{:<25}\033[0m".format(
                    r['id'], r['jenis'], f"{r['kapasitas']} orang", ', '.join(r['console'])))
            break
            
        # Pilihan 0: Kembali ke menu utama
        elif choice == '0':
            return
            
        # Pilihan tidak valid
        else:
            print("\033[1;31m❌ Pilihan tidak valid! Harap pilih 0-2.\033[0m")
    
    time.sleep(1.5)

# Fungsi untuk mencari dan mengurutkan data customer
def search_sort_customer(customer_list):
    # Membersihkan layar console
    clear_screen()
    
    # Menampilkan header menu dengan warna cyan tebal
    print("\033[1;36m" + "═"*60)
    print(" "*20 + "🔍 CARI & URUTKAN CUSTOMER")
    print("═"*60 + "\033[0m")
    
    # Memeriksa apakah list customer kosong
    if not customer_list:
        print("\n\033[1;31m⚠ Tidak ada data customer yang tersedia!\033[0m")
        time.sleep(1.5)
        return
    
    # Menampilkan pilihan menu dengan warna berbeda untuk setiap opsi
    print("\n\033[1;34mPilih Menu:\033[0m")
    print("\033[1;32m1. Cari berdasarkan Nama\033[0m")  # Hijau
    print("\033[1;33m2. Urutkan dari A-Z\033[0m")       # Kuning
    print("\033[1;35m3. Urutkan dari Z-A\033[0m")       # Ungu
    print("\033[1;31m0. Kembali ke Menu Utama\033[0m")  # Merah
    
    # Loop untuk memproses pilihan user
    while True:
        choice = input("\n\033[1;34m⌨ Pilihan Anda (0-3): \033[0m")
        
        # Pilihan 1: Pencarian berdasarkan nama customer
        if choice == '1':
            # Meminta input nama customer dari user (case insensitive)
            keyword = input("\n\033[1;34m⌨ Masukkan nama customer: \033[0m").lower()
            
            # Mencari customer yang mengandung keyword dalam namanya
            hasil = [c for c in customer_list if keyword in c['nama'].lower()]
            
            # Jika tidak ada hasil pencarian
            if not hasil:
                print("\n\033[1;31m❌ Customer tidak ditemukan!\033[0m")
            else:
                # Menampilkan hasil pencarian dalam format tabel
                print("\n\033[1;32m✓ Hasil Pencarian:\033[0m")
                print("\033[1;35m{:<5} {:<25}\033[0m".format("ID", "Nama"))
                print("\033[1;34m" + "─"*40 + "\033[0m")
                for c in hasil:
                    print("\033[1;36m{:<5}\033[0m \033[1;33m{:<25}\033[0m".format(
                        c['id'], c['nama']))
            break
            
        # Pilihan 2: Pengurutan A-Z (ascending)
        elif choice == '2':
            # Mengurutkan customer berdasarkan nama (case insensitive)
            sorted_cust = sorted(customer_list, key=lambda c: c['nama'].lower())
            print("\n\033[1;32m✓ Urutkan dari A-Z:\033[0m")
            # Menampilkan header tabel
            print("\033[1;35m{:<5} {:<25}\033[0m".format("ID", "Nama"))
            print("\033[1;34m" + "─"*40 + "\033[0m")
            # Menampilkan data customer yang sudah diurutkan
            for c in sorted_cust:
                print("\033[1;36m{:<5}\033[0m \033[1;33m{:<25}\033[0m".format(
                    c['id'], c['nama']))
            break
            
        # Pilihan 3: Pengurutan Z-A (descending)
        elif choice == '3':
            # Mengurutkan customer berdasarkan nama (case insensitive) secara terbalik
            sorted_cust = sorted(customer_list, key=lambda c: c['nama'].lower(), reverse=True)
            print("\n\033[1;32m✓ Urutkan dari Z-A:\033[0m")
            # Menampilkan header tabel
            print("\033[1;35m{:<5} {:<25}\033[0m".format("ID", "Nama"))
            print("\033[1;34m" + "─"*40 + "\033[0m")
            # Menampilkan data customer yang sudah diurutkan
            for c in sorted_cust:
                print("\033[1;36m{:<5}\033[0m \033[1;33m{:<25}\033[0m".format(
                    c['id'], c['nama']))
            break
            
        # Pilihan 0: Kembali ke menu utama
        elif choice == '0':
            return
            
        # Pilihan tidak valid
        else:
            print("\033[1;31m❌ Pilihan tidak valid! Harap pilih 0-3.\033[0m")
    
    time.sleep(1.5)

# Fungsi untuk menampilkan teks dengan efek animasi ketik
def animate_text(text, delay=0.01):
    for char in text:
        # Menulis karakter satu per satu
        sys.stdout.write(char)
        sys.stdout.flush()  
        time.sleep(delay)   
    print()

# ----- MENU ADMIN -----
def admin_menu():
    ruangan_list = load_json(RUANGAN_FILE)
    customer_list = load_json(CUSTOMER_FILE)
    history_list = load_json(HISTORY_FILE)

    while True:
        clear_screen()
        animate_text("\033[1;35m" + "="*50)
        animate_text(" "*18 + "🔒 ADMIN DASHBOARD")
        animate_text("="*50 + "\033[0m")
        
        print("\n\033[1;34m🛠️  MAIN MENU\033[0m")
        print("\033[1;36m1. 🏠 Kelola Ruangan Gaming")
        print("2. 👥 Kelola Data Customer")
        print("3. 📋 Lihat Riwayat Booking")
        print("4. 📱 Lihat Booking Online")
        print("5. 👀 Monitor Customer Hari Ini")
        print("6. 🔍 Cari/Urutkan Data")
        print("7. 🔐 Ubah Password Admin")
        print("0. 🚪 Logout\033[0m")
        print("\033[1;35m" + "="*50 + "\033[0m")
        
        choice = input("\n\033[1;33m🔹 Pilih menu (0-7): \033[0m")

        if choice == '1':
            while True:
                clear_screen()
                animate_text("\033[1;36m" + "="*50)
                animate_text(" "*18 + "🏠 MANAGE ROOMS")
                animate_text("="*50 + "\033[0m")
                
                print("\n1. ➕ Tambah Ruangan Baru")
                print("2. 👀 Lihat Daftar Ruangan")
                print("3. ✏️  Edit Data Ruangan")
                print("4. ❌ Hapus Ruangan")
                print("0. ↩️  Kembali ke Menu Utama")
                print("\033[1;35m" + "-"*50 + "\033[0m")
                
                sub_choice = input("\n\033[1;33m🔹 Pilih aksi: \033[0m")
                
                if sub_choice == '1':
                    add_ruangan(ruangan_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '2':
                    view_ruangan(ruangan_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '3':
                    edit_ruangan(ruangan_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '4':
                    delete_ruangan(ruangan_list, history_list, customer_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '0':
                    break
                else:
                    print("\n\033[1;31m❌ Pilihan tidak valid!\033[0m")
                    time.sleep(1)

        elif choice == '2':
            while True:
                clear_screen()
                animate_text("\033[1;36m" + "="*50)
                animate_text(" "*18 + "👥 MANAGE CUSTOMERS")
                animate_text("="*50 + "\033[0m")
                
                print("\n1. ➕ Tambah Customer Baru")
                print("2. 👀 Lihat Daftar Customer")
                print("3. ✏️  Edit Data Customer")
                print("4. ❌ Hapus Customer")
                print("0. ↩️  Kembali ke Menu Utama")
                print("\033[1;35m" + "-"*50 + "\033[0m")
                
                sub_choice = input("\n\033[1;33m🔹 Pilih aksi: \033[0m")
                
                if sub_choice == '1':
                    add_customer(customer_list, ruangan_list, history_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '2':
                    view_customer(customer_list, ruangan_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '3':
                    edit_customer(customer_list, ruangan_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '4':
                    delete_customer(customer_list, history_list, ruangan_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '0':
                    break
                else:
                    print("\n\033[1;31m❌ Pilihan tidak valid!\033[0m")
                    time.sleep(1)

        elif choice == '3':
            clear_screen()
            animate_text("\033[1;36m" + "="*50)
            animate_text(" "*18 + "📋 BOOKING QUEUE")
            animate_text("="*50 + "\033[0m")
            view_riwayat(history_list, customer_list, ruangan_list)
            input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")

        elif choice == '4': 
            view_online_bookings(ruangan_list)
            input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")

        elif choice == '5':
            monitor_today_customers(customer_list, ruangan_list)
            input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")

        elif choice == '6':  # Geser menu sebelumnya
            while True:
                clear_screen()
                animate_text("\033[1;36m" + "="*50)
                animate_text(" "*18 + "🔍 SEARCH & SORT")
                animate_text("="*50 + "\033[0m")
                
                print("\n1. 🔎 Cari/Urutkan Ruangan")
                print("2. 🔎 Cari/Urutkan Customer")
                print("0. ↩️  Kembali ke Menu Utama")
                print("\033[1;35m" + "-"*50 + "\033[0m")
                
                sub_choice = input("\n\033[1;33m🔹 Pilih aksi: \033[0m")
                
                if sub_choice == '1':
                    search_sort_ruangan(ruangan_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '2':
                    search_sort_customer(customer_list)
                    input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
                elif sub_choice == '0':
                    break
                else:
                    print("\n\033[1;31m❌ Pilihan tidak valid!\033[0m")
                    time.sleep(1)

        elif choice == '7':  # Geser menu change password
            clear_screen()
            animate_text("\033[1;36m" + "="*50)
            animate_text(" "*18 + "🔐 CHANGE PASSWORD")
            animate_text("="*50 + "\033[0m")
            manage_admin_account()
            input("\n\033[1;36mTekan Enter untuk melanjutkan...\033[0m")
        
        elif choice == '0':
            print("\n\033[1;32m✔️ Logging out... See you later!👋\033[0m")
            time.sleep(1)
            break
            
        else:
            print("\n\033[1;31m❌ Pilihan tidak valid!\033[0m")
            time.sleep(1)
        
        # Save changes after each operation
        save_json(RUANGAN_FILE, ruangan_list)
        save_json(CUSTOMER_FILE, customer_list)
        save_json(HISTORY_FILE, history_list)