#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
VALUACIÓN ACTUARIAL - HOSPITAL SAN LUCAS
=============================================================================

DESCRIPCIÓN:
    Script completo para realizar una valuación actuarial de todos los 
    empleados del Hospital San Lucas. Procesa datos demográficos, proyecta
    salarios, aplica tasas demográficas, calcula beneficios futuros,
    trae valores a presente y modela la reserva actuarial.

ARCHIVOS DE ENTRADA:
    - Excel: /mnt/data/Hospital_San_Lucas.xlsx
      - Hoja "DATA": datos de empleados
      - Hoja "Demográficos": tablas qx por edad y sexo

ARCHIVOS DE SALIDA:
    - valuacion_resultados.xlsx: archivo con múltiples hojas de resultados

SUPUESTOS ACTUARIALES:
    - Incremento salarial anual: 3.5%
    - Incremento anual de pensiones: 2.5%
    - Tasa de descuento: 4.0%
    - Contribución del trabajador: 8%
    - Contribución del patrón: 8%
    - Edad de retiro: 65 años
    - Años mínimos de servicio: 15
    - Edad máxima de proyección: 120 (omega)

USO:
    python valuacion_actuarial.py

REQUERIMIENTOS:
    - pandas>=2.0.0
    - numpy>=1.24.0
    - openpyxl>=3.1.0

INSTALACIÓN:
    pip install -r requirements.txt

AUTOR:
    Sistema Actuarial Hospital San Lucas
    
FECHA:
    Noviembre 2025
=============================================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os
import sys

# Configuración de advertencias
warnings.filterwarnings('default')

# =============================================================================
# CONFIGURACIÓN DE PARÁMETROS ACTUARIALES
# =============================================================================

class ParametrosActuariales:
    """Clase que contiene todos los parámetros actuariales del plan."""
    
    # Tasas y porcentajes
    INCREMENTO_SALARIAL = 0.035  # 3.5% anual
    INCREMENTO_PENSION = 0.025   # 2.5% anual
    TASA_DESCUENTO = 0.04        # 4.0% anual
    
    # Contribuciones
    PCT_CONTRIBUCION_TRABAJADOR = 0.08  # 8%
    PCT_CONTRIBUCION_PATRON = 0.08      # 8%
    
    # Parámetros del plan
    EDAD_RETIRO = 65
    ANOS_MINIMOS_SERVICIO = 15
    EDAD_MAXIMA = 120  # Omega
    
    # Pensión
    TASA_REEMPLAZO = 0.60  # 60% del salario final
    
    # Prima de antigüedad
    MAX_QUINQUENIOS = 4
    
    @classmethod
    def factor_descuento(cls, n):
        """Calcula el factor de descuento v^n."""
        return (1 / (1 + cls.TASA_DESCUENTO)) ** n


# =============================================================================
# FUNCIONES DE CARGA Y VALIDACIÓN DE DATOS
# =============================================================================

def cargar_datos_empleados(ruta_archivo):
    """
    Carga los datos de empleados desde el archivo Excel.
    
    Args:
        ruta_archivo (str): Ruta al archivo Excel
        
    Returns:
        pd.DataFrame: DataFrame con los datos de empleados
    """
    print(f"Cargando datos de empleados desde: {ruta_archivo}")
    
    try:
        df = pd.read_excel(ruta_archivo, sheet_name='DATA')
        print(f"  ✓ Se cargaron {len(df)} empleados")
        
        # Validar columnas requeridas
        columnas_requeridas = [
            'ID', 'Fecha de nacimiento', 'Fecha de alta', 
            'Salario diario', 'Estatus empleado', 'Método de pago', 'Sexo'
        ]
        
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        if columnas_faltantes:
            warnings.warn(f"Columnas faltantes: {columnas_faltantes}")
        
        return df
        
    except FileNotFoundError:
        print(f"  ✗ ERROR: No se encontró el archivo {ruta_archivo}")
        print("  Creando datos de ejemplo para demostración...")
        return crear_datos_ejemplo()
    except Exception as e:
        print(f"  ✗ ERROR al cargar archivo: {e}")
        print("  Creando datos de ejemplo para demostración...")
        return crear_datos_ejemplo()


def cargar_datos_demograficos(ruta_archivo):
    """
    Carga las tablas demográficas (qx) desde el archivo Excel.
    
    Args:
        ruta_archivo (str): Ruta al archivo Excel
        
    Returns:
        pd.DataFrame: DataFrame con las tasas demográficas por edad
    """
    print(f"Cargando datos demográficos desde: {ruta_archivo}")
    
    try:
        df = pd.read_excel(ruta_archivo, sheet_name='Demográficos')
        print(f"  ✓ Se cargaron tasas para {len(df)} edades")
        
        # Validar columnas requeridas
        columnas_esperadas = [
            'Edad', 'Hombres qx', 'Mujeres qx', 
            'Renuncia Voluntaria', 'Invalidez', 'Jubilación'
        ]
        
        columnas_faltantes = [col for col in columnas_esperadas if col not in df.columns]
        if columnas_faltantes:
            warnings.warn(f"Columnas demográficas faltantes: {columnas_faltantes}")
        
        return df
        
    except Exception as e:
        print(f"  ✗ ERROR al cargar demográficos: {e}")
        print("  Creando tabla demográfica de ejemplo...")
        return crear_tabla_demografica_ejemplo()


