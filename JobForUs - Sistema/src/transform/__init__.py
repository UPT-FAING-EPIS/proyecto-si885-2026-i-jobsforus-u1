"""
Módulo principal de transformación
JobForUs - Sistema de Inteligencia de Mercado Laboral
"""

from src.transform.data_cleaner import DataCleaner
from src.transform.salary_normalizer import SalaryNormalizer
from src.transform.seniority_classifier import SeniorityClassifier
from src.transform.tech_classifier import TechClassifier


class TransformadorCompleto:
    """
    Clase que orquesta todo el proceso de transformación.
    """
    
    def __init__(self):
        self.logs = []
    
    def _log(self, message):
        """Registra un mensaje."""
        self.logs.append(message)
        print(message)
    
    def transformar(self, df):
        """
        Ejecuta todo el pipeline de transformación.
        
        Args:
            df: DataFrame original
            
        Returns:
            DataFrame completamente transformado
        """
        self._log("\n" + "=" * 60)
        self._log("🔄 INICIANDO PIPELINE DE TRANSFORMACIÓN")
        self._log("=" * 60)
        
        # Paso 1: Limpieza
        self._log("\n📌 Paso 1: Limpieza de datos")
        cleaner = DataCleaner()
        df = cleaner.limpiar_dataset(df)
        
        # Paso 2: Normalización de salarios
        self._log("\n📌 Paso 2: Normalización de salarios")
        normalizer = SalaryNormalizer()
        df = normalizer.normalizar_salarios(df)
        
        # Paso 3: Clasificación de seniority
        self._log("\n📌 Paso 3: Clasificación de seniority")
        seniority_classifier = SeniorityClassifier()
        df = seniority_classifier.clasificar_dataset(df)
        
        # Paso 4: Clasificación de tecnologías
        self._log("\n📌 Paso 4: Clasificación de tecnologías")
        tech_classifier = TechClassifier()
        df = tech_classifier.clasificar_dataset(df)
        
        self._log("\n" + "=" * 60)
        self._log("✅ TRANSFORMACIÓN COMPLETADA")
        self._log(f"📊 Dataset final: {len(df)} registros, {len(df.columns)} columnas")
        self._log("=" * 60)
        
        return df


def probar_transformacion_completa(df):
    """
    Prueba el pipeline completo de transformación.
    
    Args:
        df: DataFrame original
        
    Returns:
        DataFrame transformado
    """
    transformador = TransformadorCompleto()
    df_transformado = transformador.transformar(df)
    
    return df_transformado