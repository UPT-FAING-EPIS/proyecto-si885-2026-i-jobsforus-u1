"""
Cargador a BigQuery para JobForUs
"""

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime
from pathlib import Path

class BigQueryLoader:
    def __init__(self):
        # Configuración del proyecto - CORREGIDO
        self.project_id = "jobforus-project"  # ← Nombre correcto
        self.dataset_id = "job_market"
        self.table_id = "fact_oferta"
        self.client = None
    
    def conectar(self):
        try:
            script_dir = Path(__file__).parent.parent.parent
            cred_path = script_dir / "credentials" / "gcp-key.json"
            
            print(f"🔍 Buscando credenciales en: {cred_path}")
            
            if cred_path.exists():
                credentials = service_account.Credentials.from_service_account_file(
                    str(cred_path)
                )
                self.client = bigquery.Client(
                    credentials=credentials,
                    project=self.project_id
                )
                print(f"✅ Conectado a BigQuery - Proyecto: {self.project_id}")
                return True
            else:
                print(f"❌ No se encontró el archivo: {cred_path}")
                return False
            
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def crear_dataset_si_no_existe(self):
        """Crea el dataset si no existe"""
        try:
            dataset_ref = f"{self.project_id}.{self.dataset_id}"
            self.client.get_dataset(dataset_ref)
            print(f"📁 Dataset {self.dataset_id} ya existe")
        except Exception:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            self.client.create_dataset(dataset)
            print(f"✅ Dataset {self.dataset_id} creado")
    
    def crear_tabla_si_no_existe(self):
        """Crea la tabla con el esquema correcto"""
        try:
            table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
            self.client.get_table(table_ref)
            print(f"📋 Tabla {self.table_id} ya existe")
        except Exception:
            schema = [
                bigquery.SchemaField("id", "INTEGER"),
                bigquery.SchemaField("survey_year", "INTEGER"),
                bigquery.SchemaField("job_title", "STRING"),
                bigquery.SchemaField("job_category", "STRING"),
                bigquery.SchemaField("experience_level", "STRING"),
                bigquery.SchemaField("education_level", "STRING"),
                bigquery.SchemaField("country", "STRING"),
                bigquery.SchemaField("continent", "STRING"),
                bigquery.SchemaField("currency", "STRING"),
                bigquery.SchemaField("company_size", "STRING"),
                bigquery.SchemaField("industry", "STRING"),
                bigquery.SchemaField("employment_type", "STRING"),
                bigquery.SchemaField("work_setting", "STRING"),
                bigquery.SchemaField("base_salary_usd", "FLOAT64"),
                bigquery.SchemaField("annual_bonus_usd", "FLOAT64"),
                bigquery.SchemaField("stock_grant_usd", "FLOAT64"),
                bigquery.SchemaField("total_compensation_usd", "FLOAT64"),
                bigquery.SchemaField("job_satisfaction", "FLOAT64"),
                bigquery.SchemaField("years_at_company", "INTEGER"),
                bigquery.SchemaField("primary_skills", "STRING"),
                bigquery.SchemaField("ai_adoption_level", "STRING"),
                bigquery.SchemaField("gender", "STRING"),
                bigquery.SchemaField("fecha_carga", "TIMESTAMP"),
            ]
            
            table = bigquery.Table(table_ref, schema=schema)
            self.client.create_table(table)
            print(f"✅ Tabla {self.table_id} creada")
    
    def cargar_desde_csv(self, archivo_csv=None):
        try:
            if archivo_csv is None:
                script_dir = Path(__file__).parent.parent.parent
                archivo_csv = script_dir / "data" / "raw" / "global_ai_tech_salaries_2020_2025.csv"
            
            print(f"📁 Leyendo archivo: {archivo_csv}")
            
            if not Path(archivo_csv).exists():
                print(f"❌ Archivo no encontrado: {archivo_csv}")
                return False
            
            df = pd.read_csv(archivo_csv)
            print(f"📊 CSV leído: {len(df)} registros")
            
            # Agregar fecha de carga
            df['fecha_carga'] = datetime.now()
            
            table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
            
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
                autodetect=False
            )
            
            job = self.client.load_table_from_dataframe(
                df, table_ref, job_config=job_config
            )
            job.result()
            
            table = self.client.get_table(table_ref)
            print(f"✅ Datos cargados a BigQuery: {len(df)} registros")
            print(f"📊 Total registros en tabla: {table.num_rows}")
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar: {e}")
            return False


if __name__ == "__main__":
    loader = BigQueryLoader()
    if loader.conectar():
        loader.crear_dataset_si_no_existe()
        loader.crear_tabla_si_no_existe()
        loader.cargar_desde_csv()