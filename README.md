# Proyecto DP-900: Helpdesk AI Pipeline

Extractor de solo lectura para consultar tickets y conversaciones de Freshservice como parte de una futura solución de IA en Azure.

## Preparación

Requiere Python 3.12 o posterior y `uv`.

```powershell
uv sync
```

Configura `FRESHSERVICE_DOMAIN` y `FRESHSERVICE_API_KEY` en `.env`. Si el archivo no existe, créalo usando `.env.example`. No compartas ni incluyas `.env` en Git.

## Inspección de un ticket

El comando consulta Freshservice y muestra metadatos sin imprimir el contenido del ticket:

```powershell
uv run helpdesk-ai-pipeline 31839
```

Para guardar los textos localmente, proporciona una ruta de salida. El comando no sobrescribe archivos existentes:

```powershell
uv run helpdesk-ai-pipeline 31839 --output data/inspection/ticket_31839.json
```

Las extracciones pueden contener datos personales; mantenlas locales y fuera de Git.
