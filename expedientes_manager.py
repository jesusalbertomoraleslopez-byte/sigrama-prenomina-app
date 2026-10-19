"""
=============================================================================
INDUSTRIA SIGRAMA S.A. DE C.V. — MÓDULO DE GESTIÓN DE EXPEDIENTES DIGITALES
- Auto-generación de expedientes al detectar personal en asistencias/nómina
- Seguimiento de checklist documental de Capital Humano (INE, RFC, CURP, NSS, etc.)
- Almacenamiento y sincronización de expedientes digitales con GCS / GitHub
=============================================================================
"""

import os
import io
import re
import json
import base64
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

# Definición del Checklist Documental Obligatorio por Capital Humano (LFT)
LISTA_DOCS_EXPEDIENTE = [
    ("Doc_INE", "🪪 Identificación Oficial (INE / Pasaporte)"),
    ("Doc_CURP", "📑 Constancia de CURP Oficial"),
    ("Doc_RFC", "🏛️ Constancia de Situación Fiscal (RFC / SAT)"),
    ("Doc_NSS", "🏥 Número de Seguridad Social (NSS / IMSS)"),
    ("Doc_Domicilio", "🏠 Comprobante de Domicilio Vigente"),
    ("Doc_Contrato", "🖋️ Contrato Individual de Trabajo Firmado"),
    ("Doc_Alta_IMSS", "📋 Aviso de Alta ante el IMSS"),
    ("Doc_CV", "📄 Solicitud de Empleo / Currículum Vitae")
]

COLUMNAS_EXPEDIENTE = [
    "Numero_Control_Personal",
    "Nombre_Empleado_Robotica",
    "Puesto",
    "Fecha_de_Ingreso",
    "CURP",
    "CURP_ARCHIVO",
    "RFC",
    "NSS",
    "Curriculum",
    "Fotografia",
    "Descripción_de_Puesto",
    "Tipo_Sangre",
    "Padecimientos:",
    "Alergias:",
    "Telefono:",
    "Contacto_Emergencia",
    "Estatus_Expediente",
    "Doc_INE",
    "Doc_CURP",
    "Doc_RFC",
    "Doc_NSS",
    "Doc_Domicilio",
    "Doc_Contrato",
    "Doc_Alta_IMSS",
    "Doc_CV"
]

# Mapa de equivalencias históricas Access -> Checador / Nómina Real
MAPA_ALIAS_LEGACY = {
    '00001': '01247',
    '00002': '01293',
    '00003': '01370',
    '00004': '01145',
    '00005': '01371',
    '00006': '01363'
}

ALIAS_EXPANDIDO = {
    '00001': ['00001', '09517', '9517', '1', '1247', '01247'],
    '01247': ['00001', '09517', '9517', '1', '1247', '01247'],
    '1247':  ['00001', '09517', '9517', '1', '1247', '01247'],
    '00002': ['00002', '2', '1293', '01293'],
    '01293': ['00002', '2', '1293', '01293'],
    '1293':  ['00002', '2', '1293', '01293'],
    '00003': ['00003', '3', '1370', '01370'],
    '01370': ['00003', '3', '1370', '01370'],
    '1370':  ['00003', '3', '1370', '01370'],
    '00004': ['00004', '4', '1145', '01145'],
    '01145': ['00004', '4', '1145', '01145'],
    '1145':  ['00004', '4', '1145', '01145'],
    '00005': ['00005', '5', '1371', '01371'],
    '01371': ['00005', '5', '1371', '01371'],
    '1371':  ['00005', '5', '1371', '01371'],
    '00006': ['00006', '6', '1363', '01363'],
    '01363': ['00006', '6', '1363', '01363'],
    '1363':  ['00006', '6', '1363', '01363']
}


def calcular_aliases_empleado(num_ctrl: str) -> list:
    """Devuelve la lista de identificadores equivalentes para un empleado."""
    clean = str(num_ctrl).strip().zfill(5)
    num_int = str(int(clean)) if clean.isdigit() else clean
    aliases = ALIAS_EXPANDIDO.get(clean, ALIAS_EXPANDIDO.get(num_int, [clean, num_int]))
    if clean not in aliases:
        aliases.append(clean)
    if num_int not in aliases:
        aliases.append(num_int)
    return aliases


