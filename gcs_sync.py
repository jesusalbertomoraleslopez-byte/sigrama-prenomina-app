"""
=============================================================================
PRENOMINA Y ASISTENCIA - INDUSTRIA SIGRAMA S.A. DE C.V.
Módulo de Persistencia con Google Cloud Storage (Cloud Run)
=============================================================================
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ARCHIVO_PERSONAL = BASE_DIR / "personal.xlsx"
RUTA_ASISTENCIAS = BASE_DIR / "asistencias"

GCS_BUCKET = os.environ.get("GCS_BUCKET", "").strip()
_GCS_READY = False

def _gcs_bucket():
    from google.cloud import storage
    return storage.Client().bucket(GCS_BUCKET)

def sync_from_gcs():
    """Descarga personal.xlsx y la carpeta asistencias desde GCS al arrancar."""
    global _GCS_READY
    if not GCS_BUCKET:
        return False
    try:
        bucket = _gcs_bucket()
        count = 0
        RUTA_ASISTENCIAS.mkdir(parents=True, exist_ok=True)
        for blob in bucket.list_blobs():
            if blob.name.endswith("/"):
                continue
            if blob.name == "data/personal.xlsx" or blob.name == "personal.xlsx":
                if not ARCHIVO_PERSONAL.exists() or ARCHIVO_PERSONAL.stat().st_size != blob.size:
                    blob.download_to_filename(str(ARCHIVO_PERSONAL))
                    count += 1
            elif blob.name.startswith("asistencias/"):
                rel_parts = blob.name.split("/")
                local_path = BASE_DIR.joinpath(*rel_parts)
                local_path.parent.mkdir(parents=True, exist_ok=True)
                if not local_path.exists() or local_path.stat().st_size != blob.size:
                    blob.download_to_filename(str(local_path))
                    count += 1
        _GCS_READY = True
        print(f"[GCS] Sincronizados exitosamente {count} archivos de prenómina desde gs://{GCS_BUCKET}")
        return True
    except Exception as e:
        print(f"[GCS] Error al sincronizar desde gs://{GCS_BUCKET}: {e}")
        return False

def push_file_to_gcs(local_path: Path):
    """Sube un archivo a GCS."""
    if not (GCS_BUCKET and _GCS_READY):
        return False
    try:
        p = Path(local_path)
        if not p.exists():
            return False
        bucket = _gcs_bucket()
        rel_path = p.relative_to(BASE_DIR).as_posix()
        bucket.blob(rel_path).upload_from_filename(str(p))
        if rel_path == "personal.xlsx":
            bucket.blob("data/personal.xlsx").upload_from_filename(str(p))
        print(f"[GCS] Archivo subido: {rel_path}")
        return True
    except Exception as e:
        print(f"[GCS] Error al subir {local_path} a GCS: {e}")
        return False
