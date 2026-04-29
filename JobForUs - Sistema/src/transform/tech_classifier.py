"""
Módulo de clasificación de tecnologías
JobForUs - Sistema de Inteligencia de Mercado Laboral
"""

import pandas as pd
import re


class TechClassifier:
    """
    Clase encargada de clasificar las tecnologías desde la columna 'skills'.
    """
    
    def __init__(self):
        self.logs = []
        
        # Diccionario de tecnologías por categoría
        self.tech_categories = {
            'Backend': ['Python', 'Java', 'Go', 'Node.js', 'Ruby', 'C#', '.NET', 'PHP'],
            'Frontend': ['React', 'Angular', 'Vue', 'JavaScript', 'TypeScript', 'HTML', 'CSS'],
            'Database': ['SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Oracle', 'Redis', 'SQLite'],
            'Cloud': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Cloud'],
            'DevOps': ['DevOps', 'CI/CD', 'Jenkins', 'Terraform', 'Ansible', 'Git'],
            'Data': ['Machine Learning', 'Data Science', 'AI', 'TensorFlow', 'Pandas', 'NumPy', 'Data']
        }
        
        # Lista plana de tecnologías para búsqueda
        self.all_techs = []
        for category, techs in self.tech_categories.items():
            for tech in techs:
                self.all_techs.append((tech.lower(), category, tech))
    
    def _log(self, message):
        """Registra un mensaje en el log."""
        self.logs.append(message)
        print(f"   {message}")
    
    def extraer_tecnologias(self, skills_texto):
        """
        Extrae las tecnologías presentes en el texto de skills.
        
        Args:
            skills_texto: Texto con las habilidades requeridas
            
        Returns:
            Lista de tecnologías encontradas
        """
        if pd.isna(skills_texto) or skills_texto == '':
            return []
        
        skills_texto_lower = skills_texto.lower()
        tecnologias_encontradas = []
        
        for tech_lower, categoria, tech_original in self.all_techs:
            if tech_lower in skills_texto_lower:
                tecnologias_encontradas.append(tech_original)
        
        return tecnologias_encontradas
    
    def clasificar_tecnologia_principal(self, tecnologias):
        """
        Determina la tecnología principal de la lista de tecnologías.
        
        Args:
            tecnologias: Lista de tecnologías encontradas
            
        Returns:
            Tecnología principal (la primera de la lista, o 'Sin tecnología')
        """
        if tecnologias and len(tecnologias) > 0:
            return tecnologias[0]
        return 'Sin tecnología'
    
    def clasificar_categoria_principal(self, tecnologias):
        """
        Determina la categoría principal basada en las tecnologías encontradas.
        
        Args:
            tecnologias: Lista de tecnologías encontradas
            
        Returns:
            Categoría principal
        """
        if not tecnologias:
            return 'No especificada'
        
        # Contar tecnologías por categoría
        conteo_categorias = {}
        for tech in tecnologias:
            tech_lower = tech.lower()
            for categoria, techs in self.tech_categories.items():
                for t in techs:
                    if t.lower() == tech_lower:
                        conteo_categorias[categoria] = conteo_categorias.get(categoria, 0) + 1
                        break
        
        if conteo_categorias:
            return max(conteo_categorias, key=conteo_categorias.get)
        return 'No especificada'
    
    def clasificar_dataset(self, df):
        """
        Clasifica todo el dataset agregando columnas de tecnologías.
        
        Args:
            df: DataFrame con columna 'skills'
            
        Returns:
            DataFrame con nuevas columnas 'tecnologias', 'tecnologia_principal', 'categoria_principal'
        """
        self._log("🔧 Clasificando tecnologías...")
        
        df_clasificado = df.copy()
        
        if 'skills' in df_clasificado.columns:
            # Extraer tecnologías
            df_clasificado['tecnologias'] = df_clasificado['skills'].apply(self.extraer_tecnologias)
            
            # Determinar tecnología principal
            df_clasificado['tecnologia_principal'] = df_clasificado['tecnologias'].apply(
                self.clasificar_tecnologia_principal
            )
            
            # Determinar categoría principal
            df_clasificado['categoria_principal'] = df_clasificado['tecnologias'].apply(
                self.clasificar_categoria_principal
            )
            
            # Mostrar estadísticas
            self._log(f"\n   📊 Tecnologías más comunes:")
            top_techs = df_clasificado['tecnologia_principal'].value_counts().head(10)
            for tech, count in top_techs.items():
                if tech != 'Sin tecnología':
                    self._log(f"      - {tech}: {count} ofertas")
            
            self._log(f"\n   📊 Categorías principales:")
            top_cats = df_clasificado['categoria_principal'].value_counts()
            for cat, count in top_cats.items():
                porcentaje = (count / len(df_clasificado)) * 100
                self._log(f"      - {cat}: {count} ofertas ({porcentaje:.1f}%)")
        else:
            self._log("   ⚠️ No se encontró columna 'skills'")
            df_clasificado['tecnologia_principal'] = 'No disponible'
            df_clasificado['categoria_principal'] = 'No disponible'
        
        return df_clasificado
    
    def obtener_logs(self):
        """Retorna los logs del proceso."""
        return self.logs


def probar_clasificacion_tecnologias(df):
    """
    Función de prueba para el módulo de clasificación de tecnologías.
    
    Args:
        df: DataFrame a clasificar
        
    Returns:
        DataFrame clasificado
    """
    print("\n" + "=" * 50)
    print("🔧 PRUEBA DE CLASIFICACIÓN DE TECNOLOGÍAS")
    print("=" * 50)
    
    classifier = TechClassifier()
    df_clasificado = classifier.clasificar_dataset(df)
    
    return df_clasificado


if __name__ == "__main__":
    print("Este módulo debe ser importado, no ejecutado directamente.")
    print("Usa probar_clasificacion_tecnologias(df) desde otro script.")