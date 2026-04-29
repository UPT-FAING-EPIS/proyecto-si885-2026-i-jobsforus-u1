"""
Módulo de normalización de salarios
JobForUs - Sistema de Inteligencia de Mercado Laboral
"""

import pandas as pd
import numpy as np


class SalaryNormalizer:
    """
    Clase encargada de normalizar los salarios.
    """
    
    def __init__(self):
        self.logs = []
    
    def _log(self, message):
        """Registra un mensaje en el log."""
        self.logs.append(message)
        print(f"   {message}")
    
    def normalizar_salarios(self, df):
        """
        Normaliza los salarios calculando el promedio y convirtiendo a USD.
        
        Args:
            df: DataFrame con columnas salary_min y salary_max
            
        Returns:
            DataFrame con nueva columna 'salary_usd'
        """
        self._log("💰 Normalizando salarios...")
        
        # Crear copia para no modificar el original
        df_normalizado = df.copy()
        
        # Calcular salario promedio
        if 'salary_min' in df_normalizado.columns and 'salary_max' in df_normalizado.columns:
            df_normalizado['salary_usd'] = (df_normalizado['salary_min'] + df_normalizado['salary_max']) / 2
            df_normalizado['salary_usd'] = df_normalizado['salary_usd'].round(2)
            
            self._log(f"   - Salarios normalizados a USD (promedio entre min y max)")
            self._log(f"   - Rango salarial: ${df_normalizado['salary_usd'].min():,.0f} - ${df_normalizado['salary_usd'].max():,.0f}")
            self._log(f"   - Salario promedio: ${df_normalizado['salary_usd'].mean():,.0f}")
        
        return df_normalizado
    
    def obtener_logs(self):
        """Retorna los logs del proceso."""
        return self.logs


def probar_normalizacion(df):
    """
    Función de prueba para el módulo de normalización.
    
    Args:
        df: DataFrame a normalizar
        
    Returns:
        DataFrame normalizado
    """
    print("\n" + "=" * 50)
    print("💰 PRUEBA DEL MÓDULO DE NORMALIZACIÓN")
    print("=" * 50)
    
    normalizer = SalaryNormalizer()
    df_normalizado = normalizer.normalizar_salarios(df)
    
    return df_normalizado


if __name__ == "__main__":
    print("Este módulo debe ser importado, no ejecutado directamente.")
    print("Usa probar_normalizacion(df) desde otro script.")