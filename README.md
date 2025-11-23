# Sistema de Valuación Actuarial - Hospital San Lucas

Sistema completo de valuación actuarial para realizar cálculos de reservas, pensiones, contribuciones y primas de antigüedad para todos los empleados del Hospital San Lucas.

## 📋 Descripción

Este script en Python realiza una valuación actuarial completa que incluye:

- Proyección de salarios con incremento anual del 3.5%
- Modelado demográfico (mortalidad, renuncia, invalidez)
- Cálculo de contribuciones de trabajador (8%) y patrón (8%)
- Cálculo de primas de antigüedad por quinquenios
- Proyección de pensiones con tasa de reemplazo del 60%
- Cálculo de valores presentes con tasa de descuento del 4%
- Determinación de reservas actuariales individuales y totales
- Análisis de escenarios con diferentes tasas de contribución patronal

## 🚀 Instalación

### Requisitos previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalar dependencias

```bash
pip install -r requirements.txt
```

Las dependencias incluyen:
- pandas (≥2.0.0): Para manipulación de datos
- numpy (≥1.24.0): Para cálculos numéricos
- openpyxl (≥3.1.0): Para leer y escribir archivos Excel

## 📊 Archivos de Entrada

El script espera un archivo Excel en la ruta `/mnt/data/Hospital_San_Lucas.xlsx` con las siguientes hojas:

### Hoja "DATA"
Contiene los datos de empleados con las columnas:
- **ID**: Identificador único del empleado
- **Fecha de nacimiento**: Fecha en formato de fecha de Excel
- **Fecha de alta**: Fecha de inicio de servicio
- **Salario diario**: Salario diario del empleado
- **Estatus empleado**: ACTIVO o PENSIONADO
- **Método de pago**: NOMINA u HONORARIOS
- **Sexo**: M (Masculino) o F (Femenino)

### Hoja "Demográficos"
Contiene las tasas demográficas por edad:
- **Edad**: Edad del empleado (0-120)
- **Hombres qx**: Tasa de mortalidad para hombres
- **Mujeres qx**: Tasa de mortalidad para mujeres
- **Renuncia Voluntaria**: Tasa de renuncia
- **Invalidez**: Tasa de invalidez
- **Jubilación**: Tasa de jubilación

### Datos de ejemplo

Si el archivo no se encuentra, el script **automáticamente genera datos de ejemplo** para demostración, permitiendo verificar el funcionamiento sin necesidad de tener el archivo real.

## 💻 Uso

### Ejecución básica

```bash
python valuacion_actuarial.py
```

### Ejecución con permisos

```bash
python3 valuacion_actuarial.py
```

## 📈 Supuestos Actuariales

El script utiliza los siguientes parámetros (configurables en la clase `ParametrosActuariales`):

| Parámetro | Valor |
|-----------|-------|
| Incremento salarial anual | 3.5% |
| Incremento anual de pensiones | 2.5% |
| Tasa de descuento | 4.0% |
| Contribución del trabajador | 8% |
| Contribución del patrón | 8% |
| Edad de retiro | 65 años |
| Años mínimos de servicio | 15 años |
| Edad máxima (omega) | 120 años |
| Tasa de reemplazo (pensión) | 60% del salario final |
| Máximo de quinquenios | 4 |

## 📑 Archivos de Salida

El script genera un archivo Excel llamado `valuacion_resultados.xlsx` con **12 hojas**:

### 1. Detallado_por_empleado
Resumen individual con:
- ID, Edad, Años de servicio, Salario mensual
- PV de pensiones, primas, contribuciones
- Reserva individual
- Elegibilidad a pensión

### 2. Salarios_Proyectados
Matriz de salarios proyectados (empleados × años)

### 3. Salarios_PV
Matriz de salarios con valor presente aplicado

### 4. Primas
Proyección de primas de antigüedad por empleado

### 5. Aportaciones
Contribuciones de trabajador y patrón

### 6. Jubilados
Lista de empleados elegibles para pensión con detalles

### 7. PV_Jubilados
Valor presente de pensiones proyectadas año por año

### 8. Reserva
Reservas individuales y total del plan

### 9. Escenarios
Análisis de sensibilidad con tres escenarios:
- Aporte patronal 8%
- Aporte patronal 10%
- Aporte patronal 12%

### 10. Resumen
Métricas clave del plan:
- Número de empleados
- Empleados elegibles
- Promedios (edad, antigüedad, salario)
- Totales de PV
- Reserva total del plan

### 11. Transpuestos_Salarios_Proy
Transposición de la matriz de salarios proyectados (años × empleados)

### 12. Transpuestos_Salarios_PV
Transposición de la matriz de salarios PV (años × empleados)

## 🧮 Metodología Actuarial

### Proyección Salarial
```
salario(t) = salario(0) × (1 + i)^t
donde i = 3.5% (incremento salarial)
```

### Modelado Demográfico
La probabilidad de estar activo en el año t se calcula como:
```
P_activo(t) = ∏[1 - (qx_muerte + qx_renuncia + qx_invalidez)]
```

### Contribuciones
```
Contribución(t) = Salario_anual(t) × % × P_activo(t) × v^t
donde v = 1/(1+d) y d = 4% (tasa de descuento)
```

