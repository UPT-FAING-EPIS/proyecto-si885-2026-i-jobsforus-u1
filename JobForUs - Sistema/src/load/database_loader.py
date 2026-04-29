"""
Módulo de carga de datos a SQLite
JobForUs - Sistema de Inteligencia de Mercado Laboral
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime


class DatabaseLoader:
    """
    Clase encargada de cargar los datos transformados a SQLite.
    """
    
    def __init__(self, db_path="database/job_market.db"):
        """
        Inicializa el cargador con la ruta de la base de datos.
        
        Args:
            db_path: Ruta relativa al archivo de base de datos SQLite
        """
        # Obtener la ruta absoluta del proyecto
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(script_dir, db_path)
        self.connection = None
        self.cursor = None
        self.logs = []
        
        # Asegurar que el directorio database existe
        db_dir = os.path.dirname(self.db_path)
        os.makedirs(db_dir, exist_ok=True)
    
    def _log(self, message):
        """Registra un mensaje en el log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)
    
    def conectar(self):
        """
        Establece conexión con la base de datos SQLite.
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        try:
            self._log(f"🔌 Conectando a base de datos: {self.db_path}")
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            self._log("✅ Conexión establecida")
            return True
        except Exception as e:
            self._log(f"❌ Error al conectar: {e}")
            return False
    
    def crear_tablas(self, schema_path="database/schema.sql"):
        """
        Crea las tablas ejecutando el script schema.sql.
        
        Args:
            schema_path: Ruta al archivo de esquema SQL
            
        Returns:
            True si la creación fue exitosa, False en caso contrario
        """
        try:
            # Obtener ruta absoluta del schema
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            schema_full_path = os.path.join(script_dir, schema_path)
            
            self._log(f"📝 Creando tablas desde: {schema_full_path}")
            
            # Leer y ejecutar el script SQL
            with open(schema_full_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Ejecutar el script (pueden ser múltiples sentencias)
            self.cursor.executescript(schema_sql)
            self.connection.commit()
            
            self._log("✅ Tablas creadas correctamente")
            return True
            
        except Exception as e:
            self._log(f"❌ Error al crear tablas: {e}")
            return False
    
    def insertar_dimensiones(self, df):
        """
        Inserta los datos únicos en las tablas de dimensiones.
        
        Args:
            df: DataFrame con los datos transformados
            
        Returns:
            Diccionario con los mapeos de IDs
        """
        self._log("\n📥 Insertando dimensiones...")
        
        mapeos = {
            'tecnologia': {},
            'empresa': {},
            'ubicacion': {}
        }
        
        # 1. Insertar tecnologías únicas
        if 'tecnologia_principal' in df.columns:
            tecnologias_unicas = df['tecnologia_principal'].unique()
            for tech in tecnologias_unicas:
                if tech and tech != 'Sin tecnología' and tech != 'No disponible':
                    categoria = df[df['tecnologia_principal'] == tech]['categoria_principal'].iloc[0] if len(df) > 0 else 'General'
                    try:
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO dim_tecnologia (nombre, categoria) VALUES (?, ?)",
                            (tech, categoria)
                        )
                        # Obtener el ID
                        self.cursor.execute("SELECT tecnologia_id FROM dim_tecnologia WHERE nombre = ?", (tech,))
                        row = self.cursor.fetchone()
                        if row:
                            mapeos['tecnologia'][tech] = row[0]
                    except Exception as e:
                        self._log(f"   ⚠️ Error insertando tecnología {tech}: {e}")
            
            self._log(f"   ✅ Tecnologías insertadas: {len(mapeos['tecnologia'])}")
        
        # 2. Insertar empresas únicas
        if 'company' in df.columns:
            empresas_unicas = df['company'].dropna().unique()
            for empresa in empresas_unicas:
                try:
                    self.cursor.execute(
                        "INSERT OR IGNORE INTO dim_empresa (nombre) VALUES (?)",
                        (empresa,)
                    )
                    self.cursor.execute("SELECT empresa_id FROM dim_empresa WHERE nombre = ?", (empresa,))
                    row = self.cursor.fetchone()
                    if row:
                        mapeos['empresa'][empresa] = row[0]
                except Exception as e:
                    self._log(f"   ⚠️ Error insertando empresa {empresa}: {e}")
            
            self._log(f"   ✅ Empresas insertadas: {len(mapeos['empresa'])}")
        
        # 3. Insertar ubicaciones únicas
        if 'location' in df.columns:
            ubicaciones_unicas = df['location'].dropna().unique()
            for ubicacion in ubicaciones_unicas:
                try:
                    # Determinar si es remoto
                    es_remoto = 1 if 'remote' in ubicacion.lower() else 0
                    self.cursor.execute(
                        "INSERT OR IGNORE INTO dim_ubicacion (nombre_completo, remoto) VALUES (?, ?)",
                        (ubicacion, es_remoto)
                    )
                    self.cursor.execute("SELECT ubicacion_id FROM dim_ubicacion WHERE nombre_completo = ?", (ubicacion,))
                    row = self.cursor.fetchone()
                    if row:
                        mapeos['ubicacion'][ubicacion] = row[0]
                except Exception as e:
                    self._log(f"   ⚠️ Error insertando ubicación {ubicacion}: {e}")
            
            self._log(f"   ✅ Ubicaciones insertadas: {len(mapeos['ubicacion'])}")
        
        self.connection.commit()
        return mapeos
    
    def obtener_seniority_id(self, seniority_texto):
        """
        Obtiene el ID de seniority basado en el texto.
        
        Args:
            seniority_texto: Nivel de seniority (Junior, Mid, Senior, Lead)
            
        Returns:
            ID del seniority
        """
        seniority_map = {
            'Junior': 1, 'Mid': 2, 'Senior': 3, 'Lead': 4
        }
        return seniority_map.get(seniority_texto, 5)  # 5 = No especificado
    
    def insertar_hechos(self, df, mapeos):
        """
        Inserta los datos en la tabla de hechos.
        
        Args:
            df: DataFrame transformado
            mapeos: Diccionario con mapeos de IDs de dimensiones
            
        Returns:
            Número de registros insertados
        """
        self._log("\n📥 Insertando hechos (ofertas laborales)...")
        
        registros_insertados = 0
        
        for idx, row in df.iterrows():
            try:
                # Obtener IDs de dimensiones
                tecnologia = row.get('tecnologia_principal', 'No especificada')
                tecnologia_id = mapeos['tecnologia'].get(tecnologia)
                
                empresa = row.get('company', None)
                empresa_id = mapeos['empresa'].get(empresa) if empresa else None
                
                ubicacion = row.get('location', None)
                ubicacion_id = mapeos['ubicacion'].get(ubicacion) if ubicacion else None
                
                seniority = row.get('seniority', 'No especificado')
                seniority_id = self.obtener_seniority_id(seniority)
                
                # Insertar oferta
                self.cursor.execute("""
                    INSERT INTO fact_oferta (
                        titulo, salario_min_original, salario_max_original, salario_usd,
                        experiencia_requerida, skills, educacion_requerida, beneficios,
                        fuente, tecnologia_id, seniority_id, empresa_id, ubicacion_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row.get('job_title'),
                    row.get('salary_min'),
                    row.get('salary_max'),
                    row.get('salary_usd'),
                    row.get('experience_required'),
                    row.get('skills'),
                    row.get('education_level'),
                    row.get('benefits'),
                    'job_market.csv',
                    tecnologia_id,
                    seniority_id,
                    empresa_id,
                    ubicacion_id
                ))
                registros_insertados += 1
                
                # Mostrar progreso cada 50 registros
                if registros_insertados % 50 == 0:
                    self._log(f"   ... {registros_insertados} registros insertados")
                    
            except Exception as e:
                self._log(f"   ⚠️ Error insertando oferta {idx}: {e}")
        
        self.connection.commit()
        self._log(f"   ✅ Total ofertas insertadas: {registros_insertados}")
        
        return registros_insertados
    
    def cargar_dataset(self, df):
        """
        Carga el dataset completo a la base de datos.
        
        Args:
            df: DataFrame transformado
            
        Returns:
            Diccionario con estadísticas de carga
        """
        self._log("\n" + "=" * 60)
        self._log("💾 INICIANDO CARGA A BASE DE DATOS")
        self._log("=" * 60)
        
        # 1. Conectar
        if not self.conectar():
            return {'error': 'No se pudo conectar a la base de datos'}
        
        # 2. Crear tablas
        if not self.crear_tablas():
            return {'error': 'No se pudieron crear las tablas'}
        
        # 3. Insertar dimensiones
        mapeos = self.insertar_dimensiones(df)
        
        # 4. Insertar hechos
        registros = self.insertar_hechos(df, mapeos)
        
        # 5. Cerrar conexión
        self.cerrar()
        
        return {
            'registros_procesados': len(df),
            'registros_insertados': registros,
            'tecnologias_insertadas': len(mapeos['tecnologia']),
            'empresas_insertadas': len(mapeos['empresa']),
            'ubicaciones_insertadas': len(mapeos['ubicacion'])
        }
    
    def cerrar(self):
        """Cierra la conexión a la base de datos."""
        if self.connection:
            self.connection.close()
            self._log("\n🔌 Conexión cerrada")
    
    def obtener_logs(self):
        """Retorna los logs del proceso."""
        return self.logs