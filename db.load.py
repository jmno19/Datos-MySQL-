import mysql.connector
import pandas as pd
print('Leyendo el archivo data.xlsx...')
df = pd.read_excel('/home/johan/Descargas/data.xlsx')
print('Conectando a MySQL...')
conexion = mysql.connector.connect(
    host='localhost',
    user='root',
    password='123456',  
    database='normalizacion_db',
)
cursor = conexion.cursor()

print('Insertando niveles educativos únicos...')
for nivel in df['nivel_edu'].unique():
  cursor.execute(
      'INSERT IGNORE INTO nivel_educativo (nombre_nivel) VALUES (%s)', (nivel,)
  )

print('Insertando sexos únicos...')
for s in df['sex'].unique():
  cursor.execute('INSERT IGNORE INTO sexo_tipo (descripcion) VALUES (%s)', (s,))

conexion.commit()

cursor.execute('SELECT id_nivel, nombre_nivel FROM nivel_educativo')
mapa_niveles = {nombre: id_n for id_n, nombre in cursor.fetchall()}

cursor.execute('SELECT id_sexo, descripcion FROM sexo_tipo')
mapa_sexos = {desc: id_s for id_s, desc in cursor.fetchall()}

print('Insertando los registros en la tabla persona...')
for _, row in df.iterrows():
  id_nivel = mapa_niveles[row['nivel_edu']]
  id_sexo = mapa_sexos[row['sex']]

  sql = """
        INSERT INTO persona (id, edad, ingreso_mensual, anios_esc, id_nivel, id_sexo)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        edad=VALUES(edad), ingreso_mensual=VALUES(ingreso_mensual), anios_esc=VALUES(anios_esc);
    """
  valores = (
      int(row['id']),
      int(row['edad']),
      int(row['ingreso_mensual']),
      int(row['anios_esc']),
      id_nivel,
      id_sexo,
  )
  cursor.execute(sql, valores)

conexion.commit()
cursor.close()
conexion.close()
print(
    'Datos cargados a MySQL desde el Excel'
    ' local.'
)