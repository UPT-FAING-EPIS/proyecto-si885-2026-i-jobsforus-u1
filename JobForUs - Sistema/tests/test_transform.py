"""
Script de prueba del pipeline de transformación
Ubicado en: tests/test_transform.py
"""

import sys
import os

# Agregar la carpeta raíz del proyecto al path
proyecto_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(proyecto_root)

print(f"📁 Ruta del proyecto: {proyecto_root}")

from src.extract.github_jobs_extractor import LocalJobsExtractor
from src.transform import TransformadorCompleto


def test_transformacion_completa():
    """
    Prueba el pipeline completo de transformación
    """
    print("=" * 60)
    print("🚀 JOBFORUS - PRUEBA DE TRANSFORMACIÓN COMPLETA")
    print("=" * 60)
    
    # Paso 1: Extraer datos
    print("\n📥 PASO 1: Extrayendo datos...")
    extractor = LocalJobsExtractor()
    df_original = extractor.extraer_dataset()
    
    if df_original is None:
        print("❌ No se pudo extraer el dataset")
        return False
    
    print(f"   ✅ Dataset extraído: {len(df_original)} registros")
    
    # Paso 2: Transformar datos
    print("\n🔄 PASO 2: Transformando datos...")
    transformador = TransformadorCompleto()
    df_transformado = transformador.transformar(df_original)
    
    # Paso 3: Mostrar resultado
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL")
    print("=" * 60)
    print(f"   - Registros originales: {len(df_original)}")
    print(f"   - Registros transformados: {len(df_transformado)}")
    print(f"   - Columnas finales: {len(df_transformado.columns)}")
    
    # Mostrar primeras filas
    print("\n📋 Primeros 3 registros transformados:")
    print(df_transformado[['job_title', 'salary_usd', 'seniority', 'tecnologia_principal', 'categoria_principal']].head(3))
    
    return True


if __name__ == "__main__":
    test_transformacion_completa()