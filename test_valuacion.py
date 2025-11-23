#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for Valuación Actuarial Script

Tests key functionality including:
- Data loading and validation
- Demographic calculations
- Salary projections
- Contribution calculations
- Pension calculations
- Reserve calculations
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from valuacion_actuarial import (
    ParametrosActuariales,
    cargar_datos_empleados,
    validar_y_limpiar_datos,
    crear_datos_ejemplo,
    crear_tabla_demografica_ejemplo,
    obtener_qx_demografico,
    calcular_probabilidad_activo,
    calcular_probabilidad_supervivencia_post_retiro,
    proyectar_salarios,
    calcular_salario_anual,
    calcular_contribuciones,
    calcular_primas_antiguedad,
    es_elegible_pension,
    calcular_pension,
    valuar_empleado,
    generar_hoja_detallado,
    generar_hoja_jubilados,
    generar_hoja_reserva,
    generar_hoja_resumen
)


def test_parametros_actuariales():
    """Test that actuarial parameters are correctly set."""
    print("Test 1: Parámetros Actuariales...")
    
    assert ParametrosActuariales.INCREMENTO_SALARIAL == 0.035, "Incremento salarial incorrecto"
    assert ParametrosActuariales.INCREMENTO_PENSION == 0.025, "Incremento pensión incorrecto"
    assert ParametrosActuariales.TASA_DESCUENTO == 0.04, "Tasa descuento incorrecta"
    assert ParametrosActuariales.PCT_CONTRIBUCION_TRABAJADOR == 0.08, "Contribución trabajador incorrecta"
    assert ParametrosActuariales.PCT_CONTRIBUCION_PATRON == 0.08, "Contribución patrón incorrecta"
    assert ParametrosActuariales.EDAD_RETIRO == 65, "Edad retiro incorrecta"
    assert ParametrosActuariales.ANOS_MINIMOS_SERVICIO == 15, "Años mínimos incorrectos"
    assert ParametrosActuariales.EDAD_MAXIMA == 120, "Edad máxima incorrecta"
    assert ParametrosActuariales.TASA_REEMPLAZO == 0.60, "Tasa reemplazo incorrecta"
    
    # Test discount factor
    v = ParametrosActuariales.factor_descuento(1)
    assert abs(v - 1/1.04) < 0.0001, "Factor de descuento incorrecto"
    
    print("  ✓ Parámetros actuariales correctos")


def test_crear_datos_ejemplo():
    """Test that example data is created correctly."""
    print("\nTest 2: Creación de Datos de Ejemplo...")
    
    df = crear_datos_ejemplo()
    
    assert len(df) == 50, "Debe crear 50 empleados"
    assert 'ID' in df.columns, "Falta columna ID"
    assert 'Fecha de nacimiento' in df.columns, "Falta columna Fecha de nacimiento"
    assert 'Fecha de alta' in df.columns, "Falta columna Fecha de alta"
    assert 'Salario diario' in df.columns, "Falta columna Salario diario"
    assert 'Sexo' in df.columns, "Falta columna Sexo"
    
    # Verify data ranges
    assert df['Salario diario'].min() >= 500, "Salario muy bajo"
    assert df['Salario diario'].max() <= 2000, "Salario muy alto"
    
    print("  ✓ Datos de ejemplo creados correctamente")


def test_crear_tabla_demografica():
    """Test that demographic table is created correctly."""
    print("\nTest 3: Creación de Tabla Demográfica...")
    
    df = crear_tabla_demografica_ejemplo()
    
    assert len(df) == 121, "Debe tener 121 edades (0-120)"
    assert 'Edad' in df.columns, "Falta columna Edad"
    assert 'Hombres qx' in df.columns, "Falta columna Hombres qx"
    assert 'Mujeres qx' in df.columns, "Falta columna Mujeres qx"
    assert 'Renuncia Voluntaria' in df.columns, "Falta columna Renuncia"
    assert 'Invalidez' in df.columns, "Falta columna Invalidez"
    
    # Verify qx are between 0 and 1
    assert (df['Hombres qx'] >= 0).all(), "qx negativo"
    assert (df['Hombres qx'] <= 1).all(), "qx mayor que 1"
    
    print("  ✓ Tabla demográfica creada correctamente")


