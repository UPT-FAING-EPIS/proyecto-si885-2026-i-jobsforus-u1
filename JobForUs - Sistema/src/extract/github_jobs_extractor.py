"""
Módulo de extracción de datos desde archivo local CSV
JobForUs - Sistema de Inteligencia de Mercado Laboral
"""

import pandas as pd
import os
from datetime import datetime

class LocalJobsExtractor:
    """
    Clase encargada de extraer datos desde un archivo CSV local.
    """
    
    def __init__(self, raw_data_path="./data/raw/"):
        """
        Inicializa el extractor con la ruta donde se encuentra el archivo.
        """
        self.raw_data_path = raw_data_path
        self.logs = []
        
        # Definir el archivo de origen
        self.source_file = os.path.join(self.raw_data_path, "job_market.csv")
    
    def _log(self, message, level="INFO"):
        """Registra un mensaje en el log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.logs.append(log_entry)
        print(log_entry)
    
    def extraer_dataset(self):
        """
        Extrae el dataset desde el archivo CSV local.
        
        Returns:
            DataFrame de pandas con los datos o None si hay error
        """
        try:
            self._log(f"📥 Extrayendo datos desde: {self.source_file}")
            
            # Verificar si el archivo existe
            if not os.path.exists(self.source_file):
                self._log(f"❌ Archivo no encontrado: {self.source_file}", "ERROR")
                return None
            
            # Leer el archivo CSV
            df = pd.read_csv(self.source_file)
            
            self._log(f"✅ Extracción exitosa: {len(df)} registros cargados")
            self._log(f"📋 Columnas disponibles: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            self._log(f"❌ Error al extraer datos: {e}", "ERROR")
            return None
    
    def obtener_info_dataset(self, df):
        """
        Muestra información básica del dataset.
        
        Args:
            df: DataFrame de pandas
        """
        print("\n" + "=" * 60)
        print("📊 INFORMACIÓN DEL DATASET")
        print("=" * 60)
        print(f"📌 Total registros: {len(df)}")
        print(f"📌 Total columnas: {len(df.columns)}")
        print(f"\n📋 Nombres de columnas:")
        for col in df.columns:
            print(f"   - {col}")
        
        print(f"\n📋 Tipos de datos:")
        print(df.dtypes)
        
        print(f"\n📋 Primeros 3 registros:")
        print(df.head(3))
        
        print(f"\n📋 Valores nulos por columna:")
        print(df.isnull().sum())
    
    def obtener_logs(self):
        """Retorna todos los logs generados."""
        return self.logs


def probar_extraccion():
    """
    Función de prueba para verificar que el extractor funciona.
    """
    print("🔧 Probando extractor de archivo local...")
    print("=" * 40)
    
    extractor = LocalJobsExtractor()
    df = extractor.extraer_dataset()
    
    if df is not None:
        extractor.obtener_info_dataset(df)
        return df
    else:
        print("❌ No se pudo cargar el dataset. Verifica la ruta del archivo.")
        return None


if __name__ == "__main__":
    probar_extraccion()