def buscar_foto_empleado(num_ctrl: str, ruta_carpeta: str) -> str:
    """Busca la foto del empleado en asistencias/fotos/ respetando aliases."""
    aliases = calcular_aliases_empleado(num_ctrl)
    dir_fotos = os.path.join(ruta_carpeta, "fotos").replace("\\", "/")
    if not os.path.exists(dir_fotos):
        return None

    for a in aliases:
        posibles = [
            f"foto_{a}.jpg",
            f"foto_{a}.png",
            f"foto_{a}.jpeg",
            f"foto_{int(a):05d}.jpg" if a.isdigit() else "",
            f"foto_{int(a)}.jpg" if a.isdigit() else ""
        ]
        for p in posibles:
            if not p:
                continue
            full_p = os.path.join(dir_fotos, p).replace("\\", "/")
            if os.path.exists(full_p):
                return full_p
    return None


def evaluar_estatus_expediente(row: pd.Series, ruta_carpeta: str = None) -> tuple:
    """
    Evalúa el estado del expediente de un colaborador considerando
    las banderas de la tabla y los archivos físicos en disco.
    Retorna: (completos, total, porcentaje, estatus_str, dict_docs)
    """
    total = len(LISTA_DOCS_EXPEDIENTE)
    completos = 0
    dict_docs = {}
    num_ctrl = str(row.get("Numero_Control_Personal", "")).strip().zfill(5)

    archivos_disco = []
    if ruta_carpeta:
        dir_emp = os.path.join(ruta_carpeta, "expedientes_digitales", num_ctrl).replace("\\", "/")
        if os.path.exists(dir_emp):
            archivos_disco = os.listdir(dir_emp)

    for col_key, etiqueta in LISTA_DOCS_EXPEDIENTE:
        val = str(row.get(col_key, "")).strip().lower()
        tiene_flag = val in ("true", "1", "si", "sí", "entregado", "completo")
        tiene_archivo = any(col_key.lower() in f.lower() for f in archivos_disco) if archivos_disco else False

        esta_ok = tiene_flag or tiene_archivo
        if esta_ok:
            completos += 1
        dict_docs[col_key] = {
            "etiqueta": etiqueta,
            "entregado": esta_ok,
            "archivo": next((f for f in archivos_disco if col_key.lower() in f.lower()), None) if archivos_disco else None
        }

    pct = int((completos / total) * 100) if total > 0 else 0
    if completos == total:
        estatus = "🟢 Expediente Completo (100%)"
    elif completos > 0:
        estatus = f"🟡 En Proceso ({completos}/{total} Documentos - {pct}%)"
    else:
        estatus = f"🔴 Incompleto (0/{total} Documentos)"

    return completos, total, pct, estatus, dict_docs