def test_validar_y_limpiar_datos():
    """Test data validation and cleaning."""
    print("\nTest 4: Validación y Limpieza de Datos...")
    
    df_original = crear_datos_ejemplo()
    df_limpio = validar_y_limpiar_datos(df_original)
    
    assert 'Edad' in df_limpio.columns, "Falta columna Edad calculada"
    assert 'Anos_Servicio' in df_limpio.columns, "Falta columna Años de servicio"
    assert 'Salario_Mensual' in df_limpio.columns, "Falta columna Salario mensual"
    
    # Verify calculated fields
    assert (df_limpio['Edad'] > 0).all(), "Edades deben ser positivas"
    assert (df_limpio['Anos_Servicio'] > 0).all(), "Antigüedad debe ser positiva"
    assert (df_limpio['Salario_Mensual'] > 0).all(), "Salario mensual debe ser positivo"
    
    print("  ✓ Datos validados y limpiados correctamente")


def test_obtener_qx_demografico():
    """Test demographic rate extraction."""
    print("\nTest 5: Obtención de Tasas Demográficas...")
    
    df_demo = crear_tabla_demografica_ejemplo()
    
    # Test for a specific age and gender
    qx = obtener_qx_demografico(45, 'M', df_demo)
    
    assert 'qx_muerte' in qx, "Falta qx_muerte"
    assert 'qx_renuncia' in qx, "Falta qx_renuncia"
    assert 'qx_invalidez' in qx, "Falta qx_invalidez"
    
    assert 0 <= qx['qx_muerte'] <= 1, "qx_muerte fuera de rango"
    assert 0 <= qx['qx_renuncia'] <= 1, "qx_renuncia fuera de rango"
    assert 0 <= qx['qx_invalidez'] <= 1, "qx_invalidez fuera de rango"
    
    print("  ✓ Tasas demográficas obtenidas correctamente")


def test_calcular_probabilidad_activo():
    """Test active probability calculation."""
    print("\nTest 6: Cálculo de Probabilidad de Estar Activo...")
    
    df_demo = crear_tabla_demografica_ejemplo()
    
    prob = calcular_probabilidad_activo(30, 10, 'M', df_demo)
    
    assert len(prob) == 11, "Debe haber 11 probabilidades (0 a 10 años)"
    assert prob[0] == 1.0, "Probabilidad inicial debe ser 1"
    assert (prob >= 0).all(), "Probabilidades no pueden ser negativas"
    assert (prob <= 1).all(), "Probabilidades no pueden exceder 1"
    assert all(prob[i] >= prob[i+1] for i in range(len(prob)-1)), "Probabilidades deben decrecer"
    
    print("  ✓ Probabilidades de estar activo calculadas correctamente")


def test_calcular_probabilidad_supervivencia():
    """Test post-retirement survival probability."""
    print("\nTest 7: Probabilidad de Supervivencia Post-Retiro...")
    
    df_demo = crear_tabla_demografica_ejemplo()
    
    prob = calcular_probabilidad_supervivencia_post_retiro(65, 20, 'F', df_demo)
    
    assert len(prob) == 21, "Debe haber 21 probabilidades (0 a 20 años)"
    assert prob[0] == 1.0, "Probabilidad inicial debe ser 1"
    assert (prob >= 0).all(), "Probabilidades no pueden ser negativas"
    assert all(prob[i] >= prob[i+1] for i in range(len(prob)-1)), "Probabilidades deben decrecer"
    
    print("  ✓ Probabilidades de supervivencia calculadas correctamente")


