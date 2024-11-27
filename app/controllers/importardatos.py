import pymysql
import pandas as pd
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'vladimir',
    'db': 'brotes'
}

# Establecer la conexión
conn = pymysql.connect(
    host=DB_CONFIG['host'],
    user=DB_CONFIG['user'],
    password=DB_CONFIG['password'],
    db=DB_CONFIG['db'],
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)


path = 'C:/projects/brotes/app/files/Listado brotes CENAPRECE_BASE_copia.xlsx'
# Cargar el archivo de Excel
try:
    df = pd.read_excel(path, sheet_name="Base_General", skiprows=10, engine='openpyxl', header=0)
except FileNotFoundError:
    print("El archivo no se encontró en la ruta especificada. Verifica la ruta y el nombre del archivo.")

df = df.drop(0)

columnas_a_mayusculas = ['Tipo evento', 'Unidad notificante', 
                         'Dx sospecha', 'Jurisdicción', 
                         'Municipio','Localidad','Resultado','Se realizó nota']
df[columnas_a_mayusculas] = df[columnas_a_mayusculas].apply(lambda x: x.str.upper())

# Eliminar varias columnas
columnas_a_eliminar = ['No','No_Juris', 'Fecha_Alta_Programada', 'Días Expirados para pedir alta', 'Estatus','Observaciones', 'Unnamed: 32', 
                       'Unnamed: 33','Semana epid inicio', 'Semana epid notificacion','No_Municipio','Población expuesta']
df = df.drop(columnas_a_eliminar, axis=1)



df = pd.DataFrame(df)

# Reordenar columnas
nuevo_orden = ['Folio notinmed', 'Fecha de notificación Notinmed', 'Tipo evento', 'Unidad notificante', 
               'Institución', 'Fecha ini', 'Fecha not','Dx sospecha', 
               'Jurisdicción', 'Municipio', 'Localidad', 'M',
               'F', 'Casos probables', 'Casos confirmados','Defunciones', 
               'Fecha Último Caso', 'Fecha Alta', 'Resultado', 'Folio de alta',
               'Fecha y hora de alta','Se realizó nota' ]
df = df[nuevo_orden]

df = df.where(pd.notnull(df), None)

#Reemplazar NaN en columnas específicas
# Columnas numéricas
numeric_columns = ['Casos probables', 'M', 'F']
df[numeric_columns] = df[numeric_columns].fillna(0)

# Columnas de texto
text_columns = ['Resultado']
df[text_columns] = df[text_columns].fillna('')

# Mostrar los primeros registros para verificar que los datos se cargaron correctamente
#df['Fecha y hora de alta'] = df['Fecha y hora de alta'].str.strip()

# Verificar si la columna tiene datos y convertir solo esos valores a formato de fecha
columns_to_format = [
                    'Fecha ini', 
                    'Fecha not', 
                    'Fecha Último Caso', 
                    'Fecha de notificación Notinmed', 
                    'Fecha y hora de alta'
                ]

for col in columns_to_format:
    df[col] = df[col].apply(lambda x: pd.to_datetime(x, dayfirst=True, errors='coerce').strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) else x)

print(df)

try:
    with conn.cursor() as cursor:
        # Iterar sobre cada fila en el DataFrame
        for index, row in df.iterrows():
            sql = """
            INSERT INTO brote (folionotinmed, fechnotinmed, tipoevento, unidadnotif, institucion, fechinicio, fechnotifica, diagsospecha, 
                            jurisdiccion, municipio, localidad, pobmascexp, pobfemexp, casosprob, casosconf, defunciones,
                            fechultimocaso, fechalta, resultado, folioaltanotin, fechaltanotin, nota) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, tuple(None if pd.isna(x) else x for x in row))
        conn.commit()
        print("Datos importados con éxito")
except pymysql.MySQLError as e:
    print(f"Error al importar datos: {e}")
finally:
    conn.close()  # Cerrar la conexión


# for index, row in df.iterrows():
#         sql = """
#         INSERT INTO brote (folionotinmed, fechnotinmed, tipoevento, unidadnotif, institucion, fechinicio, fechnotifica, diagsospecha, 
#                            jurisdiccion, municipio, localidad, pobmascexp, pobfemexp, casosprob, casosconf, defunciones,
#                            fechultimocaso, fechalta, resultado, folioaltanotin, fechaltanotin, nota) 
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         cursor.execute(sql, tuple(None if pd.isna(x) else x for x in row))
#         conn.commit()  # Confirmar los cambios
#         print("Datos importados con éxito")