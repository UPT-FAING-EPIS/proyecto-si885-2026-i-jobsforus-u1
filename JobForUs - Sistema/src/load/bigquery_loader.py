"""
Cargador simplificado a BigQuery para JobForUs
"""

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import os
from datetime import datetime

class BigQueryLoader:
    def __init__(self):
        # Configuración del proyecto
        self.project_id = "jobforus-almacen"  # Cambia por tu ID de proyecto
        self.dataset_id = "job_market"
        self.table_id = "fact_oferta"
        self.client = None
    
    def conectar(self):
        """Conectar a BigQuery"""
        try:
            # Usar credenciales locales (si existen)
            if os.path.exists("credentials/gcp-key.json"):
                credentials = service_account.Credentials.from_service_account_file(
                    "credentials/gcp-key.json"
                )
                self.client = bigquery.Client(
                    credentials=credentials,
                    project=self.project_id
                )
            else:
                # Usar autenticación por defecto
                self.client = bigquery.Client(project=self.project_id)
            
            print("✅ Conectado a BigQuery")
            return True
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def cargar_desde_csv(self, archivo_csv):
        """Cargar datos desde CSV a BigQuery"""
        try:
            # Leer CSV
            df = pd.read_csv(archivo_csv)
            
            # Agregar fecha de carga
            df['fecha_carga'] = datetime.now()
            
            # Configurar tabla
            table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
            
            # Subir datos
            job = self.client.load_table_from_dataframe(
                df, table_ref, write_disposition="WRITE_APPEND"
            )
            job.result()
            
            print(f"✅ Datos cargados: {len(df)} registros")
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar: {e}")
            return False

# Ejecutar
if __name__ == "__main__":
    loader = BigQueryLoader()
    if loader.conectar():
        loader.cargar_desde_csv("../data/raw/global_ai_tech_salaries_2020_2025.csv")