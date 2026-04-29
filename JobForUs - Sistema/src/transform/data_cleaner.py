"""
Módulo de limpieza de datos
JobForUs - Sistema de Inteligencia de Mercado Laboral
"""

import pandas as pd
import numpy as np


class DataCleaner:
    """
    Clase encargada de limpiar y validar los datos extraídos.
    """
    
    def __init__(self):
        self.logs = []
        self.estadisticas = {}
    
    def _log(self, message):
        """Registra un mensaje en el log."""
        self.logs.append(message)
        print(f"   {message}")
    
    def limpiar_dataset(self, df):
        """
        Limpia el dataset eliminando registros no válidos.
        
        Args:
            df: DataFrame original
            
        Returns:
            DataFrame limpio
        """
        self._log("🧹 Iniciando limpieza de datos...")
        registros_iniciales = len(df)
        
        # 1. Eliminar filas completamente vacías
        df = df.dropna(how='all')
        self._log(f"   - Eliminadas {registros_iniciales - len(df)} filas completamente vacías")
        
        # 2. Filtrar solo tecnología (categoria = Technology)
        if 'category' in df.columns:
            tecnologia_df = df[df['category'] == 'Technology']
            self._log(f"   - Filtradas {len(tecnologia_df)} ofertas del sector tecnología")
        else:
            tecnologia_df = df
            self._log("   - No se encontró columna 'category', se mantienen todas las ofertas")
        
        # 3. Eliminar filas sin título de trabajo
        if 'job_title' in tecnologia_df.columns:
            antes = len(tecnologia_df)
            tecnologia_df = tecnologia_df[tecnologia_df['job_title'].notna()]
            tecnologia_df = tecnologia_df[tecnologia_df['job_title'] != '']
            self._log(f"   - Eliminadas {antes - len(tecnologia_df)} filas sin título de trabajo")
        
        # 4. Eliminar filas sin salario válido
        if 'salary_min' in tecnologia_df.columns and 'salary_max' in tecnologia_df.columns:
            antes = len(tecnologia_df)
            tecnologia_df = tecnologia_df[tecnologia_df['salary_min'].notna()]
            tecnologia_df = tecnologia_df[tecnologia_df['salary_max'].notna()]
            tecnologia_df = tecnologia_df[tecnologia_df['salary_min'] > 0]
            tecnologia_df = tecnologia_df[tecnologia_df['salary_max'] > 0]
            self._log(f"   - Eliminadas {antes - len(tecnologia_df)} filas sin salario válido")
        
        # 5. Eliminar duplicados
        antes = len(tecnologia_df)
        tecnologia_df = tecnologia_df.drop_duplicates(subset=['job_title', 'company', 'location'])
        self._log(f"   - Eliminadas {antes - len(tecnologia_df)} filas duplicadas")
        
        # Registrar estadísticas
        self.estadisticas = {
            'registros_iniciales': registros_iniciales,
            'registros_finales': len(tecnologia_df),
            'eliminados': registros_iniciales - len(tecnologia_df),
            'tasa_limpieza': ((registros_iniciales - len(tecnologia_df)) / registros_iniciales) * 100
        }
        
        self._log(f"\n✅ Limpieza completada:")
        self._log(f"   - Registros iniciales: {registros_iniciales}")
        self._log(f"   - Registros finales: {len(tecnologia_df)}")
        self._log(f"   - Eliminados: {self.estadisticas['eliminados']} ({self.estadisticas['tasa_limpieza']:.1f}%)")
        
        return tecnologia_df
    
    def obtener_logs(self):
        """Retorna los logs del proceso."""
        return self.logs
    
    def obtener_estadisticas(self):
        """Retorna las estadísticas del proceso."""
        return self.estadisticas


def probar_limpieza(df):
    """
    Función de prueba para el módulo de limpieza.
    
    Args:
        df: DataFrame a limpiar
        
    Returns:
        DataFrame limpio
    """
    print("\n" + "=" * 50)
    print("🔧 PRUEBA DEL MÓDULO DE LIMPIEZA")
    print("=" * 50)
    
    cleaner = DataCleaner()
    df_limpio = cleaner.limpiar_dataset(df)
    
    return df_limpio


if __name__ == "__main__":
    print("Este módulo debe ser importado, no ejecutado directamente.")
    print("Usa probar_limpieza(df) desde otro script.")