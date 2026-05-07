from mysql.connector import Error

def cek_krs_siswa(conn, id_siswa):
    print("\n--- [SISWA] KARTU RENCANA STUDI (KRS) ---")
    try:
        cursor = conn.cursor()
        query = """
            SELECT DISTINCT p.mata_pelajaran, g.nama_guru
            FROM Pengajaran p
            JOIN Guru g ON p.id_guru = g.id_guru
            WHERE p.id_siswa = %s
        """
        cursor.execute(query, (id_siswa,))
        records = cursor.fetchall()

        if not records:
            print("KRS kamu masih kosong. Belum ada kelas yang terdaftar.")
        else:
            print(f"{'MATA PELAJARAN':<25} | {'GURU PENGAMPU'}")
            print("-" * 50)
            for row in records:
                print(f"{row[0]:<25} | {row[1]}")
    except Error as e:
        print(f"Gagal memuat KRS: {e}")
    finally:
        if cursor: cursor.close()

def lihat_materi_siswa(conn, id_siswa):
    print("\n--- [SISWA] DAFTAR MATERI BELAJAR ---")
    try:
        cursor = conn.cursor()
        query = """
            SELECT p.id_pengajaran, g.nama_guru, p.mata_pelajaran, p.judul_materi, p.link_dokumen
            FROM Pengajaran p
            JOIN Guru g ON p.id_guru = g.id_guru
            WHERE p.id_siswa = %s
        """
        cursor.execute(query, (id_siswa,))
        records = cursor.fetchall()

        if not records:
            print("Belum ada materi yang ditugaskan untukmu saat ini.")
        else:
            for row in records:
                print(f"ID Pengajaran : {row[0]}")
                print(f"Guru          : {row[1]}")
                print(f"Pelajaran     : {row[2]} - {row[3]}")
                print(f"Link Materi   : {row[4]}")
                print("-" * 40)
    except Error as e:
        print(f"Gagal mengambil materi: {e}")
    finally:
        if cursor: cursor.close()

def kumpul_tugas(conn, id_siswa):
    print("\n--- [SISWA] PENGUMPULAN TUGAS ---")
    id_pengajaran = input("Masukkan ID Pengajaran dari materi yang dikerjakan: ")
    link_jawaban = input("Masukkan Link Jawaban (G-Drive, Github, dll): ")
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_pengajaran FROM Pengajaran WHERE id_pengajaran = %s AND id_siswa = %s", (id_pengajaran, id_siswa))
        if not cursor.fetchone():
            print("Akses ditolak! ID Pengajaran tidak valid atau bukan milikmu.")
            return

        cursor.execute("SELECT id_tugas FROM Tugas WHERE id_pengajaran = %s", (id_pengajaran,))
        if cursor.fetchone():
            print("Kamu sudah pernah mengumpulkan tugas untuk materi ini!")
            return

        query = "INSERT INTO Tugas (id_pengajaran, link_jawaban) VALUES (%s, %s)"
        cursor.execute(query, (id_pengajaran, link_jawaban))
        conn.commit()
        print("Tugas berhasil dikumpulkan dan sedang menunggu penilaian guru!")
    except Error as e:
        print(f"Gagal mengumpulkan tugas: {e}")
    finally:
        if cursor: cursor.close()

def lihat_nilai_saya(conn, id_siswa):
    print("\n--- [SISWA] LAPORAN NILAI ---")
    try:
        cursor = conn.cursor()
        query = """
            SELECT p.judul_materi, t.link_jawaban, t.nilai 
            FROM Tugas t
            JOIN Pengajaran p ON t.id_pengajaran = p.id_pengajaran
            WHERE p.id_siswa = %s
        """
        cursor.execute(query, (id_siswa,))
        records = cursor.fetchall()

        if not records:
            print("Belum ada tugas yang kamu kerjakan.")
        else:
            print(f"{'MATERI':<20} | {'STATUS / NILAI'}")
            print("-" * 40)
            for row in records:
                materi = row[0][:18] + ".." if len(row[0]) > 20 else row[0]
                status_nilai = f"Nilai: {row[2]}" if row[2] is not None else "Menunggu Penilaian"
                print(f"{materi:<20} | {status_nilai}")
    except Error as e:
        print(f"Gagal mengambil data nilai: {e}")
    finally:
        if cursor: cursor.close()