import pymysql
from db.connection import MySQLConnection

class Municipio:
    @classmethod
    def obtener_municipios(cls):    
        conn = MySQLConnection().connect()
        if conn:
            try:
                with conn.cursor() as cursor:
                    # Consulta SQL para obtener todos los municipios
                    sql_query = "SELECT nomMunicipio FROM municipios"
                    cursor.execute(sql_query)
                    distritos = cursor.fetchall()
                    return distritos  # Retorna la lista de distritos
            except pymysql.MySQLError as e:
                print(f"Error al obtener municipios: {e}")
                return []  # Retorna una lista vacía en caso de error
            finally:
                conn.close()  # Cerrar la conexión
        else:
            print("No se pudo establecer la conexión con la base de datos")
            return []
   