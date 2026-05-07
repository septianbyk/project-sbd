from mysql.connector import Error

def upload_materi_oleh_guru(conn, id_guru):
    print("\n--- [GURU] UPLOAD MATERI BARU ---")
    id_siswa = input("Masukkan ID Siswa tujuan: ")
    matpel = input("Mata Pelajaran: ")
    judul = input("Judul Materi: ")
    link = input("Link Dokumen/Modul (Google Drive, dll): ")
    
    try:
        cursor = conn.cursor()
        query = """INSERT INTO Pengajaran 
                   (id_guru, id_siswa, mata_pelajaran, judul_materi, link_dokumen) 
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (id_guru, id_siswa, matpel, judul, link))
        conn.commit()
        print(f"Materi '{judul}' berhasil didistribusikan ke siswa dengan ID {id_siswa}!")
    except Error as e:
        print(f"Gagal mengupload materi: {e}")
    finally:
        if cursor: cursor.close()

def nilai_tugas_siswa(conn, id_guru):
    print("\n--- [GURU] PENILAIAN TUGAS SISWA ---")
    try:
        cursor = conn.cursor()
        query_cek = """
            SELECT t.id_tugas, s.nama_siswa, p.judul_materi, t.link_jawaban 
            FROM Tugas t
            JOIN Pengajaran p ON t.id_pengajaran = p.id_pengajaran
            JOIN Siswa s ON p.id_siswa = s.id_siswa
            WHERE p.id_guru = %s AND t.nilai IS NULL
        """
        cursor.execute(query_cek, (id_guru,))
        records = cursor.fetchall()

        if not records:
            print("Bagus! Belum ada tugas baru yang perlu dinilai saat ini.")
            return

        print("\nDaftar Tugas Menunggu Penilaian:")
        for row in records:
            print(f"[{row[0]}] Siswa: {row[1]} | Materi: {row[2]}")
            print(f"    Link Jawaban: {row[3]}")

        print("-" * 40)
        id_tugas = input("Masukkan ID Tugas yang ingin dinilai (atau ketik 'batal'): ")
        if id_tugas.lower() == 'batal': return
            
        nilai = input("Masukkan Nilai (0-100): ")
        
        query_nilai = "UPDATE Tugas SET nilai = %s WHERE id_tugas = %s AND id_pengajaran IN (SELECT id_pengajaran FROM Pengajaran WHERE id_guru = %s)"
        cursor.execute(query_nilai, (nilai, id_tugas, id_guru))
        conn.commit()
        
        if cursor.rowcount > 0:
            print("Nilai berhasil disimpan ke dalam sistem!")
        else:
            print("Gagal menyimpan nilai. Pastikan ID Tugas benar.")
    except Error as e:
        print(f"Terjadi kesalahan sistem: {e}")
    finally:
        if cursor: cursor.close()

def hapus_materi(conn, id_guru):
    print("\n--- [GURU] HAPUS MATERI ---")
    id_pengajaran = input("Masukkan ID Pengajaran yang ingin dihapus: ")
    try:
        cursor = conn.cursor()
        query = "DELETE FROM Pengajaran WHERE id_pengajaran = %s AND id_guru = %s"
        cursor.execute(query, (id_pengajaran, id_guru))
        conn.commit()
        
        if cursor.rowcount > 0:
            print("Materi (dan tugas terkait) berhasil dihapus dari database.")
        else:
            print("Materi tidak ditemukan atau Anda tidak memiliki akses menghapusnya.")
    except Error as e:
        print(f"Gagal menghapus materi: {e}")
    finally:
        if cursor: cursor.close()

def cek_krs_guru(conn, id_guru):
    print("\n--- [GURU] DAFTAR KELAS & MAHASISWA ---")
    try:
        cursor = conn.cursor()
        query = """
            SELECT DISTINCT p.mata_pelajaran, s.nama_siswa
            FROM Pengajaran p
            JOIN Siswa s ON p.id_siswa = s.id_siswa
            WHERE p.id_guru = %s
            ORDER BY p.mata_pelajaran
        """
        cursor.execute(query, (id_guru,))
        records = cursor.fetchall()

        if not records:
            print("Anda belum memiliki kelas atau siswa yang diajar.")
        else:
            print(f"{'MATA PELAJARAN':<25} | {'NAMA SISWA'}")
            print("-" * 50)
            for row in records:
                print(f"{row[0]:<25} | {row[1]}")
    except Error as e:
        print(f"Gagal memuat daftar kelas: {e}")
    finally:
        if cursor: cursor.close()