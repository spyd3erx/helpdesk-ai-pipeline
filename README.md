# Proyecto DP-900: Helpdesk AI Pipeline

Pipeline de datos para preparar tickets de Freshservice como fuente de una futura solución de IA en Azure.

## Estructura

```text
.
├── data/                         # Datos locales; excluidos de Git
│   └── inspection/               # Inspecciones locales de tickets
├── docs/                         # Modelo y decisiones de datos
│   └── modelo-datos.md
├── notebooks/                    # Pruebas de datos y análisis interactivos
│   └── 01_validacion_ticket_31839.ipynb
├── .env.example                  # Plantilla de configuración, sin secretos
├── .gitignore                    # Excluye secretos, datos y checkpoints
├── .python-version               # Versión de Python del proyecto
├── pyproject.toml                # Paquete, dependencias y comando
├── uv.lock                       # Versiones resueltas de dependencias
└── src/helpdesk_ai_pipeline/
    ├── __init__.py
    ├── connectors/
    │   ├── __init__.py
    │   └── freshservice/         # Acceso a la API y herramientas del conector
    │       ├── __init__.py
    │       └── probe.py
    └── utils/                    # Utilidades reutilizables del paquete
        └── __init__.py
```

Las extracciones locales se guardan bajo `data/`, carpeta excluida de Git porque puede contener datos de clientes. El notebook de validación comprueba la clasificación sin mostrar los textos de tickets.

## Preparación

Requiere Python 3.12 o posterior y `uv`.

```powershell
uv sync
```

Configura `FRESHSERVICE_DOMAIN` y `FRESHSERVICE_API_KEY` en `.env`. Si aún no existe el archivo, créalo a partir de `.env.example`. No compartas ni incluyas `.env` en Git.

## Inspección de un ticket

El comando solo consulta Freshservice. Por defecto muestra metadatos y no imprime el contenido del ticket:

```powershell
uv run helpdesk-ai-pipeline 31839
```

Para guardar los textos localmente, indica una ruta de salida. El comando se niega a sobrescribir un archivo existente:

```powershell
uv run helpdesk-ai-pipeline 31839 --output data/inspection/ticket_31839.json
```

El JSON puede contener datos personales; mantenlo local y fuera de Git. Para abrir la validación Jupyter, inicia Jupyter desde la raíz del repositorio y abre `notebooks/01_validacion_ticket_31839.ipynb`. El notebook requiere la extracción local indicada en su primera celda.
