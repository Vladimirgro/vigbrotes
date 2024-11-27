import pymysql
from db.connection import MySQLConnection

class Distrito:
    @classmethod
    def obtener_distritos(cls):    
        conn = MySQLConnection().connect()
        if conn:
            try:
                with conn.cursor() as cursor:
                    # Consulta SQL para obtener todos los distritos
                    sql_query = "SELECT distrito FROM distritos"
                    cursor.execute(sql_query)
                    distritos = cursor.fetchall()
                    return distritos  # Retorna la lista de distritos
            except pymysql.MySQLError as e:
                print(f"Error al obtener distritos: {e}")
                return []  # Retorna una lista vacía en caso de error
            finally:
                conn.close()  # Cerrar la conexión
        else:
            print("No se pudo establecer la conexión con la base de datos")
            return []     