def test_proyectar_salarios():
    """Test salary projection."""
    print("\nTest 8: Proyección de Salarios...")
    
    salario_inicial = 30000
    anos = 10
    
    salarios = proyectar_salarios(salario_inicial, anos)
    
    assert len(salarios) == anos + 1, "Debe haber anos+1 salarios"
    assert salarios[0] == salario_inicial, "Salario inicial incorrecto"
    
    # Verify growth rate
    for i in range(1, len(salarios)):
        expected = salario_inicial * (1.035 ** i)
        assert abs(salarios[i] - expected) < 0.01, f"Salario año {i} incorrecto"
    
    print("  ✓ Salarios proyectados correctamente")


def test_calcular_salario_anual():
    """Test annual salary calculation."""
    print("\nTest 9: Cálculo de Salario Anual...")
    
    salarios_mensuales = np.array([30000, 31050, 32107])
    salarios_anuales = calcular_salario_anual(salarios_mensuales)
    
    assert len(salarios_anuales) == len(salarios_mensuales), "Longitud incorrecta"
    assert salarios_anuales[0] == 30000 * 12, "Salario anual incorrecto"
    
    print("  ✓ Salarios anuales calculados correctamente")


def test_calcular_contribuciones():
    """Test contribution calculations."""
    print("\nTest 10: Cálculo de Contribuciones...")
    
    salarios_anuales = np.array([360000, 372600, 385401])
    prob_activo = np.array([1.0, 0.95, 0.90])
    
    contrib_trab, contrib_patron, pv_trab, pv_patron = calcular_contribuciones(
        salarios_anuales, prob_activo, 0.08, 0.08
    )
    
    assert len(contrib_trab) == len(salarios_anuales), "Longitud incorrecta"
    assert (contrib_trab >= 0).all(), "Contribuciones no pueden ser negativas"
    assert pv_trab > 0, "PV trabajador debe ser positivo"
    assert pv_patron > 0, "PV patrón debe ser positivo"
    assert abs(pv_trab - pv_patron) < 0.01, "PV deben ser iguales con misma tasa"
    
    print("  ✓ Contribuciones calculadas correctamente")


def test_calcular_primas_antiguedad():
    """Test seniority premium calculations."""
    print("\nTest 11: Cálculo de Primas de Antigüedad...")
    
    salarios_mensuales = np.array([30000, 31050, 32107])
    anos_servicio = 7.5
    prob_activo = np.array([1.0, 0.95, 0.90])
    
    primas, pv_primas = calcular_primas_antiguedad(salarios_mensuales, anos_servicio, prob_activo)
    
    assert len(primas) == len(salarios_mensuales), "Longitud incorrecta"
    assert (primas >= 0).all(), "Primas no pueden ser negativas"
    assert pv_primas > 0, "PV primas debe ser positivo"
    
    # Verify quinquenios calculation
    # 7.5 años = 1 + floor(7.5/5) = 2 quinquenios
    expected_prima_0 = 2 * 30000 * 1.0
    assert abs(primas[0] - expected_prima_0) < 0.01, "Prima inicial incorrecta"
    
    print("  ✓ Primas de antigüedad calculadas correctamente")


def test_es_elegible_pension():
    """Test pension eligibility."""
    print("\nTest 12: Elegibilidad de Pensión...")
    
    # Elegible: edad 65, 15 años servicio
    assert es_elegible_pension(65, 15) == True, "Debe ser elegible"
    assert es_elegible_pension(66, 20) == True, "Debe ser elegible"
    
    # No elegible: edad insuficiente
    assert es_elegible_pension(64, 20) == False, "No debe ser elegible (edad)"
    
    # No elegible: servicio insuficiente
    assert es_elegible_pension(65, 14) == False, "No debe ser elegible (servicio)"
    
    # No elegible: ambos insuficientes
    assert es_elegible_pension(60, 10) == False, "No debe ser elegible"
    
    print("  ✓ Elegibilidad de pensión correcta")