def crear_datos_ejemplo():
    """
    Crea un conjunto de datos de ejemplo para demostración.
    
    Returns:
        pd.DataFrame: DataFrame con datos de empleados de ejemplo
    """
    np.random.seed(42)
    n_empleados = 50
    
    # Generar fechas de nacimiento (edades entre 25 y 65)
    hoy = datetime.now()
    fechas_nacimiento = [
        hoy.replace(year=hoy.year - edad) 
        for edad in np.random.randint(25, 66, n_empleados)
    ]
    
    # Generar fechas de alta (antigüedad entre 1 y 30 años)
    fechas_alta = [
        hoy.replace(year=hoy.year - antiguedad)
        for antiguedad in np.random.randint(1, 31, n_empleados)
    ]
    
    # Generar salarios (entre 500 y 2000 por día)
    salarios = np.random.uniform(500, 2000, n_empleados)
    
    df = pd.DataFrame({
        'ID': range(1, n_empleados + 1),
        'Fecha de nacimiento': fechas_nacimiento,
        'Fecha de alta': fechas_alta,
        'Salario diario': salarios,
        'Estatus empleado': np.random.choice(['ACTIVO', 'PENSIONADO'], n_empleados, p=[0.9, 0.1]),
        'Método de pago': np.random.choice(['NOMINA', 'HONORARIOS'], n_empleados, p=[0.85, 0.15]),
        'Sexo': np.random.choice(['M', 'F'], n_empleados)
    })
    
    return df


def crear_tabla_demografica_ejemplo():
    """
    Crea una tabla demográfica de ejemplo basada en tablas de mortalidad estándar.
    
    Returns:
        pd.DataFrame: DataFrame con tasas demográficas por edad
    """
    edades = np.arange(0, 121)
    
    # Tasas de mortalidad simplificadas (más altas a mayor edad)
    qx_hombres = np.minimum(0.001 + 0.00005 * edades + 0.0001 * edades**1.5 / 100, 1.0)
    qx_mujeres = qx_hombres * 0.7  # Mujeres tienen menor mortalidad
    
    # Tasas de renuncia (más altas en edades jóvenes, decrecen con la edad)
    qx_renuncia = np.maximum(0.15 - 0.002 * edades, 0.01)
    qx_renuncia[edades > 60] = 0.005  # Muy baja cerca del retiro
    
    # Tasas de invalidez (aumentan con la edad)
    qx_invalidez = np.minimum(0.001 + 0.0001 * edades, 0.05)
    
    # Tasa de jubilación (alta solo cerca de edad de retiro)
    qx_jubilacion = np.zeros_like(edades, dtype=float)
    qx_jubilacion[edades == 65] = 0.8
    qx_jubilacion[edades == 64] = 0.1
    qx_jubilacion[edades == 66] = 0.1
    
    df = pd.DataFrame({
        'Edad': edades,
        'Hombres qx': qx_hombres,
        'Mujeres qx': qx_mujeres,
        'Renuncia Voluntaria': qx_renuncia,
        'Invalidez': qx_invalidez,
        'Jubilación': qx_jubilacion
    })
    
    return df


def validar_y_limpiar_datos(df_empleados):
    """
    Valida y limpia los datos de empleados.
    
    Args:
        df_empleados (pd.DataFrame): DataFrame con datos de empleados
        
    Returns:
        pd.DataFrame: DataFrame limpio y validado
    """
    print("\nValidando y limpiando datos...")
    
    df = df_empleados.copy()
    
    # Convertir fechas
    if not pd.api.types.is_datetime64_any_dtype(df['Fecha de nacimiento']):
        df['Fecha de nacimiento'] = pd.to_datetime(df['Fecha de nacimiento'], errors='coerce')
    
    if not pd.api.types.is_datetime64_any_dtype(df['Fecha de alta']):
        df['Fecha de alta'] = pd.to_datetime(df['Fecha de alta'], errors='coerce')
    
    # Validar datos faltantes
    if df['Fecha de nacimiento'].isna().any():
        n_faltantes = df['Fecha de nacimiento'].isna().sum()
        warnings.warn(f"  ⚠ {n_faltantes} empleados sin fecha de nacimiento")
    
    if df['Fecha de alta'].isna().any():
        n_faltantes = df['Fecha de alta'].isna().sum()
        warnings.warn(f"  ⚠ {n_faltantes} empleados sin fecha de alta")
    
    # Calcular edad y antigüedad
    hoy = pd.Timestamp.now()
    df['Edad'] = ((hoy - df['Fecha de nacimiento']).dt.days / 365.25).astype(int)
    df['Anos_Servicio'] = ((hoy - df['Fecha de alta']).dt.days / 365.25)
    
    # Validar salarios
    if df['Salario diario'].isna().any():
        n_faltantes = df['Salario diario'].isna().sum()
        warnings.warn(f"  ⚠ {n_faltantes} empleados sin salario")
        df['Salario diario'].fillna(0, inplace=True)
    
    # Estandarizar sexo
    df['Sexo'] = df['Sexo'].str.upper().str.strip()
    df['Sexo'] = df['Sexo'].replace({'HOMBRE': 'M', 'MUJER': 'F', 'H': 'M'})
    
    # Calcular salario mensual según estatus
    df['Salario_Mensual'] = np.where(
        df['Estatus empleado'].str.upper().str.contains('ACTIVO', na=False),
        df['Salario diario'] * 30,
        df['Salario diario']  # Ya es pensión mensual
    )
    
    print(f"  ✓ Datos validados: {len(df)} empleados")
    print(f"  ✓ Rango de edades: {df['Edad'].min()} - {df['Edad'].max()}")
    print(f"  ✓ Rango de antigüedad: {df['Anos_Servicio'].min():.1f} - {df['Anos_Servicio'].max():.1f} años")
    
    return df


