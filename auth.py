from mysql.connector import Error

def login(conn, role):
    print(f"\n=== LOGIN {role.upper()} ===")
    username = input("Username: ")
    password = input("Password: ")

    try:
        cursor = conn.cursor()
        tabel = "Guru" if role == "guru" else "Siswa"
        pk = "id_guru" if role == "guru" else "id_siswa"
        
        query = f"SELECT {pk}, nama_{role} FROM {tabel} WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            print(f"\nSelamat datang, {user[1]}!")
            return user[0], user[1] 
        else:
            print("\n[!] Username atau Password salah.")
            return None, None
            
    except Error as e:
        print(f"Error autentikasi: {e}")
        return None, None
    finally:
        if cursor: cursor.close()