"""
Prueba integrada del pipeline completo con el nuevo dataset global
JobForUs - Sistema de Inteligencia de Mercado Laboral

Este script ejecuta:
1. Extracción del dataset global
2. Transformación (con opción de filtro LATAM)
3. Carga a la base de datos SQLite
4. Verificación de resultados
"""

import sys
import os
import pandas as pd

# Agregar la carpeta raíz del proyecto al path
proyecto_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(proyecto_root)

from src.extract.github_jobs_extractor import LocalJobsExtractor
from src.transform.global_dataset_transformer import GlobalDatasetTransformer
from src.load.database_loader import DatabaseLoader


def print_seccion(titulo, caracter="=", longitud=70):
    """Imprime una sección formateada."""
    print("\n" + caracter * longitud)
    print(f" {titulo}")
    print(caracter * longitud)


def test_pipeline_completo(aplicar_filtro_latam=False, guardar_resultado=False):
    """
    Ejecuta el pipeline completo: Extracción -> Transformación -> Carga
    
    Args:
        aplicar_filtro_latam: Si es True, filtra solo países LATAM
        guardar_resultado: Si es True, guarda el dataset transformado en CSV
        
    Returns:
        True si todo fue exitoso, False en caso contrario
    """
    
    print_seccion("🚀 JOBFORUS - PIPELINE COMPLETO", "=", 70)
    
    # ============================================================
    # PASO 1: EXTRACCIÓN DE DATOS
    # ============================================================
    print_seccion("📥 PASO 1: EXTRACCIÓN DE DATOS", "-", 70)
    
    try:
        extractor = LocalJobsExtractor()
        df_original = extractor.extraer_dataset()
        
        if df_original is None:
            print("❌ Error: No se pudo extraer el dataset")
            return False
        
        print(f"\n✅ Extracción exitosa:")
        print(f"   - Registros: {len(df_original)}")
        print(f"   - Columnas: {len(df_original.columns)}")
        print(f"   - Columnas disponibles: {list(df_original.columns)[:10]}...")
        
    except Exception as e:
        print(f"❌ Error en extracción: {e}")
        return False
    
    # ============================================================
    # PASO 2: TRANSFORMACIÓN DE DATOS
    # ============================================================
    print_seccion("🔄 PASO 2: TRANSFORMACIÓN DE DATOS", "-", 70)
    
    if aplicar_filtro_latam:
        print(f"\n🌎 Aplicando filtro LATAM (países de Latinoamérica)")
    
    try:
        transformer = GlobalDatasetTransformer()
        df_transformado = transformer.transformar_completo(
            df_original, 
            aplicar_filtro_latam=aplicar_filtro_latam,
            guardar_resultado=guardar_resultado
        )
        
        if df_transformado is None or len(df_transformado) == 0:
            print("❌ Error: No se pudo transformar el dataset")
            return False
        
        print(f"\n✅ Transformación exitosa:")
        print(f"   - Registros originales: {len(df_original)}")
        print(f"   - Registros transformados: {len(df_transformado)}")
        print(f"   - Columnas finales: {len(df_transformado.columns)}")
        
        # Mostrar nuevas columnas agregadas
        nuevas_columnas = ['seniority_name', 'tecnologia_principal', 'categoria_principal', 'salary_usd']
        columnas_presentes = [col for col in nuevas_columnas if col in df_transformado.columns]
        if columnas_presentes:
            print(f"   - Nuevas columnas agregadas: {columnas_presentes}")
        
    except Exception as e:
        print(f"❌ Error en transformación: {e}")
        return False
    
    # ============================================================
    # PASO 3: CARGA A BASE DE DATOS
    # ============================================================
    print_seccion("💾 PASO 3: CARGA A BASE DE DATOS", "-", 70)
    
    try:
        loader = DatabaseLoader()
        resultado_carga = loader.cargar_dataset(df_transformado)
        
        if 'error' in resultado_carga:
            print(f"❌ Error en carga: {resultado_carga['error']}")
            return False
        
        print(f"\n✅ Carga exitosa:")
        print(f"   - Registros procesados: {resultado_carga['registros_procesados']}")
        print(f"   - Registros insertados: {resultado_carga['registros_insertados']}")
        print(f"   - Tecnologías únicas: {resultado_carga['tecnologias_insertadas']}")
        print(f"   - Empresas únicas: {resultado_carga['empresas_insertadas']}")
        print(f"   - Ubicaciones únicas: {resultado_carga['ubicaciones_insertadas']}")
        
    except Exception as e:
        print(f"❌ Error en carga: {e}")
        return False
    
    # ============================================================
    # PASO 4: VERIFICACIÓN DE RESULTADOS
    # ============================================================
    print_seccion("🔍 PASO 4: VERIFICACIÓN DE RESULTADOS", "-", 70)
    
    try:
        # Conectar a la base de datos para verificar
        conn = sqlite3.connect(loader.db_path)
        cursor = conn.cursor()
        
        # Verificar tablas creadas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = cursor.fetchall()
        print(f"\n📋 Tablas creadas en la base de datos:")
        for tabla in tablas:
            print(f"   - {tabla[0]}")
        
        # Verificar registros en fact_oferta
        cursor.execute("SELECT COUNT(*) FROM fact_oferta")
        total_ofertas = cursor.fetchone()[0]
        print(f"\n📊 Registros en fact_oferta: {total_ofertas}")
        
        # Verificar vistas creadas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        vistas = cursor.fetchall()
        print(f"\n📋 Vistas creadas:")
        for vista in vistas:
            print(f"   - {vista[0]}")
        
        # Verificar top tecnologías
        print(f"\n🏆 Top 5 tecnologías más demandadas:")
        cursor.execute("""
            SELECT nombre, categoria, cantidad_ofertas 
            FROM vw_tecnologias_demandadas 
            LIMIT 5
        """)
        top_tech = cursor.fetchall()
        for tech, cat, count in top_tech:
            print(f"   - {tech} ({cat}): {count} ofertas")
        
        # Verificar salarios por seniority
        print(f"\n💰 Salarios promedio por seniority:")
        cursor.execute("""
            SELECT seniority, salario_promedio 
            FROM vw_salario_por_seniority
        """)
        salarios = cursor.fetchall()
        for seniority, salario in salarios:
            print(f"   - {seniority}: ${salario:,.0f}")
        
        # Verificar distribución por género (si hay datos)
        cursor.execute("""
            SELECT gender, COUNT(*) as cantidad 
            FROM fact_oferta 
            WHERE gender IS NOT NULL AND gender != ''
            GROUP BY gender
        """)
        generos = cursor.fetchall()
        if generos:
            print(f"\n👥 Distribución por género:")
            for genero, cantidad in generos:
                print(f"   - {genero}: {cantidad} registros")
        
        # Verificar distribución por modalidad de trabajo
        cursor.execute("""
            SELECT work_setting, COUNT(*) as cantidad 
            FROM fact_oferta 
            WHERE work_setting IS NOT NULL
            GROUP BY work_setting
        """)
        work_settings = cursor.fetchall()
        if work_settings:
            print(f"\n💼 Distribución por modalidad de trabajo:")
            for setting, cantidad in work_settings:
                print(f"   - {setting}: {cantidad} registros")
        
        conn.close()
        
    except Exception as e:
        print(f"⚠️ Advertencia en verificación: {e}")
    
    # ============================================================
    # RESUMEN FINAL
    # ============================================================
    print_seccion("✅ PIPELINE COMPLETADO EXITOSAMENTE", "=", 70)
    print(f"\n📊 Resumen final:")
    print(f"   - Dataset original: {len(df_original)} registros")
    print(f"   - Dataset transformado: {len(df_transformado)} registros")
    print(f"   - Cargados a BD: {resultado_carga['registros_insertados']} registros")
    print(f"   - Tecnologías identificadas: {resultado_carga['tecnologias_insertadas']}")
    
    if aplicar_filtro_latam:
        print(f"\n🌎 Nota: Se aplicó filtro LATAM, solo se incluyeron países de Latinoamérica")
    
    return True