def test_calcular_pension():
    """Test pension calculation."""
    print("\nTest 13: Cálculo de Pensión...")
    
    df_demo = crear_tabla_demografica_ejemplo()
    
    # Test elegible employee
    resultado = calcular_pension(50, 20, 30000, 'M', df_demo)
    
    assert 'anos_hasta_retiro' in resultado, "Falta años hasta retiro"
    assert 'pension_inicial' in resultado, "Falta pensión inicial"
    assert 'pv_pension' in resultado, "Falta PV pensión"
    assert 'elegible' in resultado, "Falta elegibilidad"
    
    assert resultado['elegible'] == True, "Debe ser elegible"
    assert resultado['anos_hasta_retiro'] == 15, "Años hasta retiro incorrectos"
    assert resultado['pv_pension'] > 0, "PV pensión debe ser positivo"
    
    # Test non-eligible employee (age 30, only 2 years service = 37 years at 65, but needs 15 min)
    # This employee would have 2 + 35 = 37 years service at age 65, so IS eligible
    # Let's test someone who starts at age 55 with only 5 years (will have only 15 at 65 - borderline eligible)
    resultado_borderline = calcular_pension(55, 5, 30000, 'M', df_demo)
    # At 65: 5 + 10 = 15 years, so eligible
    assert resultado_borderline['elegible'] == True, "Debe ser elegible con 15 años"
    
    # Test truly non-eligible: age 52 with only 2 years service (will have 15 at 65 - borderline)
    # Age 53 with 1 year = 13 years at 65 - NOT eligible
    resultado_no_elegible = calcular_pension(53, 1, 30000, 'M', df_demo)
    assert resultado_no_elegible['elegible'] == False, "No debe ser elegible (solo 13 años al retiro)"
    assert resultado_no_elegible['pv_pension'] == 0, "PV debe ser 0 para no elegible"
    
    print("  ✓ Pensiones calculadas correctamente")


def test_valuar_empleado():
    """Test complete employee valuation."""
    print("\nTest 14: Valuación Completa de Empleado...")
    
    # Create test employee
    df_emp = crear_datos_ejemplo()
    df_demo = crear_tabla_demografica_ejemplo()
    df_emp = validar_y_limpiar_datos(df_emp)
    
    empleado = df_emp.iloc[0]
    resultado = valuar_empleado(empleado, df_demo)
    
    # Check all required fields
    required_fields = [
        'ID', 'Edad', 'Anos_Servicio', 'Salario_Mensual', 'Sexo',
        'Elegible_Pension', 'PV_Pensiones', 'PV_Primas',
        'PV_Contrib_Trabajador', 'PV_Contrib_Patron',
        'PV_Contribuciones_Total', 'PV_Outflows', 'Reserva'
    ]
    
    for field in required_fields:
        assert field in resultado, f"Falta campo {field}"
    
    # Verify calculations
    assert resultado['PV_Contribuciones_Total'] == (
        resultado['PV_Contrib_Trabajador'] + resultado['PV_Contrib_Patron']
    ), "PV contribuciones total incorrecto"
    
    assert resultado['PV_Outflows'] == (
        resultado['PV_Pensiones'] + resultado['PV_Primas']
    ), "PV outflows incorrecto"
    
    assert resultado['Reserva'] == (
        resultado['PV_Outflows'] - resultado['PV_Contribuciones_Total']
    ), "Reserva incorrecta"
    
    print("  ✓ Valuación de empleado completa y correcta")


def test_generar_hoja_detallado():
    """Test detailed sheet generation."""
    print("\nTest 15: Generación de Hoja Detallado...")
    
    df_emp = crear_datos_ejemplo()
    df_demo = crear_tabla_demografica_ejemplo()
    df_emp = validar_y_limpiar_datos(df_emp)
    
    # Valuar algunos empleados
    resultados = []
    for i in range(5):
        resultado = valuar_empleado(df_emp.iloc[i], df_demo)
        resultados.append(resultado)
    
    df_detalle = generar_hoja_detallado(resultados)
    
    assert len(df_detalle) == 5, "Debe tener 5 filas"
    assert 'ID' in df_detalle.columns, "Falta columna ID"
    assert 'Reserva_Individual' in df_detalle.columns, "Falta columna Reserva"
    assert 'Elegible_Pension' in df_detalle.columns, "Falta columna Elegible"
    
    print("  ✓ Hoja detallado generada correctamente")