def asegurar_expedientes_personal(df_personal_cat: pd.DataFrame, df_asistencias_raw: pd.DataFrame, ruta_carpeta: str, guardar_sync_fn=None) -> list:
    """
    Verifica y sincroniza de forma transparente la base de expedientes (access_PERSONAL.csv):
    1. Si no existe access_PERSONAL.csv, lo crea con la estructura oficial.
    2. Convierte los IDs legacy 00001..00006 a los números de control reales de nómina (01247, 01293, etc.)
       preservando todos sus datos médicos, cursos y documentación previa.
    3. Para cualquier colaborador que esté en personal.xlsx o en asistencias_raw y NO tenga
       expediente, se genera automáticamente con su fecha de primer registro/ingreso detectada.
    4. Guarda y sincroniza el archivo.
    Retorna la lista de expedientes nuevos auto-generados.
    """
    csv_path = os.path.join(ruta_carpeta, "access_PERSONAL.csv").replace("\\", "/")
    os.makedirs(os.path.join(ruta_carpeta, "expedientes_digitales"), exist_ok=True)

    if os.path.exists(csv_path):
        try:
            df_acc = pd.read_csv(csv_path, dtype=str, encoding="utf-8-sig").fillna("")
        except Exception:
            try:
                df_acc = pd.read_csv(csv_path, dtype=str, encoding="latin1").fillna("")
            except Exception:
                df_acc = pd.DataFrame(columns=COLUMNAS_EXPEDIENTE)
    else:
        df_acc = pd.DataFrame(columns=COLUMNAS_EXPEDIENTE)

    # Asegurar que existan todas las columnas
    for c in COLUMNAS_EXPEDIENTE:
        if c not in df_acc.columns:
            df_acc[c] = ""

    cambio = False
    nuevos_generados = []

    # 1. Normalizar números de control de los 6 legacy
    for idx, r in df_acc.iterrows():
        n_ctrl = str(r["Numero_Control_Personal"]).strip().zfill(5)
        if n_ctrl in MAPA_ALIAS_LEGACY:
            nuevo_id = MAPA_ALIAS_LEGACY[n_ctrl]
            df_acc.at[idx, "Numero_Control_Personal"] = nuevo_id
            cambio = True

    # Obtener catálogo de colaboradores a verificar
    mapa_empleados = {}  # id_str -> {'nombre': ..., 'area': ...}
    if df_personal_cat is not None and not df_personal_cat.empty:
        for _, row in df_personal_cat.iterrows():
            eid = str(row.get("id_empleado", "")).strip()
            if eid and eid != "nan":
                mapa_empleados[eid] = {
                    "nombre": str(row.get("nombre", "")).strip(),
                    "area": str(row.get("area", "⚪ Sin Asignar")).strip()
                }

    # Mapa de fechas de primer registro en asistencias
    fechas_primer_ingreso = {}
    if df_asistencias_raw is not None and not df_asistencias_raw.empty:
        for _, r in df_asistencias_raw.iterrows():
            eid = str(r.get("#Empleado", "")).strip()
            nom = str(r.get("Nombre del Empleado", "")).strip()
            fec = r.get("Fecha_Clean")
            if not fec or pd.isna(fec):
                fec = str(r.get("Fecha_Raw", ""))[:10]
            else:
                fec = str(fec)[:10]

            if eid and eid != "nan":
                if eid not in mapa_empleados and nom:
                    mapa_empleados[eid] = {"nombre": nom, "area": "⚪ Sin Asignar"}

                if eid not in fechas_primer_ingreso or str(fec) < str(fechas_primer_ingreso[eid]):
                    fechas_primer_ingreso[eid] = str(fec)

    # 2. Verificar existencia en df_acc
    ids_en_acc = set(df_acc["Numero_Control_Personal"].astype(str).str.strip().str.zfill(5).tolist())

    for eid, info in mapa_empleados.items():
        ctrl_id = str(eid).zfill(5)
        if ctrl_id not in ids_en_acc:
            # Detectar fecha de ingreso
            f_ing = fechas_primer_ingreso.get(eid, "")
            if f_ing and len(f_ing) >= 10:
                try:
                    dt = pd.to_datetime(f_ing)
                    f_ing_fmt = dt.strftime("%d/%m/%Y") + " 12:00:00 a. m."
                except Exception:
                    f_ing_fmt = f_ing + " 12:00:00 a. m."
            else:
                f_ing_fmt = datetime.now().strftime("%d/%m/%Y") + " 12:00:00 a. m."

            nuevo_registro = {
                "Numero_Control_Personal": ctrl_id,
                "Nombre_Empleado_Robotica": info["nombre"],
                "Puesto": info["area"],
                "Fecha_de_Ingreso": f_ing_fmt,
                "CURP": "",
                "CURP_ARCHIVO": "",
                "RFC": "",
                "NSS": "",
                "Curriculum": "",
                "Fotografia": "",
                "Descripción_de_Puesto": "",
                "Tipo_Sangre": "N/D",
                "Padecimientos:": "NINGUNO",
                "Alergias:": "NINGUNA",
                "Telefono:": "",
                "Contacto_Emergencia": "",
                "Estatus_Expediente": "🔴 Incompleto (0/8 Documentos)",
                "Doc_INE": "False",
                "Doc_CURP": "False",
                "Doc_RFC": "False",
                "Doc_NSS": "False",
                "Doc_Domicilio": "False",
                "Doc_Contrato": "False",
                "Doc_Alta_IMSS": "False",
                "Doc_CV": "False"
            }

            df_acc = pd.concat([df_acc, pd.DataFrame([nuevo_registro])], ignore_index=True)
            ids_en_acc.add(ctrl_id)
            nuevos_generados.append({
                "id": eid,
                "numero_control": ctrl_id,
                "nombre": info["nombre"],
                "area": info["area"],
                "fecha_ingreso": f_ing_fmt[:10]
            })
            cambio = True

            # Crear carpeta digital para sus documentos
            os.makedirs(os.path.join(ruta_carpeta, "expedientes_digitales", ctrl_id), exist_ok=True)

    # 3. Guardar cambios si hubo
    if cambio:
        df_acc.to_csv(csv_path, index=False, encoding="utf-8-sig")
        if guardar_sync_fn:
            try:
                guardar_sync_fn(csv_path)
            except Exception as e:
                print(f"[Expedientes] Error al sincronizar CSV con GCS: {e}")

    return nuevos_generados


