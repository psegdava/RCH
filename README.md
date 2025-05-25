# Proyecto RCH Algorithm

Este proyecto implementa el algoritmo RCH para la optimización de carga de contenedores y cálculos de volúmenes en logística.

## Estructura del Proyecto

```
RCH_Algorithm/
├── RCH_module/           # Implementación principal del algoritmo
├── input_RCH/           # Datos de entrada para cálculos RCH
├── input_total/         # Datos de entrada totales
├── viajes_prueba/       # Datos de viajes de prueba
├── soluciones/          # Directorio de soluciones
├── pruebas/             # Directorio de pruebas
├── not_loaded.xlsx      # Archivo de datos para artículos no cargados
├── requirements.txt     # Dependencias del proyecto
└── *.ipynb             # Cuadernos de Jupyter para análisis
```

## Requisitos

- Python 3.x
- Ver [requirements.txt](requirements.txt) para todas las dependencias
- Dependencias principales incluyen:
  - pandas
  - numpy
  - scikit-learn
  - tensorflow
  - fastai
  - varias bibliotecas de procesamiento y análisis de datos

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual (recomendado)
3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

El proyecto incluye varios cuadernos de Jupyter para diferentes propósitos:
- `carga_simple.ipynb`: Para leer y procesar datos de entrada y generar la solución de un viaje.
- `fetch_input.ipynb`: Para obtener datos de entrada de un archivo .xlsx
- `carga_dinamica.ipynb`: Para cálculos de carga dinámica, donde hay una carga inicial y una segunda carga con partidas que no se han cargado anteriormente.

La funcionalidad principal está implementada en el directorio `RCH_module`, con el algoritmo principal en `RCH.py`.

## Datos de Entrada

El proyecto trabaja con archivos Excel que contienen:
- Datos de Viajes
- Datos de Partidas
- Cálculos de volúmenes

## Salida

El proyecto genera cálculos de volúmenes para operaciones logísticas, con resultados almacenados en el directorio `soluciones`.

## Contribución

1. Fork el repositorio
2. Crea tu rama de características
3. Commit tus cambios
4. Push a la rama
5. Crea una nueva Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para detalles.