# =============================================================================
# FUNCIONES DE MODELADO DEMOGRÁFICO
# =============================================================================

def obtener_qx_demografico(edad, sexo, df_demograficos):
    """
    Obtiene las tasas demográficas (qx) para una edad y sexo específicos.
    
    Args:
        edad (int): Edad del empleado
        sexo (str): Sexo del empleado ('M' o 'F')
        df_demograficos (pd.DataFrame): Tabla demográfica
        
    Returns:
        dict: Diccionario con qx_muerte, qx_renuncia, qx_invalidez
    """
    # Asegurar que la edad esté dentro del rango
    edad = min(max(int(edad), 0), ParametrosActuariales.EDAD_MAXIMA)
    
    # Buscar en la tabla
    fila = df_demograficos[df_demograficos['Edad'] == edad]
    
    if fila.empty:
        # Si no existe, usar valores por defecto conservadores
        return {
            'qx_muerte': 0.01,
            'qx_renuncia': 0.05,
            'qx_invalidez': 0.01
        }
    
    fila = fila.iloc[0]
    
    # Obtener qx de mortalidad según sexo
    if sexo == 'M':
        qx_muerte = fila.get('Hombres qx', 0.01)
    else:
        qx_muerte = fila.get('Mujeres qx', 0.01)
    
    # Obtener otras tasas
    qx_renuncia = fila.get('Renuncia Voluntaria', 0.05)
    qx_invalidez = fila.get('Invalidez', 0.01)
    
    return {
        'qx_muerte': qx_muerte,
        'qx_renuncia': qx_renuncia,
        'qx_invalidez': qx_invalidez
    }


def calcular_probabilidad_activo(edad_inicio, anos_proyeccion, sexo, df_demograficos):
    """
    Calcula la probabilidad de que un empleado siga activo después de n años.
    
    Args:
        edad_inicio (int): Edad actual del empleado
        anos_proyeccion (int): Años a proyectar
        sexo (str): Sexo del empleado
        df_demograficos (pd.DataFrame): Tabla demográfica
        
    Returns:
        np.array: Vector de probabilidades de estar activo en cada año
    """
    probabilidades = np.ones(anos_proyeccion + 1)
    
    for t in range(1, anos_proyeccion + 1):
        edad = edad_inicio + t - 1
        
        # Obtener tasas demográficas
        qx = obtener_qx_demografico(edad, sexo, df_demograficos)
        
        # Probabilidad de decrementos múltiples
        q_total = qx['qx_muerte'] + qx['qx_renuncia'] + qx['qx_invalidez']
        q_total = min(q_total, 1.0)  # No puede exceder 1
        
        # Probabilidad de sobrevivir = productoria de (1 - q_total)
        probabilidades[t] = probabilidades[t-1] * (1 - q_total)
    
    return probabilidades


def calcular_probabilidad_supervivencia_post_retiro(edad_retiro, anos_proyeccion, sexo, df_demograficos):
    """
    Calcula la probabilidad de supervivencia después del retiro.
    Solo considera mortalidad (no renuncia ni invalidez).
    
    Args:
        edad_retiro (int): Edad al momento del retiro
        anos_proyeccion (int): Años post-retiro a proyectar
        sexo (str): Sexo del empleado
        df_demograficos (pd.DataFrame): Tabla demográfica
        
    Returns:
        np.array: Vector de probabilidades de supervivencia
    """
    probabilidades = np.ones(anos_proyeccion + 1)
    
    for t in range(1, anos_proyeccion + 1):
        edad = edad_retiro + t - 1
        
        if edad >= ParametrosActuariales.EDAD_MAXIMA:
            probabilidades[t] = 0
        else:
            # Solo mortalidad
            qx = obtener_qx_demografico(edad, sexo, df_demograficos)
            probabilidades[t] = probabilidades[t-1] * (1 - qx['qx_muerte'])
    
    return probabilidades


# =============================================================================
# FUNCIONES DE PROYECCIÓN SALARIAL
# =============================================================================

def proyectar_salarios(salario_mensual_inicial, anos_proyeccion):
    """
    Proyecta el salario mensual con incremento anual.
    
    Args:
        salario_mensual_inicial (float): Salario mensual al inicio
        anos_proyeccion (int): Años a proyectar
        
    Returns:
        np.array: Vector de salarios proyectados
    """
    t = np.arange(anos_proyeccion + 1)
    salarios = salario_mensual_inicial * (1 + ParametrosActuariales.INCREMENTO_SALARIAL) ** t
    return salarios


def calcular_salario_anual(salarios_mensuales):
    """
    Convierte salarios mensuales a anuales.
    
    Args:
        salarios_mensuales (np.array): Vector de salarios mensuales
        
    Returns:
        np.array: Vector de salarios anuales
    """
    return salarios_mensuales * 12


# =============================================================================
# FUNCIONES DE CÁLCULO DE CONTRIBUCIONES
# =============================================================================