def guardar_expediente_colaborador(
    num_ctrl: str,
    datos: dict,
    ruta_carpeta: str,
    archivo_personal_path: str = None,
    guardar_sync_fn = None,
    github_token: str = None,
    repo_name: str = None
) -> bool:
    """
    Actualiza la ficha técnica y documentación de un colaborador,
    calculando automáticamente el estatus del expediente y sincronizando con GCS y GitHub.
    """
    csv_path = os.path.join(ruta_carpeta, "access_PERSONAL.csv").replace("\\", "/")
    if not os.path.exists(csv_path):
        return False

    df_acc = pd.read_csv(csv_path, dtype=str, encoding="utf-8-sig").fillna("")
    num_ctrl_clean = str(num_ctrl).strip().zfill(5)

    idx_match = df_acc[df_acc["Numero_Control_Personal"].astype(str).str.strip().str.zfill(5) == num_ctrl_clean].index
    if idx_match.empty:
        return False

    idx = idx_match[0]

    # Actualizar campos
    for k, v in datos.items():
        if k in df_acc.columns:
            df_acc.at[idx, k] = str(v).strip()

    # Evaluar estatus documental
    row_act = df_acc.loc[idx]
    comp, tot, pct, estatus, _ = evaluar_estatus_expediente(row_act, ruta_carpeta)
    df_acc.at[idx, "Estatus_Expediente"] = estatus

    # Guardar en CSV
    df_acc.to_csv(csv_path, index=False, encoding="utf-8-sig")

    if guardar_sync_fn:
        try:
            guardar_sync_fn(csv_path)
        except Exception:
            pass

    # Si se actualizó puesto o nombre, reflejarlo en personal.xlsx
    if archivo_personal_path and os.path.exists(archivo_personal_path):
        try:
            df_p = pd.read_excel(archivo_personal_path, dtype=str)
            id_int = str(int(num_ctrl_clean)) if num_ctrl_clean.isdigit() else num_ctrl_clean
            p_match = df_p[df_p["id_empleado"].astype(str).str.strip().isin([num_ctrl_clean, id_int])].index
            if not p_match.empty:
                p_idx = p_match[0]
                if "Puesto" in datos and datos["Puesto"]:
                    df_p.at[p_idx, "area"] = datos["Puesto"]
                if "Nombre_Empleado_Robotica" in datos and datos["Nombre_Empleado_Robotica"]:
                    df_p.at[p_idx, "nombre"] = datos["Nombre_Empleado_Robotica"]
                df_p.to_excel(archivo_personal_path, index=False)
                if guardar_sync_fn:
                    guardar_sync_fn(archivo_personal_path)
        except Exception as e:
            print(f"[Expedientes] Error actualizando personal.xlsx: {e}")

    # Sincronización GitHub si está configurado
    if github_token and repo_name:
        try:
            url_api = f"https://api.github.com/repos/{repo_name}/contents/asistencias/access_PERSONAL.csv"
            headers_gh = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Streamlit-App"
            }
            sha = None
            res_get = requests.get(url_api, headers=headers_gh, timeout=10)
            if res_get.status_code == 200:
                sha = res_get.json().get("sha")

            with open(csv_path, "rb") as f:
                content_bytes = f.read()

            payload = {
                "message": f"Actualización Expediente Digital - Empleado {num_ctrl_clean}",
                "content": base64.b64encode(content_bytes).decode("utf-8")
            }
            if sha:
                payload["sha"] = sha

            requests.put(url_api, json=payload, headers=headers_gh, timeout=15)
        except Exception as e:
            print(f"[Expedientes] Error sincronizando con GitHub: {e}")

    return True


def guardar_documento_adjunto(num_ctrl: str, doc_key: str, uploaded_file, ruta_carpeta: str, guardar_sync_fn=None) -> str:
    """
    Almacena físicamente un documento del expediente en asistencias/expedientes_digitales/{num_ctrl}/
    y actualiza la bandera correspondiente.
    """
    clean_id = str(num_ctrl).strip().zfill(5)
    dir_emp = os.path.join(ruta_carpeta, "expedientes_digitales", clean_id).replace("\\", "/")
    os.makedirs(dir_emp, exist_ok=True)

    # Limpiar nombre de archivo seguro
    nombre_orig = Path(uploaded_file.name).name
    ext = Path(nombre_orig).suffix.lower()
    nombre_seguro = f"{doc_key}_{clean_id}{ext}"
    ruta_destino = os.path.join(dir_emp, nombre_seguro).replace("\\", "/")

    with open(ruta_destino, "wb") as f_out:
        f_out.write(uploaded_file.getbuffer())

    if guardar_sync_fn:
        try:
            guardar_sync_fn(ruta_destino)
        except Exception:
            pass

    return ruta_destino
