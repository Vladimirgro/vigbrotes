import pymysql
from db.connection import MySQLConnection

class Diagnostico:
    def __init__(self, diagnostico, periodoIncubacion):        
        self.diagnostico = diagnostico.upper()
        self.periodoIncubacion = periodoIncubacion        

    @classmethod
    def create(cls, diagnostico, periodoIncubacion):
        conn = MySQLConnection().connect()
        try:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO catalogodiagnosticos (diagnostico, periodoIncubacion)
                    VALUES (%s, %s)
                """
                cursor.execute(sql, (diagnostico, periodoIncubacion))
                conn.commit()  # Confirma la transacción
                print("Registro insertado correctamente")
        except pymysql.MySQLError as e:
            print(f"Error al insertar el registro: {e}")
        finally:
            conn.close()
        
    def to_dict(self):
        return {                        
            'diagnostico': self.diagnostico,
            'periodoIncubacion': self.periodoIncubacion
        }
           
    @classmethod
    def obtener_diagnosticos(cls):
        conn = MySQLConnection().connect()
        if conn:
            try:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    sql = "SELECT diagnostico, periodoIncubacion FROM catalogodiagnosticos"
                    cursor.execute(sql)
                    resultados = cursor.fetchall()
                    diagnosticos = [cls(**row) for row in resultados]
                    return [diag.to_dict() for diag in diagnosticos]
            except pymysql.MySQLError as e:
                print(f"Error al obtener diagnósticos: {e}")
                return []  # Retorna una lista vacía en caso de error
            finally:
                conn.close()  # Cerrar la conexión
        else:
            print("No se pudo establecer la conexión con la base de datos")
            return []

    @classmethod
    def obtener_por_id(cls, id):
        connection = MySQLConnection().connect()
        with connection.cursor() as cursor:            
            cursor.execute("SELECT diagnostico, periodoIncubacion FROM catalogodiagnosticos WHERE iddiagnostico = %s", (id,))
            result = cursor.fetchone()
            return cls(*result) if result else None

    @classmethod
    def actualizar(cls, id, diagnostico, periodoIncubacion):
        connection = MySQLConnection()
        with connection.cursor() as cursor:
            cursor.execute("UPDATE catalogodiagnosticos SET diagnostico = %s, periodoIncubacion = %s WHERE iddiagnostico = %s", (diagnostico, periodoIncubacion, id))
            connection.commit()
