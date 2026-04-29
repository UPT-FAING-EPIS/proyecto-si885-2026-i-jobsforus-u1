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
    
    def limpiar_valor_salario(self, valor):
        """
        Limpia y convierte un valor de salario a número.
        
        Args:
            valor: Valor a limpiar (puede ser string con $, comas, etc.)
            
        Returns:
            Valor numérico o None
        """
        if pd.isna(valor):
            return None
        
        # Convertir a string si no lo es
        valor_str = str(valor)
        
        # Eliminar símbolos de moneda y otros caracteres no numéricos
        valor_str = valor_str.replace('$', '')
        valor_str = valor_str.replace(',', '')
        valor_str = valor_str.replace(' ', '')
        valor_str = valor_str.replace('USD', '')
        valor_str = valor_str.strip()
        
        try:
            return float(valor_str)
        except ValueError:
            return None
    
    def normalizar_salarios(self, df):
        """
        Normaliza los salarios calculando el promedio y convirtiendo a número.
        
        Args:
            df: DataFrame con columnas salary_min y salary_max
            
        Returns:
            DataFrame con nueva columna 'salary_usd' (numérica)
        """
        self._log("💰 Normalizando salarios...")
        
        # Crear copia para no modificar el original
        df_normalizado = df.copy()
        
        # Limpiar salary_min y salary_max si son strings
        if 'salary_min' in df_normalizado.columns:
            df_normalizado['salary_min'] = df_normalizado['salary_min'].apply(self.limpiar_valor_salario)
            self._log(f"   - Limpiados valores de salary_min")
        
        if 'salary_max' in df_normalizado.columns:
            df_normalizado['salary_max'] = df_normalizado['salary_max'].apply(self.limpiar_valor_salario)
            self._log(f"   - Limpiados valores de salary_max")
        
        # Calcular salario promedio
        if 'salary_min' in df_normalizado.columns and 'salary_max' in df_normalizado.columns:
            # Asegurar que sean numéricos
            df_normalizado['salary_min'] = pd.to_numeric(df_normalizado['salary_min'], errors='coerce')
            df_normalizado['salary_max'] = pd.to_numeric(df_normalizado['salary_max'], errors='coerce')
            
            # Calcular promedio
            df_normalizado['salary_usd'] = (df_normalizado['salary_min'] + df_normalizado['salary_max']) / 2
            df_normalizado['salary_usd'] = df_normalizado['salary_usd'].round(2)
            
            # Asegurar que salary_usd sea numérico
            df_normalizado['salary_usd'] = pd.to_numeric(df_normalizado['salary_usd'], errors='coerce')
            
            # Mostrar estadísticas
            salarios_validos = df_normalizado['salary_usd'].dropna()
            if len(salarios_validos) > 0:
                self._log(f"   - Rango salarial: ${salarios_validos.min():,.0f} - ${salarios_validos.max():,.0f}")
                self._log(f"   - Salario promedio: ${salarios_validos.mean():,.0f}")
                self._log(f"   - Salarios no válidos (null): {df_normalizado['salary_usd'].isna().sum()}")
            else:
                self._log(f"   - ⚠️ No hay salarios válidos en el dataset")
        
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
    
    # Verificar tipos
    print(f"\n📊 Verificación de tipos de datos:")
    print(f"   - salary_min: {df_normalizado['salary_min'].dtype}")
    print(f"   - salary_max: {df_normalizado['salary_max'].dtype}")
    print(f"   - salary_usd: {df_normalizado['salary_usd'].dtype}")
    
    return df_normalizado


if __name__ == "__main__":
    print("Este módulo debe ser importado, no ejecutado directamente.")
    print("Usa probar_normalizacion(df) desde otro script.")