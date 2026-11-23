# -*- coding: utf-8 -*-
"""Datos del catálogo Fase 2 (v2.3). Fuente: Fase 2 principio.txt, sección 11.
Precios sin impuestos, en PEN. Sin códigos de barras (D3). Sin imágenes (D5)."""

PREFIX_CAT = {
    'YES': 'CAT-YES', 'PLA': 'CAT-PLA', 'DEC': 'CAT-DEC',
    'MAS': 'CAT-MAS', 'MAT': 'CAT-MAT', 'HER': 'CAT-HER',
}

# code, name, cost_method, routes, lot_tracking, is_storable
CATEGORIES = [
    ('CAT-YES', 'Yesos de Construcción', 'average', ('buy', 'mfg'), True, True),
    ('CAT-PLA', 'Placas y Derivados', 'average', ('buy',), False, True),
    ('CAT-DEC', 'Productos Decorativos', 'standard', ('buy',), False, True),
    ('CAT-MAS', 'Masillas y Mezclas', 'average', ('buy', 'mfg'), True, True),
    ('CAT-MAT', 'Materias Primas', 'average', ('buy',), True, True),
    ('CAT-HER', 'Herramientas y Accesorios', 'standard', ('buy',), False, False),
]

# key -> (name, base 'kg' | 'unit', relative_factor)
UOM_CREATE = {
    'SAC5': ('Saco 5 kg', 'kg', 5),
    'SAC10': ('Saco 10 kg', 'kg', 10),
    'SAC20': ('Saco 20 kg', 'kg', 20),
    'SAC25': ('Saco 25 kg', 'kg', 25),
    'SAC30': ('Saco 30 kg', 'kg', 30),
    'SAC40': ('Saco 40 kg', 'kg', 40),
    'SAC50': ('Saco 50 kg', 'kg', 50),
    'PAQ10': ('Paquete x10', 'unit', 10),
}

# name, create_variant, display_type, [(value, sequence)]
# D12: 'always' en vez de 'dynamic'. Con 'dynamic' Odoo solo crea la variante al vender,
# y las variantes con SKU propio deben existir en el catálogo.
ATTRIBUTES = [
    ('Presentación', 'always', 'radio',
     [('Saco', 10), ('Granel', 20), ('Unidad', 30), ('Paquete', 40)]),
    ('Peso del saco', 'always', 'radio',
     [('5 kg', 10), ('10 kg', 20), ('20 kg', 30), ('25 kg', 40),
      ('30 kg', 50), ('40 kg', 60), ('50 kg', 70)]),
    ('Dimensión', 'always', 'radio',
     [('1.2 x 2.4 m', 10), ('60 x 60 cm', 20), ('50 x 50 cm', 30),
      ('9.5 mm', 40), ('12.5 mm', 50), ('15 mm', 60),
      ('50 cm', 70), ('80 cm', 80)]),
    ('Color', 'always', 'color',
     [('Blanco', 10), ('Beige', 20), ('Gris', 30)]),
]

# name, color (int)
TAGS = [
    ('Nuevo Producto', 10), ('En Promoción', 1), ('Ecológico', 5),
    ('Premium', 3), ('Industrial', 11), ('Resistente', 4),
    ('Fraguado Rápido', 2), ('Ignífugo', 13), ('Acústico', 7),
    ('Impermeable', 9),
]

# code, name, discount %, min qty, selectable
PRICELISTS = [
    ('PRICELIST-001', 'Lista Pública PEN', 0, 0, True),
    ('PRICELIST-002', 'Lista Mayorista PEN', 10, 10, True),
    ('PRICELIST-003', 'Lista Distribuidor PEN', 18, 50, True),
    ('PRICELIST-004', 'Lista Corporativa PEN', 15, 20, True),
    ('PRICELIST-005', 'Lista Promocional PEN', 5, 0, False),
]

