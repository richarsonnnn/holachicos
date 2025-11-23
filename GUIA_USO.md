# Guía de Uso - Sistema de Valuación Actuarial

## Tabla de Contenidos
1. [Instalación Rápida](#instalación-rápida)
2. [Ejecución Básica](#ejecución-básica)
3. [Preparación de Datos](#preparación-de-datos)
4. [Interpretación de Resultados](#interpretación-de-resultados)
5. [Personalización](#personalización)
6. [Solución de Problemas](#solución-de-problemas)

---

## Instalación Rápida

### Paso 1: Instalar Python
Asegúrese de tener Python 3.8 o superior instalado:
```bash
python3 --version
```

### Paso 2: Instalar Dependencias
```bash
pip install -r requirements.txt
```

Esto instalará:
- pandas (manipulación de datos)
- numpy (cálculos numéricos)
- openpyxl (lectura/escritura de Excel)

---

## Ejecución Básica

### Modo Normal (con archivo de datos)
```bash
python3 valuacion_actuarial.py
```

El script buscará el archivo `/mnt/data/Hospital_San_Lucas.xlsx`. Si no lo encuentra, generará automáticamente datos de ejemplo para demostración.

### Verificar Instalación
```bash
python3 test_valuacion.py
```

Esto ejecutará 18 pruebas unitarias para verificar que todo funciona correctamente.

---

## Preparación de Datos

### Estructura del Archivo Excel

Su archivo Excel debe llamarse `Hospital_San_Lucas.xlsx` y contener dos hojas:

#### Hoja 1: "DATA"
Columnas requeridas:

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| ID | Entero | Identificador único | 1, 2, 3... |
| Fecha de nacimiento | Fecha | DD/MM/YYYY | 15/03/1985 |
| Fecha de alta | Fecha | DD/MM/YYYY | 01/06/2010 |
| Salario diario | Número | Pesos por día | 1500.00 |
| Estatus empleado | Texto | ACTIVO o PENSIONADO | ACTIVO |
| Método de pago | Texto | NOMINA u HONORARIOS | NOMINA |
| Sexo | Texto | M o F | M |

**Notas:**
- Para empleados ACTIVOS: "Salario diario" se multiplica por 30 para obtener salario mensual
- Para empleados PENSIONADOS: "Salario diario" se interpreta como pensión mensual

#### Hoja 2: "Demográficos"
Columnas requeridas:

| Columna | Tipo | Descripción | Rango |
|---------|------|-------------|-------|
| Edad | Entero | 0 a 120 | 0-120 |
| Hombres qx | Decimal | Tasa mortalidad hombres | 0.0-1.0 |
| Mujeres qx | Decimal | Tasa mortalidad mujeres | 0.0-1.0 |
| Renuncia Voluntaria | Decimal | Tasa de renuncia | 0.0-1.0 |
| Invalidez | Decimal | Tasa de invalidez | 0.0-1.0 |
| Jubilación | Decimal | Tasa de jubilación | 0.0-1.0 |

**Importante:** Las tasas deben estar en formato decimal (0.05 = 5%, no escribir "5%")

### Ejemplo de Datos Válidos

```csv
# Hoja DATA
ID,Fecha de nacimiento,Fecha de alta,Salario diario,Estatus empleado,Método de pago,Sexo
1,1980-05-15,2005-03-01,1200.00,ACTIVO,NOMINA,M
2,1975-08-22,2000-06-15,1500.00,ACTIVO,NOMINA,F
3,1960-12-10,1995-01-20,1000.00,PENSIONADO,NOMINA,M

# Hoja Demográficos
Edad,Hombres qx,Mujeres qx,Renuncia Voluntaria,Invalidez,Jubilación
30,0.0015,0.0010,0.08,0.005,0.0
40,0.0025,0.0018,0.05,0.008,0.0
50,0.0050,0.0035,0.03,0.012,0.0
65,0.0150,0.0100,0.01,0.020,0.8
```

---

## Interpretación de Resultados

El archivo de salida `valuacion_resultados.xlsx` contiene 12 hojas:

### 1. Detallado_por_empleado
**Uso:** Revisión individual de cada empleado

Columnas clave:
- `Reserva_Individual`: Monto que se debe reservar por empleado
- `Elegible_Pension`: Si califica para pensión (Sí/No)
- `PV_Pensiones`: Valor presente de sus pensiones futuras
- `PV_Total_Contribuciones`: Valor presente de contribuciones futuras

**Interpretación:**
- Reserva positiva = Beneficios exceden contribuciones
- Reserva negativa = Contribuciones exceden beneficios

### 2. Salarios_Proyectados
**Uso:** Ver crecimiento salarial esperado

- Filas = Empleados
- Columnas = Año 0, Año 1, Año 2...
- Valores = Salario mensual proyectado

### 3. Salarios_PV
**Uso:** Salarios descontados a valor presente

Similar a Salarios_Proyectados pero con descuento del 4% aplicado.

### 4. Primas
**Uso:** Primas de antigüedad por quinquenios

Muestra el pago anual de primas por cada empleado.

**Cálculo:**
- 0-4 años: 1 quinquenio = 1 × salario mensual/año
- 5-9 años: 2 quinquenios = 2 × salario mensual/año
- 10-14 años: 3 quinquenios = 3 × salario mensual/año
- 15+ años: 4 quinquenios = 4 × salario mensual/año (máximo)

### 5. Aportaciones
**Uso:** Contribuciones esperadas de trabajador y patrón

Columnas:
- `PV_Contrib_Trabajador`: 8% del salario anual
- `PV_Contrib_Patron`: 8% del salario anual (configurable)
- `PV_Total_Contribuciones`: Suma de ambos

### 6. Jubilados
**Uso:** Empleados que califican para pensión

**Criterios de elegibilidad:**
- Edad al retiro: ≥ 65 años
- Años de servicio al retiro: ≥ 15 años

Muestra:
- Años hasta el retiro
- Pensión inicial (60% del salario final)
- Valor presente de la pensión

### 7. PV_Jubilados
**Uso:** Flujo año por año de pensiones

Matriz de pensiones esperadas descontadas a valor presente.

### 8. Reserva
**Uso:** Cálculo de reserva total del plan

Muestra:
- Reserva individual por empleado
- Suma total de reservas
- Comparación inflows vs outflows

**Fórmula:**
```
Reserva = PV_Beneficios - PV_Contribuciones
donde:
  PV_Beneficios = PV_Pensiones + PV_Primas
  PV_Contribuciones = PV_Trabajador + PV_Patrón
```

### 9. Escenarios
**Uso:** Análisis de sensibilidad

Muestra la reserva total bajo tres escenarios:
1. Aporte patronal 8% (base)
2. Aporte patronal 10%
3. Aporte patronal 12%

**Interpretación:**
- Aumento de aporte patronal → Disminución de reserva requerida

### 10. Resumen
**Uso:** Visión general del plan

Métricas clave:
- Número total de empleados
- Porcentaje elegible a pensión
- Edad y antigüedad promedio
- Reserva total del plan
- Reserva promedio por empleado

### 11-12. Transpuestos
**Uso:** Vista alternativa de datos

Matrices transpuestas para análisis temporal (años en filas).

---

## Personalización

### Cambiar Parámetros Actuariales

Edite la clase `ParametrosActuariales` en `valuacion_actuarial.py`:

```python
class ParametrosActuariales:
    # Tasas de crecimiento
    INCREMENTO_SALARIAL = 0.035  # 3.5% → cambiar según necesidad
    INCREMENTO_PENSION = 0.025   # 2.5%
    TASA_DESCUENTO = 0.04        # 4.0%
    
    # Contribuciones
    PCT_CONTRIBUCION_TRABAJADOR = 0.08  # 8%
    PCT_CONTRIBUCION_PATRON = 0.08      # 8%
    
    # Elegibilidad
    EDAD_RETIRO = 65                    # edad mínima
    ANOS_MINIMOS_SERVICIO = 15          # años mínimos
    
    # Pensión
    TASA_REEMPLAZO = 0.60              # 60% del salario final
    
    # Archivo de entrada
    RUTA_ARCHIVO_DEFAULT = '/mnt/data/Hospital_San_Lucas.xlsx'
```

### Cambiar Ruta del Archivo

**Opción 1:** Modificar la clase
```python
RUTA_ARCHIVO_DEFAULT = '/ruta/a/tu/archivo.xlsx'
```

**Opción 2:** Modificar en main()
```python
def main():
    ruta_archivo = '/ruta/personalizada/datos.xlsx'
    df_empleados = cargar_datos_empleados(ruta_archivo)
    # ...
```

---

## Solución de Problemas

### Error: "No such file or directory"
**Causa:** No se encuentra el archivo Excel

**Solución:**
1. Verificar que el archivo existe en la ruta especificada
2. Verificar permisos de lectura del archivo
3. El script generará datos de ejemplo automáticamente si no encuentra el archivo

### Error: "KeyError: 'Fecha de nacimiento'"
**Causa:** Faltan columnas requeridas en la hoja DATA

**Solución:**
Asegúrese de que la hoja DATA tenga todas las columnas requeridas con los nombres exactos.

### Error: "ValueError: could not convert string to float"
**Causa:** Valores no numéricos en columnas de salario o tasas

**Solución:**
- Verificar que "Salario diario" contenga solo números
- Verificar que las tasas qx estén en formato decimal (0.05 no "5%")

### Advertencia: "empleados sin fecha de nacimiento"
**Causa:** Celdas vacías en datos críticos

**Solución:**
El script continuará pero los resultados pueden ser inexactos. Complete los datos faltantes.

### Resultados inesperados
**Verificaciones:**
1. Ejecutar test_valuacion.py para validar el código
2. Verificar que las tasas demográficas sean realistas (qx entre 0 y 1)
3. Verificar fechas de nacimiento y alta sean coherentes
4. Revisar la hoja "Resumen" para detectar anomalías

### Rendimiento lento
**Para 380+ empleados:**
- Tiempo esperado: 8-15 segundos
- Si tarda más: verificar que pandas/numpy estén actualizados
- Cerrar otros programas que consuman memoria

### Excel no abre el archivo de salida
**Causa:** Archivo corrupto o versión incompatible

**Solución:**
1. Verificar que openpyxl esté instalado: `pip install --upgrade openpyxl`
2. Abrir con Excel 2007 o superior
3. Intentar abrir con LibreOffice/Google Sheets

---

## Contacto y Soporte

Para soporte técnico o consultas actuariales:
- Revisar README.md principal
- Ejecutar test_valuacion.py para diagnóstico
- Contactar al equipo de Recursos Humanos del Hospital San Lucas

---

## Apéndice: Fórmulas Actuariales

### Proyección Salarial
```
S(t) = S(0) × (1 + i)^t
donde:
  S(t) = Salario en el año t
  S(0) = Salario inicial
  i = Incremento salarial (3.5%)
  t = Años
```

### Probabilidad de Estar Activo
```
P_activo(t) = ∏[1 - (qx_muerte + qx_renuncia + qx_invalidez)]
              desde t=0 hasta t
```

### Valor Presente
```
PV = Σ[Beneficio(t) × P(t) × v^t]
donde:
  v = 1/(1 + d)
  d = Tasa de descuento (4%)
```

### Pensión Proyectada
```
Pensión(t) = Pensión_inicial × (1 + ip)^t
donde:
  Pensión_inicial = 0.60 × Salario_final
  ip = Incremento de pensión (2.5%)
```

---

**Última actualización:** Noviembre 2025  
**Versión del documento:** 1.0
