import pymysql
from db.connection import MySQLConnection
from datetime import datetime

class Brote:
    def __init__(self, folionotinmed, fechnotinmed, tipoevento, unidadnotif, institucion, fechinicio, fechnotifica, diagsospecha, 
                 jurisdiccion, municipio, localidad, pobmascexp, pobfemexp, casosprob, casosconf, defunciones,
                 fechultimocaso, fechalta, resultado, folioaltanotin, fechaltanotin, nota, fechcaptura, idbrote=None):
        self.idbrote = idbrote
        self.folionotinmed = folionotinmed
        self.fechnotinmed = fechnotinmed
        self.tipoevento = tipoevento
        self.unidadnotif = unidadnotif.upper() 
        self.institucion = institucion
        self.fechinicio = fechinicio
        self.fechnotifica = fechnotifica
        self.diagsospecha = diagsospecha.upper() 
        self.jurisdiccion = jurisdiccion.upper() 
        self.municipio = municipio.upper() 
        self.localidad = localidad.upper() 
        self.pobmascexp = pobmascexp
        self.pobfemexp = pobfemexp
        self.casosprob = casosprob
        self.casosconf = casosconf
        self.defunciones = defunciones   
        self.fechultimocaso = fechultimocaso
        self.fechalta = fechalta
        self.resultado = resultado
        self.folioaltanotin = folioaltanotin
        self.fechaltanotin = fechaltanotin
        self.nota = nota        
        self.fechcaptura = fechcaptura if fechcaptura else datetime.now()
        
        
    @classmethod
    def create(cls, **kwargs):
        conn = MySQLConnection().connect()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                    INSERT INTO brote (folionotinmed, fechnotinmed, tipoevento, unidadnotif, institucion, fechinicio, fechnotifica, diagsospecha, 
                                       jurisdiccion, municipio, localidad, pobmascexp, pobfemexp, casosprob, casosconf, defunciones,
                                       fechultimocaso, fechalta, resultado, folioaltanotin, fechaltanotin, nota, fechcaptura)
                    VALUES (%(folionotinmed)s, %(fechnotinmed)s, %(tipoevento)s, %(unidadnotif)s, %(institucion)s, %(fechinicio)s, %(fechnotifica)s, %(diagsospecha)s, 
                            %(jurisdiccion)s, %(municipio)s, %(localidad)s, %(pobmascexp)s, %(pobfemexp)s, %(casosprob)s, %(casosconf)s, %(defunciones)s,
                            %(fechultimocaso)s, %(fechalta)s, %(resultado)s, %(folioaltanotin)s, %(fechaltanotin)s, %(nota)s, NOW())
                """
                cursor.execute(sql, kwargs)
                conn.commit()  # Confirma la transacción                        
                brote_id = cursor.lastrowid  # Obtener el ID del brote insertado
                print("Registro insertado correctamente")
                return brote_id
        except pymysql.MySQLError as e:
            print(f"Error al insertar el registro: {e}")
        finally:
            if conn:
                conn.close()
    
    
    def to_dict(self):
        return {
            "idbrote": self.idbrote,
            "folionotinmed": self.folionotinmed,
            "tipoevento": self.tipoevento,
            "institucion": self.institucion,
            "municipio": self.municipio,
            "fechnotinmed": self.fechnotinmed,
            "diagsospecha": self.diagsospecha
        }
        
        
    # Método para obtener el total de brotes
    @classmethod
    def obtener_total_brotes(cls):
        conn = MySQLConnection().connect()
        query = "SELECT COUNT(*) as total FROM brote"
        
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:  # Uso de DictCursor para obtener un diccionario
                cursor.execute(query)
                result = cursor.fetchone()
                total_brotes = result['total'] if result and 'total' in result else 0  # Acceso seguro al campo total
            
        except Exception as e:
            print(f"Error al obtener el total de brotes: {e}")
            total_brotes = 0
            
        finally:
            conn.close()
        
        
        
        return total_brotes

    # Método para obtener todos los brotes con paginación
    @classmethod
    def obtener_todos(cls, limit=None, offset=0):
        conn = MySQLConnection().connect()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT * FROM brote"
                if limit is not None:
                    sql += " LIMIT %s OFFSET %s"
                    cursor.execute(sql, (limit, offset))
                else:
                    cursor.execute(sql)
                
                resultados = cursor.fetchall()
                brotes = [cls(**row) for row in resultados]  # Construcción de objetos Brote                
                return brotes
        except pymysql.MySQLError as e:
            print(f"Error al obtener registros: {e}")
            return []
        finally:
            conn.close()           
  
    
    @classmethod
    def get_by_id(cls, idbrote):
        conn = None
        brote = None
        try:
            conn = MySQLConnection().connect()
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM brote WHERE idbrote = %s", (idbrote,))
                brote = cursor.fetchone()                
        except pymysql.MySQLError as e:
            print(f"Error al obtener el brote: {e}")
        except AttributeError as e:
            print("Error de conexión a la base de datos:", e)
        finally:
            if conn:
                conn.close()
        return brote
    
   
    @classmethod
    def update(cls, item_id, **data):
        conn = None
        try:
            conn = MySQLConnection().connect()  # Asegúrate de que la conexión esté establecida
            cursor = conn.cursor()
            
            # Preparar los valores para la consulta
            query = """
                UPDATE brote
                SET
                    folionotinmed = %s,
                    fechnotinmed = %s,
                    tipoevento = %s,
                    unidadnotif = %s,
                    institucion = %s,
                    fechinicio = %s,
                    fechnotifica = %s,
                    diagsospecha = %s,
                    jurisdiccion = %s,
                    municipio = %s,
                    localidad = %s,
                    pobmascexp = %s,
                    pobfemexp = %s,
                    casosprob = %s,
                    casosconf = %s,
                    defunciones = %s,
                    fechultimocaso = %s,
                    fechalta = %s,
                    resultado = %s,
                    folioaltanotin = %s,
                    fechaltanotin = %s,                
                    nota = %s
                WHERE idbrote = %s
            """
            
            cursor.execute(query, (*data.values(), item_id))
            conn.commit()
            
        except pymysql.MySQLError as e:
            if conn:
                conn.rollback()  # Realiza un rollback en caso de error
            print(f"Error al actualizar el registro: {e}")
        finally:
            if conn:
                conn.close()

        
    
    @classmethod
    def get_existing_brote(cls, folionotinmed):
        conn = MySQLConnection().connect()  # Asegúrate de que la conexión esté establecida
        cursor = conn.cursor(pymysql.cursors.DictCursor)
                
        # Definir y ejecutar la consulta SQL
        query = "SELECT * FROM brote WHERE folionotinmed = %s LIMIT 1"
        cursor.execute(query, (folionotinmed,))
        
        # Obtener el primer resultado
        existing_brote = cursor.fetchone()
        
        # Cerrar el cursor y la conexión
        cursor.close()
        conn.close()
        
        return existing_brote