# Proveedores (v2.1 sección 9) con RUC válido (dígito verificador SUNAT).
SUPPLIERS = [
    ('Minera Yesos del Sur S.A.C.', 'Juliaca'),
    ('Cantera Andina de Yeso S.A.', 'Puno'),
    ('Yesos Premium del Altiplano E.I.R.L.', 'Juliaca'),
    ('AgroYeso Perú S.A.C.', 'Arequipa'),
    ('Suministros Médicos Andinos S.A.C.', 'Cusco'),
    ('Placas Industriales del Sur S.A.', 'Lima'),
    ('Perfiles y Accesorios Metálicos JJS S.A.C.', 'Lima'),
    ('Cintas y Accesorios de Construcción S.A.', 'Lima'),
    ('Cementos y Placas del Sur S.A.C.', 'Arequipa'),
    ('Decorados en Yeso Artesanal E.I.R.L.', 'Puno'),
    ('Molduras y Columnas del Sur S.A.C.', 'Cusco'),
    ('Masillas y Mezclas Industriales S.A.', 'Lima'),
    ('Químicos de Construcción Andina S.A.C.', 'Lima'),
    ('Aditivos Químicos del Sur S.A.C.', 'Arequipa'),
    ('Pinturas y Recubrimientos JJS S.A.C.', 'Lima'),
    ('Cantera Central de Yeso S.A.', 'Juliaca'),
    ('Minas y Canteras del Altiplano S.A.A.', 'Puno'),
    ('Químicos Industriales Andinos S.A.', 'Lima'),
    ('Energía y Combustibles del Altiplano S.A.C.', 'Juliaca'),
    ('Gas Natural del Sur S.R.L.', 'Arequipa'),
    ('Empaques y Envases JJSUMI S.A.C.', 'Juliaca'),
    ('Flejes y Embalajes Industriales S.A.C.', 'Lima'),
    ('Lubricantes y Grasas Industriales S.A.', 'Lima'),
    ('Ferretería Industrial Global S.A.C.', 'Lima'),
    ('Pinturas Industriales del Sur S.A.C.', 'Arequipa'),
    ('Herramientas y Fijaciones Andinas S.A.C.', 'Lima'),
    ('Maquinaria y Herramientas Eléctricas S.A.', 'Lima'),
    ('Plásticos y Accesorios de Construcción S.A.', 'Lima'),
    ('Equipos de Seguridad Industrial S.A.C.', 'Lima'),
    ('Transportes y Logística del Sur S.A.C.', 'Juliaca'),
    ('Servicios de Mantenimiento Industrial S.A.', 'Juliaca'),
    ('Imprenta y Papelería JJSUMI S.A.C.', 'Juliaca'),
    ('Suministros de Oficina JJS S.A.C.', 'Juliaca'),
    ('Servicios de Limpieza Industrial S.A.C.', 'Arequipa'),
    ('Asesoría Legal y Contable JJS S.A.C.', 'Lima'),
]

# Proveedor por categoría (índices 1-based en SUPPLIERS).
SUPPLIER_MAP = {
    'CAT-YES': [1, 2, 3], 'CAT-PLA': [6, 7, 8], 'CAT-DEC': [10, 11],
    'CAT-MAS': [12, 13], 'CAT-MAT': [16, 17, 18], 'CAT-HER': [26, 27, 29],
}