def test_generar_hoja_jubilados():
    """Test retirees sheet generation."""
    print("\nTest 16: Generación de Hoja Jubilados...")
    
    df_emp = crear_datos_ejemplo()
    df_demo = crear_tabla_demografica_ejemplo()
    df_emp = validar_y_limpiar_datos(df_emp)
    
    resultados = []
    for i in range(10):
        resultado = valuar_empleado(df_emp.iloc[i], df_demo)
        resultados.append(resultado)
    
    df_jubilados = generar_hoja_jubilados(resultados)
    
    # Should only include eligible employees
    assert 'ID' in df_jubilados.columns, "Falta columna ID"
    
    print("  ✓ Hoja jubilados generada correctamente")


def test_generar_hoja_reserva():
    """Test reserve sheet generation."""
    print("\nTest 17: Generación de Hoja Reserva...")
    
    df_emp = crear_datos_ejemplo()
    df_demo = crear_tabla_demografica_ejemplo()
    df_emp = validar_y_limpiar_datos(df_emp)
    
    resultados = []
    for i in range(5):
        resultado = valuar_empleado(df_emp.iloc[i], df_demo)
        resultados.append(resultado)
    
    df_reserva = generar_hoja_reserva(resultados)
    
    assert len(df_reserva) == 6, "Debe tener 5 empleados + 1 total"
    assert df_reserva.iloc[-1]['ID'] == 'TOTAL', "Última fila debe ser TOTAL"
    
    # Verify total
    suma_manual = sum(r['Reserva'] for r in resultados)
    suma_hoja = df_reserva.iloc[-1]['Reserva_Individual']
    assert abs(suma_manual - suma_hoja) < 0.01, "Total de reserva incorrecto"
    
    print("  ✓ Hoja reserva generada correctamente")


def test_generar_hoja_resumen():
    """Test summary sheet generation."""
    print("\nTest 18: Generación de Hoja Resumen...")
    
    df_emp = crear_datos_ejemplo()
    df_demo = crear_tabla_demografica_ejemplo()
    df_emp = validar_y_limpiar_datos(df_emp)
    
    resultados = []
    for i in range(10):
        resultado = valuar_empleado(df_emp.iloc[i], df_demo)
        resultados.append(resultado)
    
    df_resumen = generar_hoja_resumen(resultados)
    
    assert 'Metrica' in df_resumen.columns, "Falta columna Metrica"
    assert 'Valor' in df_resumen.columns, "Falta columna Valor"
    assert len(df_resumen) > 10, "Debe tener múltiples métricas"
    
    print("  ✓ Hoja resumen generada correctamente")


def run_all_tests():
    """Run all tests."""
    print("="*70)
    print("EJECUTANDO SUITE DE PRUEBAS")
    print("="*70)
    
    tests = [
        test_parametros_actuariales,
        test_crear_datos_ejemplo,
        test_crear_tabla_demografica,
        test_validar_y_limpiar_datos,
        test_obtener_qx_demografico,
        test_calcular_probabilidad_activo,
        test_calcular_probabilidad_supervivencia,
        test_proyectar_salarios,
        test_calcular_salario_anual,
        test_calcular_contribuciones,
        test_calcular_primas_antiguedad,
        test_es_elegible_pension,
        test_calcular_pension,
        test_valuar_empleado,
        test_generar_hoja_detallado,
        test_generar_hoja_jubilados,
        test_generar_hoja_reserva,
        test_generar_hoja_resumen,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FALLO: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print("RESULTADOS DE PRUEBAS")
    print("="*70)
    print(f"  Total de pruebas: {passed + failed}")
    print(f"  Exitosas: {passed}")
    print(f"  Fallidas: {failed}")
    
    if failed == 0:
        print("\n  ✓ TODAS LAS PRUEBAS PASARON")
    else:
        print(f"\n  ✗ {failed} PRUEBA(S) FALLARON")
    
    print("="*70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
