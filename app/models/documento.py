import pymysql
from db.connection import MySQLConnection
from datetime import datetime

class Documento:
    def __init__(self, brote_id, nombre_archivo, path, tipo_notificacion, fechacarga=None, fechmodificacion=None, iddocumento=None):
        self.iddocumento = iddocumento
        self.brote_id = brote_id
        self.nombre_archivo = nombre_archivo
        self.path = path
        self.tipo_notificacion = tipo_notificacion
        self.fechacarga = fechacarga or datetime.now()
        self.fechmodificacion = fechmodificacion

    @classmethod
    def create(cls, **kwargs):
        conn = MySQLConnection().connect()
        try:
            with conn.cursor() as cursor:
                sql = """
                INSERT INTO documentos (brote_id, nombre_archivo, path, tipo_notificacion, fechacarga, fechmodificacion)
                VALUES (%(brote_id)s, %(nombre_archivo)s, %(path)s, %(tipo_notificacion)s,  NOW(), NOW())
                """
                cursor.execute(sql, kwargs)
                conn.commit()
                print("Documento registrado correctamente")
        except pymysql.MySQLError as e:
            conn.rollback()  # Realiza un rollback en caso de error
            print(f"Error al registrar el documento: {e}")
        finally:
            conn.close()


    @classmethod
    def update(cls, brote_id, **kwargs):
        # Conexión a la base de datos
        conn = MySQLConnection().connect()
        try:
            # Validar que los datos requeridos estén presentes en kwargs
            required_fields = ['nombre_archivo', 'path','tipo_notificacion']
            for field in required_fields:
                if field not in kwargs:
                    raise ValueError(f"El campo '{field}' es obligatorio para actualizar el documento.")
            
            # Agregar el ID del brote a los datos
            kwargs['brote_id'] = brote_id
            
            with conn.cursor() as cursor:
                # Verificar si el documento ya existe
                cursor.execute('SELECT * FROM documentos WHERE brote_id = %s', ('brote_id',))
                documento = cursor.fetchone()
                
                if documento:                   
                    # Consulta SQL
                    sql = """
                    UPDATE documentos
                    SET nombre_archivo = %(nombre_archivo)s,
                        path = %(path)s,
                        tipo_notificacion = %(tipo_notificacion)s,                    
                        fechmodificacion = NOW()
                    WHERE brote_id = %(brote_id)s
                    """
                    
                    # Ejecutar la consulta
                    cursor.execute(sql, kwargs)
                    print(f"Documento con brote_id {brote_id} actualizado.")
                else:
                    # Si no existe, insertamos un nuevo documento
                    sql = """
                    INSERT INTO documentos (brote_id, nombre_archivo, path, tipo_notificacion, fechacarga, fechmodificacion)
                    VALUES (%(brote_id)s, %(nombre_archivo)s, %(path)s, %(tipo_notificacion)s, NOW(), NOW())
                    """
                    
                    cursor.execute(sql, kwargs)
                    print(f"Documento con brote_id {brote_id} insertado.")
                    
                conn.commit()        
        except pymysql.MySQLError as e:
            conn.rollback()  # Realiza un rollback en caso de error
            print(f"Error al actualizar el documento: {e}")
        finally:
            conn.close()

    
    # Método para obtener todos los documentos asociados a un brote
    @staticmethod
    def get_by_brote_id(brote_id):
        """Obtiene todos los documentos asociados a un brote por su ID."""
        conn = MySQLConnection().connect()  # Usa la clase de conexión adecuada
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                query = 'SELECT * FROM documentos WHERE brote_id = %s'
                cursor.execute(query, (brote_id,))
                documentos = cursor.fetchall()  # Obtener todos los registros
                return documentos  # Retorna una lista de diccionarios
        except pymysql.MySQLError as e:
            print(f"Error al obtener los documentos: {e}")
            return []  # Retorna una lista vacía si hay un error
        finally:
            conn.close()