# sku, name, uom key, cost, price (sin impuestos)
PRODUCTS = [
    # Yesos
    ('YES-001', 'Yeso Fino Extra Andino', 'SAC25', 18.50, 28.00),
    ('YES-002', 'Yeso Industrial 40kg', 'SAC40', 24.00, 35.00),
    ('YES-003', 'Yeso de Fraguado Rápido 25kg', 'SAC25', 21.00, 32.00),
    ('YES-004', 'Yeso para Moldes 25kg', 'SAC25', 22.50, 34.00),
    ('YES-005', 'Yeso Proyectado 30kg', 'SAC30', 26.00, 39.00),
    ('YES-006', 'Yeso Blanco Premium 20kg', 'SAC20', 19.00, 29.50),
    ('YES-007', 'Yeso Grueso de Construcción 40kg', 'SAC40', 23.00, 34.50),
    ('YES-008', 'Yeso Agrícola 50kg', 'SAC50', 15.00, 24.00),
    ('YES-009', 'Yeso en Polvo a Granel', 'TON', 650.00, 950.00),
    ('YES-010', 'Yeso Estuco Fino 25kg', 'SAC25', 20.00, 31.00),
    ('YES-011', 'Yeso para Tabiquería 30kg', 'SAC30', 25.00, 37.50),
    ('YES-012', 'Yeso Ignífugo 25kg', 'SAC25', 28.00, 42.00),
    ('YES-013', 'Yeso Acústico 25kg', 'SAC25', 29.00, 43.50),
    ('YES-014', 'Yeso de Alta Dureza 20kg', 'SAC20', 23.50, 35.00),
    ('YES-015', 'Yeso para Revestimiento 25kg', 'SAC25', 21.50, 32.50),
    ('YES-016', 'Yeso Nivelador de Pisos 25kg', 'SAC25', 27.00, 40.00),
    ('YES-017', 'Yeso para Restauración 10kg', 'SAC10', 16.00, 25.00),
    ('YES-018', 'Yeso con Fibra 25kg', 'SAC25', 24.50, 36.50),
    ('YES-019', 'Yeso Impermeabilizado 25kg', 'SAC25', 26.50, 39.50),
    ('YES-020', 'Yeso de Calcinación Controlada 40kg', 'SAC40', 25.50, 38.00),
    ('YES-021', 'Yeso para Artesanía 5kg', 'SAC5', 9.00, 15.00),
    ('YES-022', 'Yeso Médico 1kg', 'U', 5.00, 9.50),
    ('YES-023', 'Yeso de Fraguado Retardado 25kg', 'SAC25', 22.00, 33.00),
    ('YES-024', 'Yeso para Fundición 25kg', 'SAC25', 23.00, 34.50),
    ('YES-025', 'Yeso Ecológico 25kg', 'SAC25', 24.00, 36.00),
    # Placas
    ('PLA-001', 'Placa de Yeso Estándar', 'U', 28.00, 42.00),
    ('PLA-002', 'Placa Resistente a la Humedad', 'U', 35.00, 52.00),
    ('PLA-003', 'Placa Ignífuga Tipo X', 'U', 38.00, 56.00),
    ('PLA-004', 'Placa Flexible', 'U', 40.00, 59.00),
    ('PLA-005', 'Placa de Yeso 9.5mm', 'U', 26.00, 39.00),
    ('PLA-006', 'Placa de Yeso 15mm', 'U', 32.00, 48.00),
    ('PLA-007', 'Perfil Metálico Parante 0.6mm 3m', 'U', 12.00, 18.50),
    ('PLA-008', 'Perfil Metálico Canal 0.6mm 3m', 'U', 11.00, 17.00),
    ('PLA-009', 'Perfil Metálico Omega 0.6mm 3m', 'U', 13.00, 19.50),
    ('PLA-010', 'Perfil Metálico U 0.6mm 3m', 'U', 10.50, 16.00),
    ('PLA-011', 'Cinta de Papel Microperforada 75m', 'U', 6.00, 9.50),
    ('PLA-012', 'Cinta de Malla de Fibra de Vidrio 90m', 'U', 8.00, 12.50),
    ('PLA-013', 'Esquinero Metálico 2.4m', 'U', 7.50, 11.50),
    ('PLA-014', 'Esquinero de PVC 2.4m', 'U', 6.50, 10.00),
    ('PLA-015', 'Suspensor Ajustable 1.5mm', 'PAQ10', 15.00, 23.00),
    ('PLA-016', 'Conector de Perfiles', 'PAQ10', 18.00, 27.00),
    ('PLA-017', 'Placa de Yeso Acústica', 'U', 45.00, 67.00),
    ('PLA-018', 'Placa de Yeso con Aislante Térmico', 'U', 50.00, 75.00),
    ('PLA-019', 'Placa Cementicia 1.2x2.4m', 'U', 42.00, 63.00),
    ('PLA-020', 'Placa de Yeso Curvada', 'U', 48.00, 72.00),
    # Decorativos
    ('DEC-001', 'Cornisa Decorativa Clásica 2.4m', 'U', 12.00, 18.00),
    ('DEC-002', 'Cornisa Decorativa Moderna 2.4m', 'U', 14.00, 21.00),
    ('DEC-003', 'Moldura para Pared 2m', 'U', 8.00, 12.50),
    ('DEC-004', 'Rosetón para Centro de Luz 50cm', 'U', 15.00, 23.00),
    ('DEC-005', 'Rosetón para Centro de Luz 80cm', 'U', 22.00, 33.00),
    ('DEC-006', 'Columna Decorativa 2.5m', 'U', 85.00, 125.00),
    ('DEC-007', 'Capitel para Columna', 'U', 35.00, 52.00),
    ('DEC-008', 'Base para Columna', 'U', 30.00, 45.00),
    ('DEC-009', 'Panel 3D de Yeso 60x60cm', 'U', 18.00, 27.00),
    ('DEC-010', 'Panel 3D de Yeso 50x50cm', 'U', 15.00, 23.00),
    ('DEC-011', 'Zócalo de Yeso 2.4m', 'U', 9.00, 14.00),
    ('DEC-012', 'Guardapolvo de Yeso 2.4m', 'U', 7.00, 11.00),
    ('DEC-013', 'Dovelaje Decorativo 2m', 'U', 25.00, 38.00),
    ('DEC-014', 'Marco para Espejo de Yeso', 'U', 40.00, 60.00),
    ('DEC-015', 'Aplicación Floral de Yeso', 'U', 12.00, 18.50),
    ('DEC-016', 'Aplicación Geométrica de Yeso', 'U', 14.00, 21.00),
    ('DEC-017', 'Friso Decorativo 2.4m', 'U', 16.00, 24.00),
    ('DEC-018', 'Remate de Muro 2.4m', 'U', 11.00, 17.00),
    ('DEC-019', 'Nicho de Yeso para Pared', 'U', 45.00, 68.00),
    ('DEC-020', 'Cenefa Decorativa de Yeso 2m', 'U', 13.00, 20.00),
    # Masillas
    ('MAS-001', 'Masilla para Juntas 20kg', 'SAC20', 25.00, 38.00),
    ('MAS-002', 'Masilla para Juntas 5kg', 'U', 8.00, 12.50),
    ('MAS-003', 'Pegamento para Placas de Yeso 20kg', 'SAC20', 22.00, 33.00),
    ('MAS-004', 'Estuco Plástico 25kg', 'SAC25', 30.00, 45.00),
    ('MAS-005', 'Pasta Mural 25kg', 'SAC25', 28.00, 42.00),
    ('MAS-006', 'Pasta Mural 10kg', 'SAC10', 13.00, 20.00),
    ('MAS-007', 'Sellador Acrílico 1kg', 'U', 6.00, 9.50),
    ('MAS-008', 'Sellador de Poliuretano 300ml', 'U', 8.00, 12.50),
    ('MAS-009', 'Impermeabilizante para Yeso 5L', 'U', 35.00, 52.00),
    ('MAS-010', 'Aditivo Retardador de Fraguado 1L', 'U', 15.00, 23.00),
    ('MAS-011', 'Aditivo Acelerador de Fraguado 1L', 'U', 14.00, 21.50),
    ('MAS-012', 'Mezcla para Revestimiento Exterior 25kg', 'SAC25', 32.00, 48.00),
    ('MAS-013', 'Mortero de Reparación 20kg', 'SAC20', 26.00, 39.00),
    ('MAS-014', 'Pintura Selladora Blanca 5L', 'U', 40.00, 60.00),
    ('MAS-015', 'Enduido Corrido 25kg', 'SAC25', 24.00, 36.00),
    # Materias primas
    ('MAT-001', 'Piedra de Yeso Natural', 'TON', 120.00, 180.00),
    ('MAT-002', 'Piedra de Yeso Triturada', 'TON', 140.00, 210.00),
    ('MAT-003', 'Aditivo Industrial A-100', 'KG', 8.00, 12.50),
    ('MAT-004', 'Aditivo Industrial B-200', 'KG', 9.50, 14.50),
    ('MAT-005', 'Carbón Mineral para Horno', 'TON', 350.00, 520.00),
    ('MAT-006', 'Gas Natural Industrial', 'U', 450.00, 670.00),
    ('MAT-007', 'Bolsa de Polipropileno 25kg', 'PAQ10', 12.00, 18.00),
    ('MAT-008', 'Bolsa de Polipropileno 40kg', 'PAQ10', 15.00, 22.50),
    ('MAT-009', 'Fleje de Acero 500m', 'U', 45.00, 68.00),
    ('MAT-010', 'Fleje Plástico 500m', 'U', 25.00, 38.00),
    ('MAT-011', 'Hebillas para Fleje', 'PAQ10', 18.00, 27.00),
    ('MAT-012', 'Lubricante Industrial 20L', 'U', 120.00, 180.00),
    ('MAT-013', 'Grasa para Maquinaria 15kg', 'U', 85.00, 128.00),
    ('MAT-014', 'Repuesto Trituradora Tipo A', 'U', 250.00, 375.00),
    ('MAT-015', 'Repuesto Trituradora Tipo B', 'U', 180.00, 270.00),
    ('MAT-016', 'Filtro de Aire Industrial', 'U', 65.00, 98.00),
    ('MAT-017', 'Correa de Transmisión 1.5m', 'U', 40.00, 60.00),
    ('MAT-018', 'Rodamiento de Bola 6205', 'U', 15.00, 23.00),
    ('MAT-019', 'Pintura Industrial para Maquinaria 5L', 'U', 55.00, 82.00),
    ('MAT-020', 'Material de Empaque Stretch 20kg', 'U', 70.00, 105.00),
    # Herramientas
    ('HER-001', 'Llana de Acero Profesional', 'U', 15.00, 23.00),
    ('HER-002', 'Espátula de 10cm', 'U', 5.00, 8.00),
    ('HER-003', 'Espátula de 25cm', 'U', 9.00, 14.00),
    ('HER-004', 'Mezcladora de Paleta Eléctrica', 'U', 120.00, 180.00),
    ('HER-005', 'Cortadora de Placas de Yeso', 'U', 35.00, 52.00),
    ('HER-006', 'Cuchilla para Cortadora (paq. 10)', 'PAQ10', 8.00, 12.50),
    ('HER-007', 'Nivel de Burbuja 60cm', 'U', 25.00, 38.00),
    ('HER-008', 'Lija de Agua Grano 120 (paq. 10)', 'PAQ10', 12.00, 18.50),
    ('HER-009', 'Lija de Agua Grano 220 (paq. 10)', 'PAQ10', 14.00, 21.50),
    ('HER-010', 'Pistola para Sellador', 'U', 18.00, 27.00),
    ('HER-011', 'Balde de Plástico 20L', 'U', 10.00, 15.50),
    ('HER-012', 'Rodillo de Pintura 23cm', 'U', 12.00, 18.50),
    ('HER-013', 'Bandeja para Pintura', 'U', 8.00, 12.50),
    ('HER-014', 'Guantes de Trabajo (par)', 'U', 4.00, 6.50),
    ('HER-015', 'Mascarilla N95 (caja 20)', 'PAQ10', 25.00, 38.00),
    ('HER-016', 'Lentes de Seguridad', 'U', 15.00, 23.00),
    ('HER-017', 'Casco de Seguridad Blanco', 'U', 18.00, 27.00),
    ('HER-018', 'Taladro Percutor 1/2"', 'U', 150.00, 225.00),
    ('HER-019', 'Destornillador Phillips', 'U', 8.00, 12.50),
    ('HER-020', 'Cinta Métrica 5m', 'U', 12.00, 18.50),
]

