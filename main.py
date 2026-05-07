# Ubah bagian ini dari 'koneksi' menjadi 'connector'
from connector import create_connection
import auth
import guru
import siswa

def main():
    conn = create_connection()
    if not conn: 
        print("Sistem dihentikan karena tidak dapat terhubung ke database.")
        return

    while True:
        print("\n===== SISTEM LMS SEKOLAH =====")
        print("1. Login sebagai Guru")
        print("2. Login sebagai Siswa")
        print("3. Keluar")
        
        pilihan = input("Pilih (1/2/3): ")

        if pilihan == '1':
            user_id, nama = auth.login(conn, "guru")
            if user_id:
                # Menu khusus Guru
                while True:
                    print(f"\n--- MENU GURU ({nama}) ---")
                    print("1. Upload Materi")
                    print("2. Beri Nilai Tugas")
                    print("3. Hapus Materi")
                    print("4. Logout")
                    p_guru = input("Pilih: ")
                    
                    if p_guru == '1': 
                        guru.upload_materi_oleh_guru(conn, user_id)
                    elif p_guru == '2': 
                        guru.nilai_tugas_siswa(conn, user_id)
                    elif p_guru == '3': 
                        guru.hapus_materi(conn)
                    elif p_guru == '4': 
                        break
        
        elif pilihan == '2':
            user_id, nama = auth.login(conn, "siswa")
            if user_id:
                # Menu khusus Siswa
                while True:
                    print(f"\n--- MENU SISWA ({nama}) ---")
                    print("1. Lihat Materi")
                    print("2. Kumpul Tugas")
                    print("3. Cek Nilai")
                    print("4. Logout")
                    p_siswa = input("Pilih: ")
                    
                    if p_siswa == '1': 
                        siswa.lihat_materi_siswa(conn, user_id)
                    elif p_siswa == '2': 
                        # Opsional: Jika ingin otomatis mendeteksi siswa yang kumpul tugas
                        siswa.kumpul_tugas(conn, user_id) 
                    elif p_siswa == '3': 
                        siswa.lihat_nilai_saya(conn, user_id)
                    elif p_siswa == '4': 
                        break

        elif pilihan == '3':
            print("Sistem ditutup. Terima kasih!")
            break
        else:
            print("Pilihan tidak valid.")

    if conn.is_connected():
        conn.close()

if __name__ == '__main__':
    main()