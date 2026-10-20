"""Read-only check of where a Freshservice ticket's resolution is stored."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from pydantic import SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    freshservice_domain: str
    freshservice_api_key: SecretStr


def _host(domain: str) -> str:
    value = domain.strip()
    if value.startswith(("https://", "http://")):
        value = urlsplit(value).netloc
    value = value.rstrip("/").lower()
    if "/" in value or ":" in value or "@" in value:
        raise ValueError
    if not value.endswith(".freshservice.com"):
        value = f"{value}.freshservice.com"
    if not value or value.startswith(".") or value.count(".") < 2:
        raise ValueError
    return value


def _get(client: httpx.Client, path: str) -> dict:
    response = client.get(path)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Consulta un ticket y, opcionalmente, guarda sus textos en JSON local.")
    parser.add_argument("ticket_id", type=int, help="ID del ticket que quieres revisar")
    parser.add_argument(
        "--output",
        type=Path,
        help="Guarda localmente la solicitud, la resolución y los textos de las conversaciones en JSON.",
    )
    args = parser.parse_args()

    try:
        settings = Settings()
        host = _host(settings.freshservice_domain)
    except (ValidationError, ValueError):
        print("Revisa FRESHSERVICE_DOMAIN y FRESHSERVICE_API_KEY en .env; sus valores no se mostrarán.")
        return 1

    try:
        with httpx.Client(
            base_url=f"https://{host}/api/v2/",
            auth=(settings.freshservice_api_key.get_secret_value(), "X"),
            timeout=20,
        ) as client:
            ticket_payload = _get(client, f"tickets/{args.ticket_id}")
            ticket = ticket_payload.get("ticket", ticket_payload)
            if not isinstance(ticket, dict):
                raise ValueError
            conversations_payload = _get(client, f"tickets/{args.ticket_id}/conversations")
    except httpx.HTTPStatusError as error:
        print(f"Freshservice respondió HTTP {error.response.status_code}; revisa acceso y permisos de lectura.")
        return 1
    except httpx.RequestError:
        print("No se pudo conectar con Freshservice; revisa la red y el dominio configurado.")
        return 1
    except (ValueError, KeyError):
        print("Freshservice devolvió una respuesta que no pude interpretar como JSON.")
        return 1

    conversations = conversations_payload.get("conversations", [])
    if not isinstance(conversations, list):
        conversations = []
    with_text = [
        item
        for item in conversations
        if isinstance(item, dict) and (item.get("body_text") or item.get("body"))
    ]
    private_count = sum(item.get("private") is True for item in with_text)
    public_count = sum(item.get("private") is False for item in with_text)
    notes = ticket.get("resolution_notes")

    print(f"Lectura correcta. Estado del ticket: {ticket.get('status', 'no disponible')}.")
    print(f"resolution_notes: {'con contenido' if isinstance(notes, str) and notes.strip() else 'vacío o ausente'}.")
    print(
        f"Conversaciones: {len(conversations)}; con contenido: {len(with_text)}; "
        f"privadas: {private_count}; públicas: {public_count}."
    )
    if args.output:
        if args.output.exists():
            print("El archivo de salida ya existe; el extractor no lo sobrescribió.")
            return 1
        extracted = {
            "ticket": {
                "id": ticket.get("id"),
                "status": ticket.get("status"),
                "type": ticket.get("type"),
                "category": ticket.get("category"),
                "sub_category": ticket.get("sub_category"),
                "description_text": ticket.get("description_text"),
                "resolution_notes": ticket.get("resolution_notes"),
            },
            "conversations": [
                {
                    "created_at": item.get("created_at"),
                    "private": item.get("private"),
                    "incoming": item.get("incoming"),
                    "source": item.get("source"),
                    "body_text": item.get("body_text"),
                }
                for item in with_text
            ],
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(extracted, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Texto extraído localmente a: {args.output}")
        print("El archivo puede contener datos personales; no lo compartas ni lo incluyas en Git.")
    else:
        print("No se mostró ni guardó el texto del ticket.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