# Productos heredados que se archivan (D11). No se borran.
LEGACY_ARCHIVE = ['JJ-PIEDRA', 'JJ-BOLSA', 'JJ-COMBUSTIBLE']

# Variantes explícitas (v2.1 sección 12). Por template: atributo y valores de la línea.
# Cada valor genera una variante; el template queda como contenedor.
VARIANT_LINES = [
    ('YES-001', 'Peso del saco', ['25 kg', '40 kg']),
    ('YES-002', 'Presentación', ['Saco', 'Granel']),
    ('YES-003', 'Peso del saco', ['25 kg']),
    ('YES-004', 'Peso del saco', ['25 kg', '40 kg']),
    ('YES-006', 'Peso del saco', ['20 kg', '25 kg']),
    ('YES-021', 'Peso del saco', ['5 kg']),
    ('MAS-001', 'Peso del saco', ['20 kg', '5 kg']),
    ('MAS-005', 'Peso del saco', ['25 kg', '10 kg']),
    ('PLA-001', 'Dimensión', ['9.5 mm', '12.5 mm', '15 mm']),
    ('PLA-002', 'Dimensión', ['12.5 mm', '15 mm']),
    ('PLA-003', 'Dimensión', ['12.5 mm', '15 mm']),
    ('DEC-004', 'Dimensión', ['50 cm', '80 cm']),
    ('DEC-009', 'Dimensión', ['60 x 60 cm', '50 x 50 cm']),
]