def calcular_contribuciones(salarios_anuales, prob_activo, pct_trabajador, pct_patron):
    """
    Calcula las contribuciones de trabajador y patrón.
    
    Args:
        salarios_anuales (np.array): Salarios anuales proyectados
        prob_activo (np.array): Probabilidades de estar activo
        pct_trabajador (float): Porcentaje de contribución del trabajador
        pct_patron (float): Porcentaje de contribución del patrón
        
    Returns:
        tuple: (contribuciones_trabajador, contribuciones_patron, pv_trabajador, pv_patron)
    """
    # Contribuciones brutas
    contrib_trabajador = salarios_anuales * pct_trabajador * prob_activo
    contrib_patron = salarios_anuales * pct_patron * prob_activo
    
    # Valor presente
    anos = len(salarios_anuales)
    factores = np.array([ParametrosActuariales.factor_descuento(t) for t in range(anos)])
    
    pv_trabajador = np.sum(contrib_trabajador * factores)
    pv_patron = np.sum(contrib_patron * factores)
    
    return contrib_trabajador, contrib_patron, pv_trabajador, pv_patron


# =============================================================================
# FUNCIONES DE PRIMAS DE ANTIGÜEDAD
# =============================================================================

def calcular_primas_antiguedad(salarios_mensuales, anos_servicio_inicial, prob_activo):
    """
    Calcula las primas de antigüedad por quinquenios.
    
    Args:
        salarios_mensuales (np.array): Salarios mensuales proyectados
        anos_servicio_inicial (float): Años de servicio al inicio
        prob_activo (np.array): Probabilidades de estar activo
        
    Returns:
        tuple: (primas_anuales, pv_primas)
    """
    anos = len(salarios_mensuales)
    primas = np.zeros(anos)
    
    for t in range(anos):
        # Años de servicio en el año t
        anos_servicio = anos_servicio_inicial + t
        
        # Número de quinquenios (máximo 4)
        n_quinquenios = min(1 + int(anos_servicio // 5), ParametrosActuariales.MAX_QUINQUENIOS)
        
        # Prima anual = n_quinquenios * salario mensual
        primas[t] = n_quinquenios * salarios_mensuales[t] * prob_activo[t]
    
    # Valor presente
    factores = np.array([ParametrosActuariales.factor_descuento(t) for t in range(anos)])
    pv_primas = np.sum(primas * factores)
    
    return primas, pv_primas


# =============================================================================
# FUNCIONES DE ELEGIBILIDAD Y PENSIONES
# =============================================================================

def es_elegible_pension(edad, anos_servicio):
    """
    Determina si un empleado es elegible para pensión.
    
    Args:
        edad (int): Edad del empleado
        anos_servicio (float): Años de servicio
        
    Returns:
        bool: True si es elegible
    """
    return (edad >= ParametrosActuariales.EDAD_RETIRO and 
            anos_servicio >= ParametrosActuariales.ANOS_MINIMOS_SERVICIO)


def calcular_pension(edad_actual, anos_servicio_actual, salario_mensual_actual, 
                     sexo, df_demograficos):
    """
    Calcula la pensión proyectada y su valor presente.
    
    Args:
        edad_actual (int): Edad actual del empleado
        anos_servicio_actual (float): Años de servicio actuales
        salario_mensual_actual (float): Salario mensual actual
        sexo (str): Sexo del empleado
        df_demograficos (pd.DataFrame): Tabla demográfica
        
    Returns:
        dict: Diccionario con años_hasta_retiro, pension_inicial, 
              pensiones_proyectadas, pv_pension, elegible
    """
    # Verificar elegibilidad al retiro
    anos_hasta_retiro = max(ParametrosActuariales.EDAD_RETIRO - edad_actual, 0)
    anos_servicio_al_retiro = anos_servicio_actual + anos_hasta_retiro
    
    elegible = es_elegible_pension(ParametrosActuariales.EDAD_RETIRO, anos_servicio_al_retiro)
    
    if not elegible:
        return {
            'anos_hasta_retiro': anos_hasta_retiro,
            'pension_inicial': 0,
            'pensiones_proyectadas': np.zeros(1),
            'pv_pension': 0,
            'elegible': False
        }
    
    # Proyectar salario hasta el retiro
    salario_al_retiro = salario_mensual_actual * (
        (1 + ParametrosActuariales.INCREMENTO_SALARIAL) ** anos_hasta_retiro
    )
    
    # Pensión inicial = 60% del salario final
    pension_inicial_mensual = salario_al_retiro * ParametrosActuariales.TASA_REEMPLAZO
    pension_inicial_anual = pension_inicial_mensual * 12
    
    # Proyectar pensión post-retiro
    anos_post_retiro = ParametrosActuariales.EDAD_MAXIMA - ParametrosActuariales.EDAD_RETIRO
    t_pension = np.arange(anos_post_retiro + 1)
    
    # Pensión escalada
    pensiones = pension_inicial_anual * (1 + ParametrosActuariales.INCREMENTO_PENSION) ** t_pension
    
    # Probabilidad de supervivencia post-retiro
    prob_supervivencia = calcular_probabilidad_supervivencia_post_retiro(
        ParametrosActuariales.EDAD_RETIRO, anos_post_retiro, sexo, df_demograficos
    )
    
    # Ajustar pensiones por probabilidad de supervivencia
    pensiones_esperadas = pensiones * prob_supervivencia
    
    # Valor presente
    # Factor de descuento = v^(años_hasta_retiro) * v^(t_post_retiro)
    factores = np.array([
        ParametrosActuariales.factor_descuento(anos_hasta_retiro + t) 
        for t in range(len(pensiones_esperadas))
    ])
    
    pv_pension = np.sum(pensiones_esperadas * factores)
    
    return {
        'anos_hasta_retiro': anos_hasta_retiro,
        'pension_inicial': pension_inicial_anual,
        'pensiones_proyectadas': pensiones_esperadas,
        'pv_pension': pv_pension,
        'elegible': True
    }


# =============================================================================
# FUNCIÓN PRINCIPAL DE VALUACIÓN POR EMPLEADO
# =============================================================================

def valuar_empleado(empleado, df_demograficos, pct_patron=None):
    """
    Realiza la valuación completa de un empleado.
    
    Args:
        empleado (pd.Series): Datos del empleado
        df_demograficos (pd.DataFrame): Tabla demográfica
        pct_patron (float, optional): Porcentaje de contribución patronal alternativo
        
    Returns:
        dict: Diccionario con todos los resultados de la valuación
    """
    # Parámetros del empleado
    edad = empleado['Edad']
    anos_servicio = empleado['Anos_Servicio']
    salario_mensual = empleado['Salario_Mensual']
    sexo = empleado['Sexo']
    
    # Años a proyectar hasta edad máxima
    anos_proyeccion = ParametrosActuariales.EDAD_MAXIMA - edad
    anos_proyeccion = max(anos_proyeccion, 0)
    
    # 1. Proyección salarial
    salarios_mensuales = proyectar_salarios(salario_mensual, anos_proyeccion)
    salarios_anuales = calcular_salario_anual(salarios_mensuales)
    
    # 2. Probabilidad de estar activo
    prob_activo = calcular_probabilidad_activo(edad, anos_proyeccion, sexo, df_demograficos)
    
    # 3. Contribuciones
    pct_patron_actual = pct_patron if pct_patron is not None else ParametrosActuariales.PCT_CONTRIBUCION_PATRON
    
    contrib_trab, contrib_patron, pv_contrib_trab, pv_contrib_patron = calcular_contribuciones(
        salarios_anuales, prob_activo,
        ParametrosActuariales.PCT_CONTRIBUCION_TRABAJADOR,
        pct_patron_actual
    )
    
    pv_contribuciones_total = pv_contrib_trab + pv_contrib_patron
    
    # 4. Primas de antigüedad
    primas, pv_primas = calcular_primas_antiguedad(salarios_mensuales, anos_servicio, prob_activo)
    
    # 5. Pensión
    resultado_pension = calcular_pension(edad, anos_servicio, salario_mensual, sexo, df_demograficos)
    pv_pension = resultado_pension['pv_pension']
    elegible_pension = resultado_pension['elegible']
    
    # 6. Valor presente de salarios
    factores = np.array([ParametrosActuariales.factor_descuento(t) for t in range(len(salarios_anuales))])
    salarios_pv = salarios_anuales * prob_activo * factores
    pv_salarios = np.sum(salarios_pv)
    
    # 7. Outflows totales
    pv_outflows = pv_pension + pv_primas
    
    # 8. Reserva individual
    reserva = pv_outflows - pv_contribuciones_total
    
    return {
        'ID': empleado['ID'],
        'Edad': edad,
        'Anos_Servicio': anos_servicio,
        'Salario_Mensual': salario_mensual,
        'Sexo': sexo,
        'Elegible_Pension': elegible_pension,
        'Anos_Hasta_Retiro': resultado_pension['anos_hasta_retiro'],
        'Pension_Inicial': resultado_pension['pension_inicial'],
        
        # Proyecciones
        'Salarios_Mensuales_Proy': salarios_mensuales,
        'Salarios_Anuales_Proy': salarios_anuales,
        'Salarios_PV': salarios_pv,
        'Prob_Activo': prob_activo,
        'Contrib_Trabajador': contrib_trab,
        'Contrib_Patron': contrib_patron,
        'Primas': primas,
        'Pensiones_Proy': resultado_pension['pensiones_proyectadas'],
        
        # Valores presentes
        'PV_Salarios': pv_salarios,
        'PV_Pensiones': pv_pension,
        'PV_Primas': pv_primas,
        'PV_Contrib_Trabajador': pv_contrib_trab,
        'PV_Contrib_Patron': pv_contrib_patron,
        'PV_Contribuciones_Total': pv_contribuciones_total,
        'PV_Outflows': pv_outflows,
        'Reserva': reserva
    }


# =============================================================================
# FUNCIÓN PRINCIPAL DE VALUACIÓN MASIVA
# =============================================================================

def valuar_poblacion(df_empleados, df_demograficos):
    """
    Realiza la valuación de toda la población de empleados.
    
    Args:
        df_empleados (pd.DataFrame): DataFrame con empleados
        df_demograficos (pd.DataFrame): Tabla demográfica
        
    Returns:
        list: Lista de diccionarios con resultados por empleado
    """
    print("\n" + "="*70)
    print("INICIANDO VALUACIÓN ACTUARIAL")
    print("="*70)
    
    resultados = []
    total = len(df_empleados)
    
    for idx, empleado in df_empleados.iterrows():
        if (idx + 1) % 50 == 0 or idx == 0:
            print(f"  Procesando empleado {idx + 1}/{total}...")
        
        resultado = valuar_empleado(empleado, df_demograficos)
        resultados.append(resultado)
    
    print(f"  ✓ Valuación completada para {total} empleados")
    
    return resultados


# =============================================================================
# FUNCIONES DE GENERACIÓN DE REPORTES
# =============================================================================

def generar_hoja_detallado(resultados):
    """
    Genera la hoja 'Detallado_por_empleado'.
    
    Args:
        resultados (list): Lista de resultados de valuación
        
    Returns:
        pd.DataFrame: DataFrame con resumen por empleado
    """
    datos = []
    
    for r in resultados:
        datos.append({
            'ID': r['ID'],
            'Edad': r['Edad'],
            'Anos_Servicio': round(r['Anos_Servicio'], 2),
            'Salario_Mensual': round(r['Salario_Mensual'], 2),
            'Sexo': r['Sexo'],
            'PV_Pensiones': round(r['PV_Pensiones'], 2),
            'PV_Primas': round(r['PV_Primas'], 2),
            'PV_Contrib_Trabajador': round(r['PV_Contrib_Trabajador'], 2),
            'PV_Contrib_Patron': round(r['PV_Contrib_Patron'], 2),
            'PV_Total_Contribuciones': round(r['PV_Contribuciones_Total'], 2),
            'PV_Outflows': round(r['PV_Outflows'], 2),
            'Reserva_Individual': round(r['Reserva'], 2),
            'Elegible_Pension': 'Sí' if r['Elegible_Pension'] else 'No'
        })
    
    return pd.DataFrame(datos)


def generar_matriz_proyeccion(resultados, campo, max_anos=None):
    """
    Genera una matriz de proyección (empleados x años).
    
    Args:
        resultados (list): Lista de resultados
        campo (str): Campo a proyectar
        max_anos (int, optional): Máximo de años a incluir
        
    Returns:
        pd.DataFrame: Matriz de proyección
    """
    # Determinar número máximo de años
    if max_anos is None:
        max_anos = max(len(r[campo]) for r in resultados)
    
    # Crear matriz
    datos = []
    for r in resultados:
        valores = r[campo]
        if len(valores) < max_anos:
            # Rellenar con ceros
            valores = np.pad(valores, (0, max_anos - len(valores)), constant_values=0)
        else:
            valores = valores[:max_anos]
        
        fila = {'ID': r['ID']}
        for t in range(max_anos):
            fila[f'Ano_{t}'] = round(valores[t], 2)
        
        datos.append(fila)
    
    return pd.DataFrame(datos)


def generar_hoja_jubilados(resultados):
    """
    Genera la hoja 'Jubilados' con empleados elegibles.
    
    Args:
        resultados (list): Lista de resultados
        
    Returns:
        pd.DataFrame: DataFrame de jubilados
    """
    datos = []
    
    for r in resultados:
        if r['Elegible_Pension']:
            datos.append({
                'ID': r['ID'],
                'Edad': r['Edad'],
                'Anos_Servicio': round(r['Anos_Servicio'], 2),
                'Anos_Hasta_Retiro': r['Anos_Hasta_Retiro'],
                'Salario_Mensual_Actual': round(r['Salario_Mensual'], 2),
                'Pension_Inicial_Anual': round(r['Pension_Inicial'], 2),
                'PV_Pension': round(r['PV_Pensiones'], 2)
            })
    
    if not datos:
        # Si no hay jubilados, crear DataFrame vacío con columnas
        return pd.DataFrame(columns=[
            'ID', 'Edad', 'Anos_Servicio', 'Anos_Hasta_Retiro',
            'Salario_Mensual_Actual', 'Pension_Inicial_Anual', 'PV_Pension'
        ])
    
    return pd.DataFrame(datos)


def generar_hoja_reserva(resultados):
    """
    Genera la hoja 'Reserva' con reservas individuales.
    
    Args:
        resultados (list): Lista de resultados
        
    Returns:
        pd.DataFrame: DataFrame de reservas
    """
    datos = []
    
    for r in resultados:
        datos.append({
            'ID': r['ID'],
            'Reserva_Individual': round(r['Reserva'], 2),
            'PV_Outflows': round(r['PV_Outflows'], 2),
            'PV_Inflows': round(r['PV_Contribuciones_Total'], 2),
            'Elegible_Pension': 'Sí' if r['Elegible_Pension'] else 'No'
        })
    
    df = pd.DataFrame(datos)
    
    # Agregar fila de totales
    total_fila = {
        'ID': 'TOTAL',
        'Reserva_Individual': df['Reserva_Individual'].sum(),
        'PV_Outflows': df['PV_Outflows'].sum(),
        'PV_Inflows': df['PV_Inflows'].sum(),
        'Elegible_Pension': ''
    }
    
    df = pd.concat([df, pd.DataFrame([total_fila])], ignore_index=True)
    
    return df


def generar_hoja_escenarios(df_empleados, df_demograficos, resultados_base):
    """
    Genera la hoja 'Escenarios' con diferentes tasas de aporte patronal.
    
    Args:
        df_empleados (pd.DataFrame): Empleados
        df_demograficos (pd.DataFrame): Tabla demográfica
        resultados_base (list): Resultados con 8% patronal
        
    Returns:
        pd.DataFrame: DataFrame de escenarios
    """
    print("\nGenerando escenarios alternativos...")
    
    escenarios = [
        ('Aporte_Patron_8%', 0.08),
        ('Aporte_Patron_10%', 0.10),
        ('Aporte_Patron_12%', 0.12)
    ]
    
    datos = []
    
    for nombre, pct_patron in escenarios:
        print(f"  Calculando escenario: {nombre}...")
        
        if pct_patron == 0.08:
            # Usar resultados base
            reserva_total = sum(r['Reserva'] for r in resultados_base)
            pv_outflows = sum(r['PV_Outflows'] for r in resultados_base)
            pv_inflows = sum(r['PV_Contribuciones_Total'] for r in resultados_base)
        else:
            # Recalcular con nueva tasa
            reserva_total = 0
            pv_outflows = 0
            pv_inflows = 0
            
            for _, empleado in df_empleados.iterrows():
                resultado = valuar_empleado(empleado, df_demograficos, pct_patron=pct_patron)
                reserva_total += resultado['Reserva']
                pv_outflows += resultado['PV_Outflows']
                pv_inflows += resultado['PV_Contribuciones_Total']
        
        datos.append({
            'Escenario': nombre,
            'Porcentaje_Patron': f"{pct_patron*100:.1f}%",
            'PV_Outflows': round(pv_outflows, 2),
            'PV_Inflows': round(pv_inflows, 2),
            'Reserva_Total': round(reserva_total, 2)
        })
    
    return pd.DataFrame(datos)


def generar_hoja_resumen(resultados):
    """
    Genera la hoja 'Resumen' con métricas clave del plan.
    
    Args:
        resultados (list): Lista de resultados
        
    Returns:
        pd.DataFrame: DataFrame de resumen
    """
    df_detalle = generar_hoja_detallado(resultados)
    
    n_empleados = len(resultados)
    n_elegibles = sum(1 for r in resultados if r['Elegible_Pension'])
    
    datos = [
        {'Metrica': 'Número de Empleados', 'Valor': n_empleados},
        {'Metrica': 'Empleados Elegibles a Pensión', 'Valor': n_elegibles},
        {'Metrica': 'Porcentaje Elegible', 'Valor': f"{(n_elegibles/n_empleados*100):.2f}%"},
        {'Metrica': '', 'Valor': ''},
        {'Metrica': 'Edad Promedio', 'Valor': f"{df_detalle['Edad'].mean():.2f}"},
        {'Metrica': 'Antigüedad Promedio (años)', 'Valor': f"{df_detalle['Anos_Servicio'].mean():.2f}"},
        {'Metrica': 'Salario Mensual Promedio', 'Valor': f"${df_detalle['Salario_Mensual'].mean():,.2f}"},
        {'Metrica': '', 'Valor': ''},
        {'Metrica': 'PV Total Pensiones', 'Valor': f"${df_detalle['PV_Pensiones'].sum():,.2f}"},
        {'Metrica': 'PV Total Primas', 'Valor': f"${df_detalle['PV_Primas'].sum():,.2f}"},
        {'Metrica': 'PV Total Contribuciones Trabajador', 'Valor': f"${df_detalle['PV_Contrib_Trabajador'].sum():,.2f}"},
        {'Metrica': 'PV Total Contribuciones Patrón', 'Valor': f"${df_detalle['PV_Contrib_Patron'].sum():,.2f}"},
        {'Metrica': 'PV Total Contribuciones', 'Valor': f"${df_detalle['PV_Total_Contribuciones'].sum():,.2f}"},
        {'Metrica': '', 'Valor': ''},
        {'Metrica': 'PV Total Outflows', 'Valor': f"${df_detalle['PV_Outflows'].sum():,.2f}"},
        {'Metrica': 'Reserva Total del Plan', 'Valor': f"${df_detalle['Reserva_Individual'].sum():,.2f}"},
        {'Metrica': '', 'Valor': ''},
        {'Metrica': 'Reserva Promedio por Empleado', 'Valor': f"${df_detalle['Reserva_Individual'].mean():,.2f}"},
        {'Metrica': 'Reserva Promedio (Elegibles)', 'Valor': f"${df_detalle[df_detalle['Elegible_Pension']=='Sí']['Reserva_Individual'].mean():,.2f}"},
    ]
    
    return pd.DataFrame(datos)


# =============================================================================
# FUNCIÓN DE EXPORTACIÓN A EXCEL
# =============================================================================

def exportar_resultados(resultados, df_empleados, df_demograficos, archivo_salida='valuacion_resultados.xlsx'):
    """
    Exporta todos los resultados a un archivo Excel con múltiples hojas.
    
    Args:
        resultados (list): Lista de resultados de valuación
        df_empleados (pd.DataFrame): DataFrame de empleados
        df_demograficos (pd.DataFrame): Tabla demográfica
        archivo_salida (str): Nombre del archivo de salida
    """
    print("\n" + "="*70)
    print("GENERANDO ARCHIVO DE RESULTADOS")
    print("="*70)
    
    with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
        
        # 1. Detallado por empleado
        print("  Generando hoja: Detallado_por_empleado...")
        df_detalle = generar_hoja_detallado(resultados)
        df_detalle.to_excel(writer, sheet_name='Detallado_por_empleado', index=False)
        
        # 2. Salarios Proyectados
        print("  Generando hoja: Salarios_Proyectados...")
        df_sal_proy = generar_matriz_proyeccion(resultados, 'Salarios_Mensuales_Proy', max_anos=50)
        df_sal_proy.to_excel(writer, sheet_name='Salarios_Proyectados', index=False)
        
        # 3. Salarios PV
        print("  Generando hoja: Salarios_PV...")
        df_sal_pv = generar_matriz_proyeccion(resultados, 'Salarios_PV', max_anos=50)
        df_sal_pv.to_excel(writer, sheet_name='Salarios_PV', index=False)
        
        # 4. Primas
        print("  Generando hoja: Primas...")
        df_primas = generar_matriz_proyeccion(resultados, 'Primas', max_anos=50)
        df_primas.to_excel(writer, sheet_name='Primas', index=False)
        
        # 5. Aportaciones
        print("  Generando hoja: Aportaciones...")
        df_aport_trab = generar_matriz_proyeccion(resultados, 'Contrib_Trabajador', max_anos=50)
        df_aport_patron = generar_matriz_proyeccion(resultados, 'Contrib_Patron', max_anos=50)
        
        # Combinar trabajador y patrón
        df_aportaciones = df_detalle[['ID', 'PV_Contrib_Trabajador', 'PV_Contrib_Patron', 'PV_Total_Contribuciones']].copy()
        df_aportaciones.to_excel(writer, sheet_name='Aportaciones', index=False)
        
        # 6. Jubilados
        print("  Generando hoja: Jubilados...")
        df_jubilados = generar_hoja_jubilados(resultados)
        df_jubilados.to_excel(writer, sheet_name='Jubilados', index=False)
        
        # 7. PV_Jubilados
        print("  Generando hoja: PV_Jubilados...")
        resultados_elegibles = [r for r in resultados if r['Elegible_Pension']]
        if resultados_elegibles:
            df_pv_jubilados = generar_matriz_proyeccion(resultados_elegibles, 'Pensiones_Proy', max_anos=50)
        else:
            df_pv_jubilados = pd.DataFrame({'ID': [], 'Nota': ['No hay empleados elegibles']})
        df_pv_jubilados.to_excel(writer, sheet_name='PV_Jubilados', index=False)
        
        # 8. Reserva
        print("  Generando hoja: Reserva...")
        df_reserva = generar_hoja_reserva(resultados)
        df_reserva.to_excel(writer, sheet_name='Reserva', index=False)
        
        # 9. Escenarios
        print("  Generando hoja: Escenarios...")
        df_escenarios = generar_hoja_escenarios(df_empleados, df_demograficos, resultados)
        df_escenarios.to_excel(writer, sheet_name='Escenarios', index=False)
        
        # 10. Resumen
        print("  Generando hoja: Resumen...")
        df_resumen = generar_hoja_resumen(resultados)
        df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
        
        # 11-12. Hojas transpuestas
        print("  Generando hojas transpuestas...")
        df_sal_proy_t = df_sal_proy.set_index('ID').T
        df_sal_proy_t.to_excel(writer, sheet_name='Transpuestos_Salarios_Proy')
        
        df_sal_pv_t = df_sal_pv.set_index('ID').T
        df_sal_pv_t.to_excel(writer, sheet_name='Transpuestos_Salarios_PV')
    
    print(f"\n  ✓ Archivo generado exitosamente: {archivo_salida}")
    print("="*70)


# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

def main():
    """
    Función principal que ejecuta toda la valuación actuarial.
    """
    print("\n")
    print("="*70)
    print("SISTEMA DE VALUACIÓN ACTUARIAL")
    print("HOSPITAL SAN LUCAS")
    print("="*70)
    print("\nVersión: 1.0")
    print(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Parámetros del archivo de entrada
    ruta_archivo = '/mnt/data/Hospital_San_Lucas.xlsx'
    
    # 1. Cargar datos
    print("\n" + "="*70)
    print("CARGANDO DATOS")
    print("="*70)
    
    df_empleados = cargar_datos_empleados(ruta_archivo)
    df_demograficos = cargar_datos_demograficos(ruta_archivo)
    
    # 2. Validar y limpiar datos
    df_empleados = validar_y_limpiar_datos(df_empleados)
    
    # 3. Realizar valuación
    resultados = valuar_poblacion(df_empleados, df_demograficos)
    
    # 4. Exportar resultados
    exportar_resultados(resultados, df_empleados, df_demograficos)
    
    # 5. Resumen final
    print("\n" + "="*70)
    print("RESUMEN DE LA VALUACIÓN")
    print("="*70)
    
    reserva_total = sum(r['Reserva'] for r in resultados)
    pv_pensiones_total = sum(r['PV_Pensiones'] for r in resultados)
    pv_contribuciones_total = sum(r['PV_Contribuciones_Total'] for r in resultados)
    n_elegibles = sum(1 for r in resultados if r['Elegible_Pension'])
    
    print(f"\n  Total de empleados valuados: {len(resultados)}")
    print(f"  Empleados elegibles a pensión: {n_elegibles} ({n_elegibles/len(resultados)*100:.1f}%)")
    print(f"\n  PV Total de Pensiones: ${pv_pensiones_total:,.2f}")
    print(f"  PV Total de Contribuciones: ${pv_contribuciones_total:,.2f}")
    print(f"  Reserva Total del Plan: ${reserva_total:,.2f}")
    
    print("\n" + "="*70)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("="*70)
    print("\nEl archivo 'valuacion_resultados.xlsx' ha sido generado.")
    print("Contiene 12 hojas con todos los cálculos actuariales.")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n" + "="*70)
        print("ERROR EN LA EJECUCIÓN")
        print("="*70)
        print(f"\nSe produjo un error: {e}")
        print("\nPor favor, verifique:")
        print("  1. Que el archivo Excel existe en la ruta especificada")
        print("  2. Que las hojas 'DATA' y 'Demográficos' existen")
        print("  3. Que tiene permisos de escritura en el directorio")
        print("  4. Que las dependencias están instaladas (pip install -r requirements.txt)")
        print("\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
