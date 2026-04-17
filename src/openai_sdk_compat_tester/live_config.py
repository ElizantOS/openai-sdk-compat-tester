from __future__ import annotations


def extract_model_ids(response) -> list[str]:
    model_ids: list[str] = []
    for entry in getattr(response, "data", []):
        if isinstance(entry, dict):
            model_id = entry.get("id")
        else:
            model_id = getattr(entry, "id", None)
        if isinstance(model_id, str) and model_id.strip():
            model_ids.append(model_id.strip())
    return model_ids


def choose_model_id(
    model_ids: list[str], preferred_model: str | None = None
) -> tuple[str, bool]:
    if not model_ids:
        raise ValueError("router returned no models from /v1/models")

    preferred = (preferred_model or "").strip()
    if preferred and preferred in model_ids:
        return preferred, False

    return model_ids[0], bool(preferred)