# variant_sku, template_sku, valor de atributo, precio de venta, costo
VARIANT_ITEMS = [
    ('YES-001-25', 'YES-001', '25 kg', 28.00, 18.50),
    ('YES-001-40', 'YES-001', '40 kg', 38.50, 25.00),
    ('YES-002-40', 'YES-002', 'Saco', 35.00, 24.00),
    ('YES-002-GR', 'YES-002', 'Granel', 850.00, 580.00),
    ('YES-003-25', 'YES-003', '25 kg', 32.00, 21.00),
    ('YES-004-25', 'YES-004', '25 kg', 34.00, 22.50),
    ('YES-004-40', 'YES-004', '40 kg', 48.00, 32.00),
    ('YES-006-20', 'YES-006', '20 kg', 29.50, 19.00),
    ('YES-006-25', 'YES-006', '25 kg', 35.00, 23.00),
    ('YES-021-05', 'YES-021', '5 kg', 15.00, 9.00),
    ('MAS-001-20', 'MAS-001', '20 kg', 38.00, 25.00),
    ('MAS-001-05', 'MAS-001', '5 kg', 12.50, 8.00),
    ('MAS-005-25', 'MAS-005', '25 kg', 42.00, 28.00),
    ('MAS-005-10', 'MAS-005', '10 kg', 20.00, 13.00),
    ('PLA-001-095', 'PLA-001', '9.5 mm', 39.00, 26.00),
    ('PLA-001-125', 'PLA-001', '12.5 mm', 42.00, 28.00),
    ('PLA-001-150', 'PLA-001', '15 mm', 48.00, 32.00),
    ('PLA-002-125', 'PLA-002', '12.5 mm', 52.00, 35.00),
    ('PLA-002-150', 'PLA-002', '15 mm', 58.00, 39.00),
    ('PLA-003-125', 'PLA-003', '12.5 mm', 56.00, 38.00),
    ('PLA-003-150', 'PLA-003', '15 mm', 62.00, 42.00),
    ('DEC-004-50', 'DEC-004', '50 cm', 23.00, 15.00),
    ('DEC-004-80', 'DEC-004', '80 cm', 33.00, 22.00),
    ('DEC-009-6060', 'DEC-009', '60 x 60 cm', 27.00, 18.00),
    ('DEC-009-5050', 'DEC-009', '50 x 50 cm', 23.00, 15.00),
]
