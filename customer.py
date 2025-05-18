from utils import load_json, save_json, next_id, RUANGAN_FILE, CUSTOMER_FILE, HISTORY_FILE, ONLINE_FILE
from admin import add_to_history
from datetime import datetime, date
import os
import sys
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def typewriter(text, delay=0.001):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def validate_date(input_date):
    try:
        return datetime.strptime(input_date, "%Y-%m-%d").date()
    except ValueError:
        return None

def get_available_hours(history_list, ruangan_id, tanggal):
    """Get available hours between 7 AM to 10 PM"""
    booked_hours = [q['jam'] for q in history_list 
                   if q['ruangan_id'] == ruangan_id 
                   and q['tanggal'] == str(tanggal)]
    return [h for h in range(7, 23) if h not in booked_hours]

def show_available_rooms(ruangan_list, history_list, booking_date=None):
    """Show available rooms with time slots"""
    if booking_date is None:
        # Get booking date if not provided
        while True:
            date_str = input("Masukkan tanggal (YYYY-MM-DD): ").strip()
            booking_date = validate_date(date_str)
            if booking_date and booking_date >= date.today():
                break
            print("Tanggal tidak valid atau sudah lewat!")
    
    # Display room information
    print("\nDaftar Ruangan:")
    print("=" * 80)
    print("ID    Jenis      Kapasitas    Console                  ")
    print("-" * 80)
    for room in ruangan_list:
        console = room.get('console', 'Tidak ada info')
        print(f"{room['id']:<5} {room['jenis']:<10} {room['kapasitas']:<12} {console}")
    print("=" * 80)
    
    # Room selection
    while True:
        try:
            room_id = int(input("\nPilih ID Ruangan (0 untuk batal): "))
            if room_id == 0:
                return None, None, None
            selected_room = next(r for r in ruangan_list if r['id'] == room_id)
            break
        except (ValueError, StopIteration):
            print("ID Ruangan tidak valid!")
    
    available_hours = get_available_hours(history_list, room_id, str(booking_date))
    
    if not available_hours:
        print(f"\nRuangan {selected_room['jenis']} (ID: {room_id}) sudah penuh pada {booking_date}!")
        return None, None, None
    
    # Display available slots
    print(f"\nSlot waktu tersedia untuk Ruangan {selected_room['jenis']} (ID: {room_id}):")
    print("-" * 40)
    for i, hour in enumerate(available_hours, 1):
        print(f"{i}. {hour:02d}:00-{hour+1:02d}:00")
    print("-" * 40)
    
    return booking_date, room_id, available_hours

