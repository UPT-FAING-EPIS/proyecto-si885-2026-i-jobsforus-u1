"""
Transformador específico para el dataset global_ai_tech_salaries_2020_2025.csv
JobForUs - Sistema de Inteligencia de Mercado Laboral
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime


class GlobalDatasetTransformer:
    """
    Clase específica para transformar el dataset global de salarios tecnológicos.
    """
    
    def __init__(self):
        self.logs = []
        self.estadisticas = {}
        
        # Mapeo de experience_level a valores numéricos
        self.experience_map = {
            'Entry (0-2 yrs)': 1,      # Junior
            'Mid (3-5 yrs)': 2,        # Mid
            'Senior (6-10 yrs)': 3,    # Senior
            'Lead (11-15 yrs)': 4      # Lead
        }
        
        # Mapeo inverso para nombres amigables
        self.seniority_names = {
            'Entry (0-2 yrs)': 'Junior',
            'Mid (3-5 yrs)': 'Mid',
            'Senior (6-10 yrs)': 'Senior',
            'Lead (11-15 yrs)': 'Lead'
        }
    
    def _log(self, message, level="INFO"):
        """Registra un mensaje en el log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.logs.append(log_entry)
        print(log_entry)
    
    def limpiar_datos(self, df):
        """
        Limpia los datos del dataset global.
        """
        self._log("🧹 Iniciando limpieza de datos...")
        registros_iniciales = len(df)
        
        # Eliminar filas con valores nulos críticos
        columnas_criticas = ['job_title', 'base_salary_usd', 'country', 'experience_level']
        for col in columnas_criticas:
            if col in df.columns:
                antes = len(df)
                df = df[df[col].notna()]
                self._log(f"   - Eliminados {antes - len(df)} registros sin '{col}'")
        
        # Eliminar duplicados
        antes = len(df)
        columnas_dup = ['job_title', 'country', 'survey_year', 'base_salary_usd']
        columnas_dup_existentes = [col for col in columnas_dup if col in df.columns]
        if columnas_dup_existentes:
            df = df.drop_duplicates(subset=columnas_dup_existentes)
            self._log(f"   - Eliminados {antes - len(df)} registros duplicados")
        
        # Eliminar salarios atípicos (outliers)
        if 'base_salary_usd' in df.columns:
            Q1 = df['base_salary_usd'].quantile(0.25)
            Q3 = df['base_salary_usd'].quantile(0.75)
            IQR = Q3 - Q1
            limite_inferior = Q1 - 3 * IQR
            limite_superior = Q3 + 3 * IQR
            
            antes = len(df)
            df = df[(df['base_salary_usd'] >= limite_inferior) & 
                    (df['base_salary_usd'] <= limite_superior)]
            self._log(f"   - Eliminados {antes - len(df)} outliers salariales")
        
        self.estadisticas['registros_iniciales'] = registros_iniciales
        self.estadisticas['registros_finales'] = len(df)
        self.estadisticas['tasa_limpieza'] = ((registros_iniciales - len(df)) / registros_iniciales) * 100
        
        self._log(f"\n✅ Limpieza completada:")
        self._log(f"   - Registros iniciales: {registros_iniciales}")
        self._log(f"   - Registros finales: {len(df)}")
        
        return df
    
    def normalizar_salarios(self, df):
        """
        Normaliza los salarios y crea alias para compatibilidad.
        """
        self._log("💰 Normalizando salarios...")
        
        if 'base_salary_usd' in df.columns:
            df['base_salary_usd'] = pd.to_numeric(df['base_salary_usd'], errors='coerce')
            # Crear alias 'salary_usd' para compatibilidad con dashboard existente
            df['salary_usd'] = df['base_salary_usd']
            self._log(f"   - Salario base: ${df['base_salary_usd'].mean():,.0f} promedio")
        
        if 'total_compensation_usd' in df.columns:
            df['total_compensation_usd'] = pd.to_numeric(df['total_compensation_usd'], errors='coerce')
            self._log(f"   - Compensación total: ${df['total_compensation_usd'].mean():,.0f} promedio")
        
        return df
    
    def clasificar_seniority(self, df):
        """
        Clasifica el seniority basado en experience_level.
        """
        self._log("🏷️ Clasificando seniority...")
        
        if 'experience_level' in df.columns:
            df['seniority_name'] = df['experience_level'].map(self.seniority_names)
            df['seniority_name'] = df['seniority_name'].fillna('No especificado')
            df['seniority_code'] = df['experience_level'].map(self.experience_map)
            df['seniority_code'] = df['seniority_code'].fillna(0)
            
            # Distribución
            distribucion = df['seniority_name'].value_counts()
            self._log(f"\n   📊 Distribución de seniority:")
            for nivel, cantidad in distribucion.items():
                porcentaje = (cantidad / len(df)) * 100
                self._log(f"      - {nivel}: {cantidad} registros ({porcentaje:.1f}%)")
        else:
            self._log("   ⚠️ No se encontró columna 'experience_level'")
            df['seniority_name'] = 'No especificado'
            df['seniority_code'] = 0
        
        return df
    
    def clasificar_tecnologias(self, df):
        """
        Extrae y clasifica tecnologías desde primary_skills.
        """
        self._log("🔧 Clasificando tecnologías...")
        
        tech_categories = {
            'Backend': ['Python', 'Java', 'Go', 'Node.js', 'Ruby', 'C#', '.NET', 'Rust', 'C++'],
            'Frontend': ['JavaScript', 'TypeScript', 'React', 'Angular', 'Vue', 'HTML', 'CSS'],
            'Database': ['SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Oracle', 'Redis', 'dbt'],
            'Cloud': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Cloud'],
            'DevOps': ['DevOps', 'CI/CD', 'Jenkins', 'Terraform', 'Ansible', 'Git', 'Airflow'],
            'Data': ['Pandas', 'NumPy', 'Spark', 'Hadoop', 'Tableau', 'Power BI', 'Excel', 'Kafka'],
            'AI/ML': ['PyTorch', 'TensorFlow', 'Hugging Face', 'LangChain', 'OpenCV', 'Machine Learning', 'AI']
        }
        
        def extraer_tecnologia_principal(skills_texto):
            if pd.isna(skills_texto) or skills_texto == '':
                return 'Sin tecnología'
            skills_texto = str(skills_texto)
            for categoria, tecnologias in tech_categories.items():
                for tech in tecnologias:
                    if tech.lower() in skills_texto.lower():
                        return tech
            return 'Otra'
        
        def extraer_categoria_principal(skills_texto):
            if pd.isna(skills_texto) or skills_texto == '':
                return 'No especificada'
            skills_texto = str(skills_texto)
            for categoria, tecnologias in tech_categories.items():
                for tech in tecnologias:
                    if tech.lower() in skills_texto.lower():
                        return categoria
            return 'Otra'
        
        if 'primary_skills' in df.columns:
            df['tecnologia_principal'] = df['primary_skills'].apply(extraer_tecnologia_principal)
            df['categoria_principal'] = df['primary_skills'].apply(extraer_categoria_principal)
            
            top_tech = df['tecnologia_principal'].value_counts().head(10)
            self._log(f"\n   📊 Top 10 tecnologías:")
            for tech, count in top_tech.items():
                if tech != 'Sin tecnología':
                    self._log(f"      - {tech}: {count} registros")
            
            top_cats = df['categoria_principal'].value_counts()
            self._log(f"\n   📊 Categorías principales:")
            for cat, count in top_cats.items():
                if cat != 'No especificada':
                    porcentaje = (count / len(df)) * 100
                    self._log(f"      - {cat}: {count} registros ({porcentaje:.1f}%)")
        else:
            self._log("   ⚠️ No se encontró columna 'primary_skills'")
            df['tecnologia_principal'] = 'No disponible'
            df['categoria_principal'] = 'No disponible'
        
        return df
    
    def filtrar_latinoamerica(self, df):
        """
        Filtra el dataframe para incluir solo países de Latinoamérica.
        """
        paises_latam = ['Brazil', 'Argentina', 'Chile', 'Mexico', 'Colombia', 'Peru', 
                        'Uruguay', 'Paraguay', 'Ecuador', 'Bolivia', 'Venezuela']
        
        if 'country' in df.columns:
            df_latam = df[df['country'].isin(paises_latam)]
            self._log(f"\n🌎 Filtro LATAM aplicado: {len(df_latam)} registros")
            return df_latam
        
        return df
    
    def guardar_dataset_transformado(self, df, output_path="../data/processed/global_dataset_transformado.csv"):
        """
        Guarda el dataset transformado en un archivo CSV.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        self._log(f"💾 Dataset transformado guardado en: {output_path}")
    
    def transformar_completo(self, df, aplicar_filtro_latam=False, guardar_resultado=False):
        """
        Ejecuta todo el pipeline de transformación.
        """
        self._log("\n" + "=" * 60)
        self._log("🔄 INICIANDO TRANSFORMACIÓN DEL DATASET GLOBAL")
        self._log("=" * 60)
        
        # Validación inicial
        columnas_requeridas = ['job_title', 'base_salary_usd', 'country', 'experience_level']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        
        if columnas_faltantes:
            self._log(f"❌ Columnas requeridas no encontradas: {columnas_faltantes}", "ERROR")
            return None
        
        # Paso 1: Limpieza
        self._log("\n📌 Paso 1: Limpieza de datos")
        df = self.limpiar_datos(df)
        
        if df is None or len(df) == 0:
            self._log("❌ No hay datos después de la limpieza", "ERROR")
            return None
        
        # Paso 1.5: Filtrar LATAM
        if aplicar_filtro_latam:
            self._log("\n📌 Paso 1.5: Filtrado geográfico")
            df = self.filtrar_latinoamerica(df)
        
        # Paso 2: Normalización
        self._log("\n📌 Paso 2: Normalización de salarios")
        df = self.normalizar_salarios(df)
        
        # Paso 3: Clasificar seniority
        self._log("\n📌 Paso 3: Clasificación de seniority")
        df = self.clasificar_seniority(df)
        
        # Paso 4: Clasificar tecnologías
        self._log("\n📌 Paso 4: Clasificación de tecnologías")
        df = self.clasificar_tecnologias(df)
        
        # Guardar resultado si se solicita
        if guardar_resultado:
            self.guardar_dataset_transformado(df)
        
        self._log("\n" + "=" * 60)
        self._log("✅ TRANSFORMACIÓN COMPLETADA")
        self._log(f"📊 Dataset final: {len(df)} registros, {len(df.columns)} columnas")
        self._log("=" * 60)
        
        return df
    
    def obtener_logs(self):
        return self.logs
    
    def obtener_estadisticas(self):
        return self.estadisticas


def probar_transformacion(df):
    """
    Función de prueba para el transformador del dataset global.
    """
    print("\n" + "=" * 60)
    print("🧪 PRUEBA DEL TRANSFORMADOR DE DATASET GLOBAL")
    print("=" * 60)
    
    transformer = GlobalDatasetTransformer()
    df_transformado = transformer.transformar_completo(df, aplicar_filtro_latam=False)
    
    if df_transformado is not None:
        print(f"\n✅ Transformación exitosa: {len(df_transformado)} registros")
    else:
        print("\n❌ Transformación fallida")
    
    return df_transformado


if __name__ == "__main__":
    print("Este módulo debe ser importado, no ejecutado directamente.")
    print("Usa probar_transformacion(df) desde otro script.")