"""
Módulo de clasificación de seniority
JobForUs - Sistema de Inteligencia de Mercado Laboral
"""

import pandas as pd
import numpy as np


class SeniorityClassifier:
    """
    Clase encargada de clasificar el seniority según los años de experiencia.
    """
    
    def __init__(self):
        self.logs = []
        self.reglas = {
            'Junior': (0, 2),
            'Mid': (3, 5),
            'Senior': (6, 9),
            'Lead': (10, 99)
        }
    
    def _log(self, message):
        """Registra un mensaje en el log."""
        self.logs.append(message)
        print(f"   {message}")
    
    def clasificar_por_experiencia(self, años):
        """
        Clasifica el seniority según los años de experiencia.
        
        Args:
            años: Número de años de experiencia
            
        Returns:
            String con el nivel de seniority
        """
        if pd.isna(años):
            return 'No especificado'
        
        for nivel, (min_años, max_años) in self.reglas.items():
            if min_años <= años <= max_años:
                return nivel
        
        return 'No especificado'
    
    def clasificar_dataset(self, df):
        """
        Clasifica todo el dataset agregando columna 'seniority'.
        
        Args:
            df: DataFrame con columna 'experience_required'
            
        Returns:
            DataFrame con nueva columna 'seniority'
        """
        self._log("🏷️ Clasificando seniority...")
        
        df_clasificado = df.copy()
        
        if 'experience_required' in df_clasificado.columns:
            df_clasificado['seniority'] = df_clasificado['experience_required'].apply(
                self.clasificar_por_experiencia
            )
            
            # Mostrar distribución
            distribucion = df_clasificado['seniority'].value_counts()
            self._log(f"\n   📊 Distribución de seniority:")
            for nivel, cantidad in distribucion.items():
                porcentaje = (cantidad / len(df_clasificado)) * 100
                self._log(f"      - {nivel}: {cantidad} ofertas ({porcentaje:.1f}%)")
        else:
            self._log("   ⚠️ No se encontró columna 'experience_required'")
            df_clasificado['seniority'] = 'No especificado'
        
        return df_clasificado
    
    def obtener_logs(self):
        """Retorna los logs del proceso."""
        return self.logs


def probar_clasificacion_seniority(df):
    """
    Función de prueba para el módulo de clasificación de seniority.
    
    Args:
        df: DataFrame a clasificar
        
    Returns:
        DataFrame clasificado
    """
    print("\n" + "=" * 50)
    print("🏷️ PRUEBA DE CLASIFICACIÓN DE SENIORITY")
    print("=" * 50)
    
    classifier = SeniorityClassifier()
    df_clasificado = classifier.clasificar_dataset(df)
    
    return df_clasificado


if __name__ == "__main__":
    print("Este módulo debe ser importado, no ejecutado directamente.")
    print("Usa probar_clasificacion_seniority(df) desde otro script.")