def online_booking(ruangan_list, history_list):
    print("\n=== BOOKING ONLINE ===")
    
    # Get customer info first
    while True:
        name = input("Nama Lengkap: ").strip()
        if name:
            break
        print("Nama tidak boleh kosong!")
    
    while True:
        phone = input("Nomor HP (min 10 digit): ").strip()
        if phone.isdigit() and len(phone) >= 10:
            break
        print("Nomor HP harus angka minimal 10 digit!")

    # Get booking date once at the start
    while True:
        date_str = input("\nMasukkan tanggal booking (YYYY-MM-DD): ").strip()
        booking_date = validate_date(date_str)
        if booking_date and booking_date >= date.today():
            break
        print("Tanggal tidak valid atau sudah lewat!")

    # Load customer data at the start
    customer_list = load_json(CUSTOMER_FILE)
    
    # Show available rooms for selected date
    while True:
        print("\nDaftar Ruangan Tersedia:")
        print("=" * 80)
        print("ID    Jenis      Kapasitas    Console                  ")
        print("-" * 80)
        for room in ruangan_list:
            available_hours = get_available_hours(history_list, room['id'], str(booking_date))
            status = "Tersedia" if available_hours else "Penuh"
            console = ', '.join(room.get('console', []))
            print(f"{room['id']:<5} {room['jenis']:<10} {room['kapasitas']:<12} {console:<20} {status}")
        print("=" * 80)
        
        try:
            room_id = int(input("\nPilih ID Ruangan (0 untuk batal): "))
            if room_id == 0:
                return
            selected_room = next(r for r in ruangan_list if r['id'] == room_id)
            break
        except (ValueError, StopIteration):
            print("ID Ruangan tidak valid!")

    available_hours = get_available_hours(history_list, room_id, str(booking_date))
    
    if not available_hours:
        print(f"\nRuangan {selected_room['jenis']} (ID: {room_id}) sudah penuh pada {booking_date}!")
        return
    
    # Time selection process
    while True:
        print(f"\nSlot waktu tersedia untuk Ruangan {selected_room['jenis']}:")
        print("-" * 40)
        for i, hour in enumerate(available_hours, 1):
            print(f"{i}. {hour:02d}:00-{hour+1:02d}:00")
        print("-" * 40)
        
        try:
            slot_choice = int(input("Pilih nomor slot (0 untuk ganti ruangan): "))
            if slot_choice == 0:
                break  # Back to room selection
            elif 1 <= slot_choice <= len(available_hours):
                start_hour = available_hours[slot_choice-1]
                
                # Get duration
                duration = int(input("Durasi (1-4 jam): "))
                duration = max(1, min(4, duration))  # Clamp between 1-4
                
                # Validate slot
                if all(h in available_hours for h in range(start_hour, start_hour + duration)):
                    # Generate customer ID
                    cust_id = next_id(customer_list)
                    
                    # Create booking records
                    new_customer = {
                        'id': cust_id,
                        'nama': name,
                        'booking': [{
                            'ruangan_id': room_id,
                            'tanggal': str(booking_date),
                            'jam': hour,
                            'online': True,
                        } for hour in range(start_hour, start_hour + duration)]
                    }

                    # Update all data files
                    customer_list.append(new_customer)
                    save_json(CUSTOMER_FILE, customer_list)
                    
                    for hour in range(start_hour, start_hour + duration):
                        add_to_history(history_list, cust_id, room_id, str(booking_date), hour, online=True)
                    save_json(HISTORY_FILE, history_list)

                    online_booking_data = {
                        'customer_id': cust_id,
                        'nama': name,
                        'telepon': phone,
                        'ruangan_id': room_id,
                        'tanggal': str(booking_date),
                        'jam_mulai': start_hour,
                        'durasi': duration,
                        'status': 'confirmed',
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    online_bookings = load_json(ONLINE_FILE)
                    online_bookings.append(online_booking_data)
                    save_json(ONLINE_FILE, online_bookings)

                    # Show receipt
                    print("\n=== BOOKING BERHASIL ===")
                    print(f"ID Booking: {cust_id}")
                    print(f"Ruangan: {selected_room['jenis']} (ID: {room_id})")
                    print(f"Tanggal: {booking_date}")
                    print(f"Waktu: {start_hour:02d}:00-{start_hour+duration:02d}:00")
                    return
                else:
                    print("Slot waktu tidak tersedia untuk durasi ini!")
            else:
                print("Pilihan slot tidak valid!")
        except ValueError:
            print("Input harus angka!")

def customer_menu():
    ruangan_list = load_json(RUANGAN_FILE)
    history_list = load_json(HISTORY_FILE)
    
    while True:
        clear_screen()
        print("\033[1;35m" + "="*50)
        print(" "*18 + "🎮 MENU PELANGGAN")
        print("="*50 + "\033[0m")
        
        print("\n\033[1;34m🌟 MAIN MENU\033[0m")
        print("\033[1;36m1. 🔍 Lihat Ruangan Tersedia")
        print("2. 📅 Booking Online")
        print("0. 🚪 Keluar\033[0m")
        print("\033[1;35m" + "="*50 + "\033[0m")
        
        choice = input("\n\033[1;33m🔹 Pilih menu (0-2): \033[0m")

        if choice == '1':
            clear_screen()
            print("\033[1;36m" + "="*50)
            print(" "*18 + "🔍 RUANGAN TERSEDIA")
            print("="*50 + "\033[0m")
            show_available_rooms(ruangan_list, history_list)
            input("\n\033[1;36mTekan Enter untuk kembali...\033[0m")
            
        elif choice == '2':
            clear_screen()
            print("\033[1;36m" + "="*50)
            print(" "*18 + "📅 BOOKING ONLINE")
            print("="*50 + "\033[0m")
            online_booking(ruangan_list, history_list)
            input("\n\033[1;36mTekan Enter untuk kembali...\033[0m")
            
        elif choice == '0':
            print("\n\033[1;32m✔️ Terima kasih! Game on! 🎮\033[0m")
            time.sleep(1)
            break
            
        else:
            print("\n\033[1;31m❌ Pilihan tidak valid!\033[0m")
            time.sleep(1)