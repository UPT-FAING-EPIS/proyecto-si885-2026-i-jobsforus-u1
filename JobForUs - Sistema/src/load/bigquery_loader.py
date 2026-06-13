"""
Cargador automatizado a BigQuery
JobForUs - Sistema de Inteligencia de Mercado Laboral
"""

from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import os
from datetime import datetime


class BigQueryLoader:
    """
    Clase para cargar datos transformados a BigQuery.
    """
    
    def __init__(self, credentials_path="credentials/gcp_key.json"):
        """
        Inicializa el cargador de BigQuery.
        
        Args:
            credentials_path: Ruta al archivo de credenciales de GCP
        """
        self.credentials_path = credentials_path
        self.client = None
        self.project_id = "jobforus-project"
        self.dataset_id = "job_market"
        self.logs = []
        
        self._authenticate()
    
    def _log(self, message):
        """Registra un mensaje en el log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)
    
    def _authenticate(self):
        """Autenticación con Google Cloud."""
        try:
            # Verificar si existe el archivo de credenciales
            if not os.path.exists(self.credentials_path):
                self._log(f"⚠️ No se encontró credenciales en {self.credentials_path}")
                self._log("💡 Usando autenticación por defecto (gcloud auth)")
                self.client = bigquery.Client(project=self.project_id)
            else:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self.client = bigquery.Client(
                    credentials=credentials,
                    project=self.project_id
                )
            self._log("✅ Autenticación exitosa con Google Cloud")
            return True
        except Exception as e:
            self._log(f"❌ Error de autenticación: {e}")
            return False
    
    def crear_dataset(self):
        """Crea el dataset en BigQuery si no existe."""
        dataset_ref = f"{self.project_id}.{self.dataset_id}"
        
        try:
            self.client.get_dataset(dataset_ref)
            self._log(f"📁 Dataset {dataset_ref} ya existe")
        except Exception:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            dataset.description = "Dataset JobForUs - Análisis de mercado laboral tecnológico"
            self.client.create_dataset(dataset)
            self._log(f"✅ Dataset {dataset_ref} creado")
    
    def crear_tablas(self):
        """Crea las tablas en BigQuery si no existen."""
        self._log("\n📝 Creando tablas en BigQuery...")
        
        # Esquema para fact_oferta
        schema_fact_oferta = [
            bigquery.SchemaField("oferta_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("titulo", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("salario_usd", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("survey_year", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("job_satisfaction", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("gender", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("work_setting", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("tecnologia_principal", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("seniority", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("annual_bonus_usd", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("total_compensation_usd", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("ai_adoption_level", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("fecha_carga", "TIMESTAMP", mode="NULLABLE")
        ]
        
        table_ref = f"{self.project_id}.{self.dataset_id}.fact_oferta"
        
        try:
            self.client.get_table(table_ref)
            self._log(f"   ✅ Tabla fact_oferta ya existe")
        except Exception:
            table = bigquery.Table(table_ref, schema=schema_fact_oferta)
            table.description = "Tabla de hechos con ofertas laborales"
            self.client.create_table(table)
            self._log(f"   ✅ Tabla fact_oferta creada")
    
    def cargar_desde_dataframe(self, df, table_name):
        """
        Carga datos desde un DataFrame a BigQuery.
        
        Args:
            df: DataFrame con los datos
            table_name: Nombre de la tabla (ej: 'fact_oferta')
        """
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        # Agregar fecha de carga
        df['fecha_carga'] = datetime.now()
        
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",  # Agregar datos (modo incremental)
            autodetect=True
        )
        
        try:
            job = self.client.load_table_from_dataframe(
                df, table_ref, job_config=job_config
            )
            job.result()  # Esperar a que termine
            
            self._log(f"   ✅ {table_name}: {len(df)} registros cargados")
            return len(df)
        except Exception as e:
            self._log(f"   ❌ Error cargando {table_name}: {e}")
            return 0
    
    def cargar_dataset_completo(self, df):
        """
        Carga el dataset completo al almacén.
        
        Args:
            df: DataFrame transformado
        """
        self._log("\n" + "=" * 60)
        self._log("💾 CARGANDO DATOS A BIGQUERY")
        self._log("=" * 60)
        
        # Verificar autenticación
        if not self.client:
            self._log("❌ No hay autenticación válida")
            return {'error': 'Autenticación fallida'}
        
        # Crear dataset y tablas
        self.crear_dataset()
        self.crear_tablas()
        
        # Cargar datos
        self._log("\n📥 Cargando datos...")
        registros = self.cargar_desde_dataframe(df, "fact_oferta")
        
        self._log("\n" + "=" * 60)
        self._log("✅ CARGA COMPLETADA")
        self._log(f"📊 Total registros cargados: {registros}")
        self._log("=" * 60)
        
        return {
            'registros_cargados': registros,
            'dataset': self.dataset_id,
            'proyecto': self.project_id
        }
    
    def obtener_logs(self):
        """Retorna los logs del proceso."""
        return self.logs


def probar_conexion():
    """Prueba la conexión con BigQuery."""
    print("\n" + "=" * 60)
    print("🧪 PROBANDO CONEXIÓN A BIGQUERY")
    print("=" * 60)
    
    loader = BigQueryLoader()
    
    if loader.client:
        print("\n✅ Conexión exitosa a Google Cloud")
        print(f"   - Proyecto: {loader.project_id}")
        print(f"   - Dataset: {loader.dataset_id}")
        
        # Probar crear dataset
        loader.crear_dataset()
        
        return True
    else:
        print("\n❌ Error de conexión")
        return False


if __name__ == "__main__":
    probar_conexion()