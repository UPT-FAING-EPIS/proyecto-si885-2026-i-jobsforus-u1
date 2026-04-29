"""
Script de prueba del extractor de datos
Ubicado en: tests/test_extractor.py
"""

import sys
import os

# Agregar la carpeta raíz del proyecto al path
# Esto permite importar desde src
# os.path.dirname(os.path.dirname(__file__)) sube dos niveles:
#   tests/test_extractor.py -> tests/ -> JobForUs - Sistema/
proyecto_root = os.path.dirname(os.path.dirname(os.path.abspath("tests/test_extractor.py")))
sys.path.append(proyecto_root)

print(f"📁 Ruta del proyecto: {proyecto_root}")

# Ahora importamos desde src
from src.extract.github_jobs_extractor import LocalJobsExtractor


if __name__ == "__main__":
    print("🚀 JOBFORUS - PRUEBA DE EXTRACCIÓN\n")
    
    extractor = LocalJobsExtractor()
    df = extractor.extraer_dataset()
    
    if df is not None:
        print(f"\n✅ Dataset cargado correctamente")
        print(f"   - Filas: {len(df)}")
        print(f"   - Columnas: {len(df.columns)}")
        
        # Verificar valores nulos
        nulls = df.isnull().sum()
        if nulls.sum() > 0:
            print(f"\n⚠️ Columnas con valores nulos:")
            for col in nulls[nulls > 0].index:
                print(f"   - {col}: {nulls[col]} nulos")
        else:
            print(f"\n✅ No hay valores nulos en el dataset")
        
        # Verificar distribución de salarios
        print(f"\n📊 Distribución de salarios mínimos:")
        print(f"   - Min: ${df['salary_min'].min():,.0f}")
        print(f"   - Max: ${df['salary_min'].max():,.0f}")
        print(f"   - Promedio: ${df['salary_min'].mean():,.0f}")
        
        # Verificar tipos de empleo
        print(f"\n📊 Tipos de empleo:")
        print(df['job_type'].value_counts())
        
        # Verificar categorías
        print(f"\n📊 Categorías:")
        print(df['category'].value_counts())