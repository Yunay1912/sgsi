# db/test_conexion.py
from db.conexion import crear_conexion, obtener_cursor

def main():
    conn = crear_conexion()
    if not conn:
        print("No hay conexión. Revisa DATABASE_URL.")
        return
    cur = obtener_cursor(conn, dict_cursor=False)
    try:
        cur.execute("SELECT version();")
        print("Postgres version:", cur.fetchone())
    finally:
        cur.close()
        conn.close()
        print("Conexión cerrada.")

if __name__ == "__main__":
    main()
