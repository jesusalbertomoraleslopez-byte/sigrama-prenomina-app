"""
Script de sincronización automática de asistencias desde Microsoft Outlook.
Extrae los archivos adjuntos .xls enviados por el sistema checador (noreply@sigrama.com.mx)
con asunto 'ASISTENCIA DIARIA: MAQUINADOS DEL ...' y los guarda en la carpeta 'asistencias/'.
"""

import os
import sys
import glob
import subprocess
from datetime import datetime

# Rutas del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_ASISTENCIAS = os.path.join(BASE_DIR, "asistencias").replace("\\", "/")
LOG_FILE = os.path.join(BASE_DIR, "sync_outlook.log").replace("\\", "/")


def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def sincronizar_desde_outlook(dir_destino: str = DIR_ASISTENCIAS) -> list[str]:
    """
    Se conecta a la instancia local de Microsoft Outlook mediante COM
    y descarga los archivos adjuntos .xls de los correos de asistencia diaria y pre-nómina.
    """
    try:
        import win32com.client
    except ImportError:
        log("ERROR: La librería pywin32 no está instalada.")
        return []

    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
    except Exception as e:
        log(f"ERROR al conectar con Outlook: {e}")
        return []

    # Localizar la carpeta específica donde el usuario guarda las asistencias
    folder_target = None
    try:
        for acc in namespace.Folders:
            try:
                inbox = acc.Folders["Bandeja de entrada"]
                for f1 in inbox.Folders:
                    if "sigrama" in f1.Name.lower():
                        for f2 in f1.Folders:
                            if "asistencia" in f2.Name.lower():
                                folder_target = f2
                                break
                    if folder_target:
                        break
            except Exception:
                pass
            if folder_target:
                break
    except Exception as e:
        log(f"Advertencia al buscar carpeta: {e}")

    # Si no se encontró la subcarpeta, buscar en la Bandeja de Entrada por defecto
    items_to_check = []
    if folder_target:
        log(f"Carpeta detectada: {folder_target.Name} ({folder_target.Items.Count} correos)")
        items_to_check = list(folder_target.Items)
    else:
        try:
            inbox_default = namespace.GetDefaultFolder(6)  # olFolderInbox
            log(f"Buscando en Bandeja de Entrada general ({inbox_default.Items.Count} correos)")
            items_to_check = list(inbox_default.Items)
        except Exception as e:
            log(f"No se pudo acceder a la bandeja de entrada: {e}")
            return []

    os.makedirs(dir_destino, exist_ok=True)
    archivos_existentes = set(os.listdir(dir_destino))
    archivos_descargados = []

    for item in items_to_check:
        try:
            subject = getattr(item, "Subject", "")
            subj_upper = subject.upper()
            
            # Filtrar por los correos de checador
            es_asistencia = (
                "ASISTENCIA DIARIA" in subj_upper or 
                "MAQUINADOS" in subj_upper or 
                "PRE-NÓMINA" in subj_upper or
                "PRE-NOMINA" in subj_upper
            )

            if not es_asistencia:
                continue

            if hasattr(item, "Attachments") and item.Attachments.Count > 0:
                for att in item.Attachments:
                    fname = att.FileName
                    # Solo archivos Excel válidos
                    if fname.lower().endswith((".xls", ".xlsx")) and not fname.startswith("~$"):
                        if fname not in archivos_existentes:
                            dest_path = os.path.join(dir_destino, fname).replace("\\", "/")
                            att.SaveAsFile(dest_path)
                            archivos_existentes.add(fname)
                            archivos_descargados.append(fname)
                            log(f"Descargado: {fname} (Asunto: '{subject}')")
        except Exception as e:
            continue

    return archivos_descargados


def ejecutar_sync():
    log("================ INICIO DE SINCRONIZACIÓN OUTLOOK ================")
    descargados = sincronizar_desde_outlook(DIR_ASISTENCIAS)
    
    if descargados:
        log(f"Se descargaron {len(descargados)} archivo(s) nuevo(s): {', '.join(descargados)}")
        
        # Opcional: hacer commit y push a GitHub para que Streamlit Cloud también los reciba
        try:
            log("Sincronizando con repositorio Git...")
            subprocess.run(["git", "add", "asistencias/"], cwd=BASE_DIR, check=False)
            commit_msg = f"auto-sync: sincronizar {len(descargados)} archivo(s) de asistencia desde Outlook"
            res_commit = subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, capture_output=True, text=True)
            if res_commit.returncode == 0:
                res_push = subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, capture_output=True, text=True)
                if res_push.returncode == 0:
                    log("Repositorio actualizado en GitHub exitosamente.")
                else:
                    log(f"Aviso en git push: {res_push.stderr}")
            else:
                log("No hubo cambios adicionales para commit.")
        except Exception as eg:
            log(f"Aviso en sincronización Git: {eg}")
    else:
        log("No se encontraron nuevos archivos de asistencia pendientes en Outlook.")

    log("================ FIN DE SINCRONIZACIÓN ================\n")
    return len(descargados)


if __name__ == "__main__":
    total = ejecutar_sync()
    sys.exit(0)