### Primas de Antigüedad
```
n_quinquenios = min(1 + ⌊años_servicio/5⌋, 4)
Prima(t) = n_quinquenios × salario_mensual(t) × P_activo(t) × v^t
```

### Pensión
Para empleados elegibles (edad ≥ 65 y servicio ≥ 15 años):
```
Pensión_inicial = 0.60 × salario_al_retiro
Pensión(t) = Pensión_inicial × (1 + ip)^t
donde ip = 2.5% (incremento de pensión)

PV_Pensión = Σ[Pensión(t) × P_supervivencia(t) × v^(años_hasta_retiro + t)]
```

### Reserva Actuarial
```
Reserva = PV_Beneficios - PV_Contribuciones
donde:
  PV_Beneficios = PV_Pensiones + PV_Primas
  PV_Contribuciones = PV_Trabajador + PV_Patrón
```

## 🔧 Personalización

Para modificar los parámetros actuariales, edite la clase `ParametrosActuariales` en el archivo `valuacion_actuarial.py`:

```python
class ParametrosActuariales:
    INCREMENTO_SALARIAL = 0.035  # Cambiar según necesidad
    TASA_DESCUENTO = 0.04        # Cambiar según necesidad
    EDAD_RETIRO = 65             # Cambiar según plan
    # etc...
```

## 📊 Ejemplo de Ejecución

```bash
$ python valuacion_actuarial.py

======================================================================
SISTEMA DE VALUACIÓN ACTUARIAL
HOSPITAL SAN LUCAS
======================================================================

Cargando datos de empleados desde: /mnt/data/Hospital_San_Lucas.xlsx
  ✓ Se cargaron 380 empleados

Cargando datos demográficos...
  ✓ Se cargaron tasas para 121 edades

Validando y limpiando datos...
  ✓ Datos validados: 380 empleados
  ✓ Rango de edades: 22 - 68
  ✓ Rango de antigüedad: 0.5 - 35.0 años

INICIANDO VALUACIÓN ACTUARIAL
  Procesando empleado 50/380...
  Procesando empleado 100/380...
  ...
  ✓ Valuación completada para 380 empleados

GENERANDO ARCHIVO DE RESULTADOS
  Generando hoja: Detallado_por_empleado...
  Generando hoja: Salarios_Proyectados...
  ...
  ✓ Archivo generado exitosamente: valuacion_resultados.xlsx

RESUMEN DE LA VALUACIÓN
  Total de empleados valuados: 380
  Empleados elegibles a pensión: 215 (56.6%)
  
  PV Total de Pensiones: $X,XXX,XXX,XXX.XX
  PV Total de Contribuciones: $X,XXX,XXX,XXX.XX
  Reserva Total del Plan: $X,XXX,XXX,XXX.XX

PROCESO COMPLETADO EXITOSAMENTE
```

## 🛡️ Manejo de Errores

El script incluye manejo robusto de errores:

- **Archivo no encontrado**: Genera datos de ejemplo automáticamente
- **Datos faltantes**: Emite advertencias pero continúa la ejecución
- **Valores inconsistentes**: Aplica valores por defecto conservadores
- **Errores de cálculo**: Registra en logs y continúa con los demás empleados

## ⚠️ Notas Importantes

1. **Datos sensibles**: El script maneja información de empleados. Asegúrese de cumplir con las políticas de privacidad.

2. **Rendimiento**: Para 380+ empleados, la ejecución puede tomar 1-3 minutos dependiendo del hardware.

3. **Memoria**: El script está optimizado con pandas/numpy para ser eficiente con la memoria.

4. **Validación**: Aunque el script incluye validaciones, es recomendable que un actuario certificado revise los resultados.

5. **Backup**: El archivo de salida se sobrescribe en cada ejecución. Haga copias de seguridad si es necesario.

## 📝 Estructura del Código

```
valuacion_actuarial.py
├── Configuración de parámetros (ParametrosActuariales)
├── Funciones de carga de datos
│   ├── cargar_datos_empleados()
│   ├── cargar_datos_demograficos()
│   └── validar_y_limpiar_datos()
├── Funciones de modelado demográfico
│   ├── obtener_qx_demografico()
│   ├── calcular_probabilidad_activo()
│   └── calcular_probabilidad_supervivencia_post_retiro()
├── Funciones de proyección
│   ├── proyectar_salarios()
│   ├── calcular_contribuciones()
│   ├── calcular_primas_antiguedad()
│   └── calcular_pension()
├── Función de valuación
│   ├── valuar_empleado()
│   └── valuar_poblacion()
├── Funciones de generación de reportes
│   ├── generar_hoja_detallado()
│   ├── generar_matriz_proyeccion()
│   ├── generar_hoja_jubilados()
│   ├── generar_hoja_reserva()
│   ├── generar_hoja_escenarios()
│   └── generar_hoja_resumen()
├── Exportación
│   └── exportar_resultados()
└── main()
```

## 🤝 Contribuciones

Este script ha sido desarrollado específicamente para el Hospital San Lucas. Para modificaciones o mejoras, contacte al equipo actuarial.

## 📄 Licencia

Uso interno del Hospital San Lucas.

## 👥 Contacto

Para soporte técnico o consultas actuariales, contacte al equipo de Recursos Humanos del Hospital San Lucas.

---

**Versión**: 1.0  
**Última actualización**: Noviembre 2025  
**Autor**: Sistema Actuarial Hospital San Lucas