def test_solo_latam():
    """
    Ejecuta el pipeline completo con filtro LATAM
    """
    print_seccion("🌎 EJECUTANDO PIPELINE CON FILTRO LATAM", "=", 70)
    print("\nNota: Solo se incluirán países de Latinoamérica (Brazil, Argentina, Chile, México, Colombia, Perú, etc.)")
    
    return test_pipeline_completo(aplicar_filtro_latam=True, guardar_resultado=True)


def test_sin_filtro():
    """
    Ejecuta el pipeline completo sin filtro (datos globales)
    """
    return test_pipeline_completo(aplicar_filtro_latam=False, guardar_resultado=True)


if __name__ == "__main__":
    import sqlite3
    
    print("=" * 70)
    print("🧪 JOBFORUS - PRUEBA INTEGRADA DEL PIPELINE COMPLETO")
    print("=" * 70)
    print("\nSelecciona una opción:")
    print("   1. Ejecutar pipeline con DATOS GLOBALES (todos los países)")
    print("   2. Ejecutar pipeline con FILTRO LATAM (solo Latinoamérica)")
    print("   3. Ejecutar ambas pruebas")
    print("   4. Salir")
    
    opcion = input("\nIngresa tu opción (1-4): ").strip()
    
    if opcion == "1":
        test_sin_filtro()
    elif opcion == "2":
        test_solo_latam()
    elif opcion == "3":
        print("\n" + "=" * 70)
        print("📊 PRIMERA PRUEBA: DATOS GLOBALES")
        print("=" * 70)
        test_sin_filtro()
        
        print("\n" + "=" * 70)
        print("📊 SEGUNDA PRUEBA: FILTRO LATAM")
        print("=" * 70)
        test_solo_latam()
    else:
        print("Saliendo...")