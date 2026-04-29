-- ============================================
-- ESQUEMA DE BASE DE DATOS - JOBFORUS
-- Modelito para análisis de mercado laboral
-- ============================================

-- ============================================
-- ELIMINAR TABLAS SI EXISTEN (para limpiar)
-- ============================================
DROP TABLE IF EXISTS fact_oferta;
DROP TABLE IF EXISTS dim_tecnologia;
DROP TABLE IF EXISTS dim_seniority;
DROP TABLE IF EXISTS dim_empresa;
DROP TABLE IF EXISTS dim_ubicacion;

-- ============================================
-- TABLAS DE DIMENSIONES
-- ============================================

-- 1. Dimensión: Tecnología
CREATE TABLE dim_tecnologia (
    tecnologia_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    categoria VARCHAR(30) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Dimensión: Seniority (nivel de experiencia)
CREATE TABLE dim_seniority (
    seniority_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nivel VARCHAR(20) NOT NULL UNIQUE,
    años_min INTEGER,
    años_max INTEGER,
    descripcion TEXT
);

-- 3. Dimensión: Empresa
CREATE TABLE dim_empresa (
    empresa_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    tamano VARCHAR(50),
    pais_origen VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Dimensión: Ubicación
CREATE TABLE dim_ubicacion (
    ubicacion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ciudad VARCHAR(50),
    pais VARCHAR(50),
    remoto BOOLEAN DEFAULT 0,
    nombre_completo VARCHAR(100)
);

-- ============================================
-- TABLA DE HECHOS (OFERTAS LABORALES)
-- ============================================
CREATE TABLE fact_oferta (
    oferta_id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo VARCHAR(200) NOT NULL,
    salario_min_original DECIMAL(10,2),
    salario_max_original DECIMAL(10,2),
    salario_usd DECIMAL(10,2),
    experiencia_requerida INTEGER,
    fecha_publicacion DATE,
    skills TEXT,
    educacion_requerida VARCHAR(50),
    beneficios TEXT,
    fuente VARCHAR(50),
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tecnologia_id INTEGER,
    seniority_id INTEGER,
    empresa_id INTEGER,
    ubicacion_id INTEGER,
    FOREIGN KEY (tecnologia_id) REFERENCES dim_tecnologia(tecnologia_id),
    FOREIGN KEY (seniority_id) REFERENCES dim_seniority(seniority_id),
    FOREIGN KEY (empresa_id) REFERENCES dim_empresa(empresa_id),
    FOREIGN KEY (ubicacion_id) REFERENCES dim_ubicacion(ubicacion_id)
);

-- ============================================
-- ÍNDICES PARA MEJORAR EL RENDIMIENTO
-- ============================================
CREATE INDEX idx_oferta_salario ON fact_oferta(salario_usd);
CREATE INDEX idx_oferta_fecha ON fact_oferta(fecha_publicacion);
CREATE INDEX idx_oferta_tecnologia ON fact_oferta(tecnologia_id);
CREATE INDEX idx_oferta_seniority ON fact_oferta(seniority_id);
CREATE INDEX idx_oferta_empresa ON fact_oferta(empresa_id);
CREATE INDEX idx_oferta_ubicacion ON fact_oferta(ubicacion_id);

-- ============================================
-- VISTAS PARA ANÁLISIS COMUNES
-- ============================================

-- Vista 1: Salarios por tecnología
CREATE VIEW vw_salario_por_tecnologia AS
SELECT 
    t.nombre AS tecnologia,
    t.categoria,
    COUNT(o.oferta_id) AS cantidad_ofertas,
    ROUND(AVG(o.salario_usd), 2) AS salario_promedio,
    ROUND(MIN(o.salario_usd), 2) AS salario_minimo,
    ROUND(MAX(o.salario_usd), 2) AS salario_maximo
FROM fact_oferta o
JOIN dim_tecnologia t ON o.tecnologia_id = t.tecnologia_id
WHERE o.salario_usd IS NOT NULL
GROUP BY t.nombre, t.categoria;

-- Vista 2: Salarios por seniority
CREATE VIEW vw_salario_por_seniority AS
SELECT 
    s.nivel AS seniority,
    COUNT(o.oferta_id) AS cantidad_ofertas,
    ROUND(AVG(o.salario_usd), 2) AS salario_promedio,
    ROUND(MIN(o.salario_usd), 2) AS salario_minimo,
    ROUND(MAX(o.salario_usd), 2) AS salario_maximo
FROM fact_oferta o
JOIN dim_seniority s ON o.seniority_id = s.seniority_id
WHERE o.salario_usd IS NOT NULL
GROUP BY s.nivel;

-- Vista 3: Tecnologías más demandadas
CREATE VIEW vw_tecnologias_demandadas AS
SELECT 
    t.nombre AS tecnologia,
    t.categoria,
    COUNT(o.oferta_id) AS cantidad_ofertas,
    ROUND(COUNT(o.oferta_id) * 100.0 / (SELECT COUNT(*) FROM fact_oferta), 2) AS porcentaje
FROM fact_oferta o
JOIN dim_tecnologia t ON o.tecnologia_id = t.tecnologia_id
GROUP BY t.nombre, t.categoria
ORDER BY cantidad_ofertas DESC;

-- ============================================
-- INSERTAR DATOS POR DEFECTO (SENIORITY)
-- ============================================
INSERT OR IGNORE INTO dim_seniority (nivel, años_min, años_max, descripcion) VALUES 
('Junior', 0, 2, 'Profesional con 0-2 años de experiencia'),
('Mid', 3, 5, 'Profesional con 3-5 años de experiencia'),
('Senior', 6, 9, 'Profesional con 6-9 años de experiencia'),
('Lead', 10, 99, 'Profesional con 10+ años de experiencia o liderazgo'),
('No especificado', NULL, NULL, 'No se especificó la experiencia requerida');