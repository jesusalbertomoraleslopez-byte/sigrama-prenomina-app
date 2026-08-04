# ==============================================================================
# SECCIÓN 1 - CONFIGURACIÓN DE PLATAFORMA E IMPORTACIONES
# ==============================================================================

import streamlit as st
import pandas as pd
import glob
import os
import io
import requests
import base64
import plotly.graph_objects as go
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


# Configuración estética de la interfaz del navegador
st.set_page_config(
    page_title="Industria Sigrama - Control de Pre-Nómina",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialización de variables de sesión para control de acceso
if "usuario_rol" not in st.session_state:
    st.session_state["usuario_rol"] = None
if "usuario_name" not in st.session_state:
    st.session_state["usuario_name"] = None

# Inyección de Estilos CSS Oficiales de Industria Sigrama
st.markdown("""
<style>
/* Importación de tipografías desde Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400;1,700&family=Questrial&display=swap');

/* Aplicación global de fuentes y colores base */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    font-family: 'Questrial', 'Montserrat', sans-serif !important;
    background-color: #FFFFFF !important;
    color: #111111 !important;
}

/* Encabezados y títulos con Montserrat */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 700 !important;
    color: #111111 !important;
}

/* ==========================================
   BARRA LATERAL (SIDEBAR) - MODO OSCURO #111111
   ========================================== */
[data-testid="stSidebar"] {
    background-color: #111111 !important;
    color: #FFFFFF !important;
    border-right: 1px solid #D2D3D5 !important;
}

/* Todos los textos del sidebar en blanco */
[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] span, 
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] h4, 
[data-testid="stSidebar"] h5, 
[data-testid="stSidebar"] h6 {
    color: #FFFFFF !important;
    font-family: 'Questrial', sans-serif !important;
}

/* Inputs en la barra lateral */
[data-testid="stSidebar"] input {
    color: #111111 !important;
}

/* File Uploader Dropzone en Sidebar */
[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] {
    border: 2px dashed #D2D3D5 !important;
    background-color: #222222 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] * {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] button {
    background-color: #EC2024 !important;
    color: #FFFFFF !important;
    border: 1px solid #EC2024 !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 4px !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] button:hover {
    background-color: #B81216 !important;
    border-color: #B81216 !important;
}

/* ==========================================
   BOTONES CORPORATIVOS (#EC2024)
   ========================================== */
div.stButton > button, div.stButton > button[kind="primary"] {
    background-color: #EC2024 !important;
    color: #FFFFFF !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important;
    border: 1px solid #EC2024 !important;
    border-radius: 6px !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.3s ease-in-out !important;
}

div.stButton > button:hover {
    background-color: #B81216 !important;
    border-color: #B81216 !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 10px rgba(236, 32, 36, 0.25) !important;
    transform: translateY(-1px) !important;
}

div.stButton > button:active {
    transform: translateY(1px) !important;
}

/* Botones secundarios (download buttons, etc) */
div.stDownloadButton > button {
    background-color: #FFFFFF !important;
    color: #EC2024 !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important;
    border: 2px solid #EC2024 !important;
    border-radius: 6px !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.3s ease-in-out !important;
}

div.stDownloadButton > button:hover {
    background-color: #EC2024 !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 10px rgba(236, 32, 36, 0.25) !important;
}

/* ==========================================
   INPUTS Y SELECTORES (FOCO #EC2024)
   ========================================== */
/* Text inputs, number inputs, time, date */
div[data-baseweb="input"] {
    border: 1px solid #D2D3D5 !important;
    border-radius: 6px !important;
    background-color: #FFFFFF !important;
}
div[data-baseweb="input"]:focus-within {
    border-color: #EC2024 !important;
    box-shadow: 0 0 0 2px rgba(236, 32, 36, 0.2) !important;
}

/* Selectbox / Dropdowns */
div[data-baseweb="select"] {
    border: 1px solid #D2D3D5 !important;
    border-radius: 6px !important;
    background-color: #FFFFFF !important;
}
div[data-baseweb="select"]:focus-within {
    border-color: #EC2024 !important;
    box-shadow: 0 0 0 2px rgba(236, 32, 36, 0.2) !important;
}

/* ==========================================
   PESTAÑAS (TABS)
   ========================================== */
button[data-baseweb="tab"] {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 500 !important;
    color: #111111 !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s ease !important;
}
button[data-baseweb="tab"]:hover {
    color: #EC2024 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #EC2024 !important;
    font-weight: 700 !important;
    border-bottom: 2px solid #EC2024 !important;
}

/* ==========================================
   MÉTRICAS (METRICS)
   ========================================== */
[data-testid="stMetricValue"] {
    color: #EC2024 !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
    color: #111111 !important;
    font-family: 'Questrial', sans-serif !important;
}
[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    color: #FFFFFF !important;
}

/* ==========================================
   LÍNEAS DIVISORIAS (HR)
   ========================================== */
hr {
    border: 0 !important;
    height: 2px !important;
    background: #EC2024 !important;
    margin: 1.5rem 0 !important;
}

/* ==========================================
   ESTILOS PERSONALIZADOS PARA ESLÓGANES
   ========================================== */
.slogan-transformacion {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 700 !important;
    font-size: 20px !important;
    color: #EC2024 !important;
    text-align: center !important;
    letter-spacing: 1.5px !important;
    margin: 15px 0 !important;
    text-transform: uppercase !important;
}

.slogan-resultados-container {
    text-align: center !important;
    margin: 25px auto !important;
}

.slogan-resultados {
    font-family: 'Questrial', sans-serif !important;
    font-style: italic !important;
    font-size: 18px !important;
    color: #111111 !important;
    display: inline-block !important;
    position: relative !important;
    padding-bottom: 6px !important;
}

.slogan-resultados::after {
    content: '' !important;
    position: absolute !important;
    left: 0 !important;
    bottom: 0 !important;
    width: 100% !important;
    height: 1px !important;
    background-color: #EC2024 !important;
}

.slogan-resultados-sidebar {
    font-family: 'Questrial', sans-serif !important;
    font-style: italic !important;
    font-size: 14px !important;
    color: #FFFFFF !important;
    display: inline-block !important;
    position: relative !important;
    padding-bottom: 4px !important;
}

.slogan-resultados-sidebar::after {
    content: '' !important;
    position: absolute !important;
    left: 0 !important;
    bottom: 0 !important;
    width: 100% !important;
    height: 1px !important;
    background-color: #EC2024 !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# ENCABEZADO INSTITUCIONAL - BANNER DE RECURSOS HUMANOS
# ==============================================================================
NOMBRE_BANNER = "RH BANNER APP.png"

# Verificamos si el archivo del banner existe en la raíz del repositorio de GitHub
if os.path.exists(NOMBRE_BANNER):
    st.image(
        NOMBRE_BANNER, 
        use_container_width=True,
        caption="Industria Sigrama S.A. de C.V. | Dirección Humana, Resultados e Innovación"
    )

else:
    # Si el banner aún no se sube, muestra un título de respaldo limpio para que la app no falle
    st.title("🏭 Industria Sigrama S.A. de C.V.")
    st.subheader("Panel Operativo de Control de Pre-Nómina e Incidencias")

# Eslógan de Transformación
st.markdown('<div class="slogan-transformacion">SOLUCIONES QUE TRANSFORMAN TU EMPRESA</div>', unsafe_allow_html=True)

st.markdown("---") # Línea divisoria estética antes de iniciar los paneles y pestañas

# Constantes del Sistema
ARCHIVO_PERSONAL = "personal.xlsx"
ruta_carpeta = "./asistencias"
ARCHIVO_HISTORICO = os.path.join(ruta_carpeta, "historico_semanal.xlsx").replace("\\", "/")

if not os.path.exists(ruta_carpeta):
    os.makedirs(ruta_carpeta)

# --- RECONOCIMIENTO DEL TOKEN DESDE SECRETS ---
try:
    GITHUB_TOKEN = st.secrets["github"]["token"]
except:
    GITHUB_TOKEN = None

REPO_NAME = "jesusalbertomoraleslopez-byte/sigrama-prenomina-app"

# ==============================================================================
# SECCIÓN 1.5 - FUNCIONES AUXILIARES GLOBALES (DEFINICIÓN TEMPRANA)
# ==============================================================================

def limpiar_registro_hora(valor_celda):
    if pd.isna(valor_celda) or str(valor_celda).strip() == "":
        return None
    texto_hora = str(valor_celda).strip()
    if "1900" in texto_hora:
        componentes = texto_hora.split(" ")
        if len(componentes) >= 3:
            texto_hora = componentes[1] + " " + " ".join(componentes[2:])
    texto_hora = texto_hora.replace("a. m.", "AM").replace("p. m.", "PM").replace("a.m.", "AM").replace("p.m.", "PM")
    try:
        return pd.to_datetime(texto_hora, format="%I:%M:%S %p").time()
    except:
        try:
            return pd.to_datetime(texto_hora, format="%H:%M:%S").time()
        except:
            return valor_celda.time() if hasattr(valor_celda, 'time') else None

@st.cache_data
def procesar_base_asistencias(carpeta):
    ruta_busqueda = os.path.join(carpeta, "*.xls").replace("\\", "/")
    archivos = glob.glob(ruta_busqueda)
    if not archivos:
        return None
    listado = []
    for r in archivos:
        try:
            df = pd.read_excel(r, skiprows=1, engine='xlrd')
            df.columns = df.columns.str.strip().str.replace('\n', '').str.replace('\r', '')
            df_limpio = pd.DataFrame()
            df_limpio['#Empleado'] = df.iloc[:, 1]
            df_limpio['Nombre del Empleado'] = df.iloc[:, 2]
            col_fecha = [c for c in df.columns if 'Fecha' in str(c)]
            col_hora = [c for c in df.columns if 'Hora Entrada' in str(c)]
            col_nave = [c for c in df.columns if 'Nave Entrada' in str(c)]
            df_limpio['Fecha_Raw'] = df[col_fecha] if col_fecha else df.iloc[:, 4]
            df_limpio['Hora Entrada Raw'] = df[col_hora] if col_hora else df.iloc[:, 6]
            df_limpio['Nave Entrada'] = df[col_nave] if col_nave else df.iloc[:, 7]
            df_limpio = df_limpio.dropna(subset=['#Empleado'])
            df_limpio['#Empleado'] = pd.to_numeric(df_limpio['#Empleado'], errors='coerce').dropna().astype(int).astype(str)
            listado.append(df_limpio)
        except:
            continue
    if listado:
        df_master = pd.concat(listado, ignore_index=True)
        df_master['Fecha_Clean'] = pd.to_datetime(df_master['Fecha_Raw'], errors='coerce', dayfirst=True).dt.date
        return df_master
    return None

def recalcular_historico_completo(ruta_dir_asistencias, archivo_personal_path, limite_hora):
    if not os.path.exists(archivo_personal_path):
        return pd.DataFrame(columns=["Semana", "Fecha Inicio", "Fecha Fin", "Asistencia", "Puntualidad", "Tasa de Ausencia"])
    try:
        df_p = pd.read_excel(archivo_personal_path, dtype=str)
        df_p['id_empleado'] = df_p['id_empleado'].str.strip()
        employees = df_p['id_empleado'].dropna().tolist()
    except:
        return pd.DataFrame(columns=["Semana", "Fecha Inicio", "Fecha Fin", "Asistencia", "Puntualidad", "Tasa de Ausencia"])
        
    if not employees:
        return pd.DataFrame(columns=["Semana", "Fecha Inicio", "Fecha Fin", "Asistencia", "Puntualidad", "Tasa de Ausencia"])
        
    df_m = procesar_base_asistencias(ruta_dir_asistencias)
    if df_m is None or df_m.empty:
        return pd.DataFrame(columns=["Semana", "Fecha Inicio", "Fecha Fin", "Asistencia", "Puntualidad", "Tasa de Ausencia"])
        
    df_m['util_hora'] = df_m['Hora Entrada Raw'].apply(limpiar_registro_hora)
    
    codigos = []
    for _, fila in df_m.iterrows():
        nave = str(fila.get('Nave Entrada', '')).strip().upper()
        if "FALTA" in nave or pd.isna(fila['util_hora']): codigos.append("F")
        elif fila['util_hora'] > limite_hora: codigos.append("R")
        else: codigos.append("A")
    df_m['Cod_Incidencia'] = codigos
    
    df_m['Fecha_Clean'] = pd.to_datetime(df_m['Fecha_Clean']).dt.date
    unique_dates = sorted(df_m['Fecha_Clean'].dropna().unique())
    
    # Mapear la fecha del primer registro/ingreso de cada empleado en los archivos cargados
    primeros_ingresos = (
        df_m.dropna(subset=['Fecha_Clean'])
        .groupby('#Empleado')['Fecha_Clean']
        .min()
        .to_dict()
    )
    
    semanas_agrupadas = {}
    for d in unique_dates:
        if d.weekday() <= 4: # Lunes a Viernes
            year, week_num, weekday = d.isocalendar()
            week_key = (year, week_num)
            if week_key not in semanas_agrupadas:
                semanas_agrupadas[week_key] = []
            semanas_agrupadas[week_key].append(d)
            
    renglones = []
    for k, v in sorted(semanas_agrupadas.items()):
        total_a, total_r, total_f = 0, 0, 0
        total_records = 0
        for date_val in v:
            df_day = df_m[df_m['Fecha_Clean'] == date_val].copy()
            df_day['#Empleado'] = df_day['#Empleado'].astype(str).str.strip()
            day_map = df_day.groupby('#Empleado')['Cod_Incidencia'].apply(lambda x: 'A' if 'A' in list(x) else ('R' if 'R' in list(x) else 'F')).to_dict()
            for emp in employees:
                # Solo se considera al colaborador a partir de su primer registro de asistencia en el sistema
                first_date = primeros_ingresos.get(emp)
                if first_date is not None and date_val >= first_date:
                    total_records += 1
                    status = day_map.get(emp, 'F')
                    if status == 'A': total_a += 1
                    elif status == 'R': total_r += 1
                    elif status == 'F': total_f += 1
                
        conteo_asistencias = total_a + total_r
        pct_asist = (conteo_asistencias / total_records * 100) if total_records > 0 else 0.0
        pct_punt = (total_a / conteo_asistencias * 100) if conteo_asistencias > 0 else 0.0
        pct_ausen = (total_f / total_records * 100) if total_records > 0 else 0.0
        
        v_sorted = sorted(v)
        start_week = v_sorted[0]
        end_week = v_sorted[-1]
        
        renglones.append({
            "Semana": f"Semana {k[1]}",
            "Fecha Inicio": start_week.strftime("%d-%b-%y").lower(),
            "Fecha Fin": end_week.strftime("%d-%b-%y").lower(),
            "Asistencia": f"{pct_asist:.2f}% ({conteo_asistencias} de {total_records})",
            "Puntualidad": f"{pct_punt:.2f}% ({total_a} de {conteo_asistencias})",
            "Tasa de Ausencia": f"{pct_ausen:.2f}% ({total_f} de {total_records})"
        })
        
    return pd.DataFrame(renglones)


# ==============================================================================
# SECCIÓN 2 - PANEL LATERAL Y CARGADOR DE ARCHIVOS
# ================================================# Variables por defecto para evitar errores al cargar la app sin sesión
hora_limite_input = datetime.strptime("08:01:00", "%H:%M:%S").time()
hoy_real = datetime.now().date()
if hoy_real.day <= 15:
    defecto_inicio = hoy_real.replace(day=1)
    defecto_fin = hoy_real.replace(day=15)
else:
    defecto_inicio = hoy_real.replace(day=16)
    siguiente_mes = hoy_real.replace(day=28) + timedelta(days=4)
    defecto_fin = siguiente_mes - timedelta(days=siguiente_mes.day)

fecha_inicio = defecto_inicio
fecha_fin = defecto_fin
archivos_correo = None

# ==============================================================================
# SECCIÓN 2 - PANEL LATERAL Y CARGADOR DE ARCHIVOS
# ==============================================================================
logo_sidebar = "logo_sigrama_negativo.png"
if os.path.exists(logo_sidebar):
    st.sidebar.image(logo_sidebar, use_container_width=True)
    st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Control de Acceso en Sidebar
if st.session_state["usuario_rol"] is not None:
    st.sidebar.write(f"👤 **Usuario:** `{st.session_state['usuario_name']}`")
    st.sidebar.write(f"💼 **Rol:** `{st.session_state['usuario_rol']}`")
    if st.sidebar.button("🔒 Cerrar Sesión", use_container_width=True, key="sidebar_logout_btn"):
        st.session_state["usuario_rol"] = None
        st.session_state["usuario_name"] = None
        st.rerun()
        
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Configuración del Periodo")
    
    # Cargador de archivos en espera
    st.sidebar.subheader("📥 Cargar Nuevas Asistencias")
    
    # Mostrar mensaje de éxito si existe en el estado de sesión y limpiarlo
    if "mensaje_exito" in st.session_state and st.session_state["mensaje_exito"]:
        st.sidebar.success(st.session_state["mensaje_exito"])
        st.session_state["mensaje_exito"] = None
        
    if "uploader_key_counter" not in st.session_state:
        st.session_state["uploader_key_counter"] = 0
        
    archivos_correo = st.sidebar.file_uploader(
        "Arrastra aquí tus archivos .xls del correo:", 
        type=["xls"], 
        accept_multiple_files=True,
        key=f"uploader_{st.session_state['uploader_key_counter']}"
    )
    
    if archivos_correo:
        st.sidebar.info(f"📋 {len(archivos_correo)} archivo(s) listos.")
        
        # Entrada de clave de autorización para guardar asistencias en GitHub
        clave_usuario_asist = st.sidebar.text_input(
            "Clave de Autorización para GitHub:", 
            type="password", 
            key="clave_asist_input"
        )
        
        if st.sidebar.button("💾 Subir y Registrar en GitHub", use_container_width=True):
            if clave_usuario_asist != "RHSigrama":
                st.sidebar.error("❌ Clave incorrecta. No tienes autorización.")
            else:
                with st.sidebar.status("Subiendo archivos de asistencia...", expanded=True) as status:
                    success_count = 0
                    for archivo in archivos_correo:
                        nombre_archivo = archivo.name
                        # 1. Guardar de forma local
                        ruta_local = os.path.join(ruta_carpeta, nombre_archivo).replace("\\", "/")
                        with open(ruta_local, "wb") as f:
                            f.write(archivo.getbuffer())
                        
                        # 2. Subir a GitHub si hay token
                        if GITHUB_TOKEN:
                            url_api_file = f"https://api.github.com/repos/{REPO_NAME}/contents/asistencias/{nombre_archivo}"
                            headers_github = {
                                "Authorization": f"token {GITHUB_TOKEN}",
                                "Accept": "application/vnd.github.v3+json",
                                "User-Agent": "Streamlit-App"
                            }
                            
                            # Obtener SHA si ya existe para reemplazarlo
                            sha_file = None
                            res_get = requests.get(url_api_file, headers=headers_github, timeout=10)
                            if res_get.status_code == 200:
                                sha_file = res_get.json().get("sha")
                            
                            payload = {
                                "message": f"Sincronización de asistencia: {nombre_archivo}",
                                "content": base64.b64encode(archivo.getvalue()).decode("utf-8")
                            }
                            if sha_file:
                                payload["sha"] = sha_file
                                
                            res_put = requests.put(url_api_file, json=payload, headers=headers_github, timeout=15)
                            if res_put.status_code in [200, 201]:
                                success_count += 1
                            else:
                                st.sidebar.error(f"Error subiendo {nombre_archivo} a GitHub: {res_put.status_code}")
                        else:
                            success_count += 1
                    
                    # 3. Recalcular e inyectar el nuevo histórico a GitHub
                    df_hist_new = recalcular_historico_completo(ruta_carpeta, ARCHIVO_PERSONAL, hora_limite_input)
                    if not df_hist_new.empty:
                        df_hist_new.to_excel(ARCHIVO_HISTORICO, index=False)
                        if GITHUB_TOKEN:
                            url_api_hist = f"https://api.github.com/repos/{REPO_NAME}/contents/asistencias/historico_semanal.xlsx"
                            headers_github = {
                                "Authorization": f"token {GITHUB_TOKEN}",
                                "Accept": "application/vnd.github.v3+json",
                                "User-Agent": "Streamlit-App"
                            }
                            
                            res_get_hist = requests.get(url_api_hist, headers=headers_github, timeout=10)
                            sha_hist = None
                            if res_get_hist.status_code == 200:
                                sha_hist = res_get_hist.json().get("sha")
                                
                            with open(ARCHIVO_HISTORICO, "rb") as f_hist:
                                conteo_bytes_hist = f_hist.read()
                            
                            payload_hist = {
                                "message": "Sincronización de historico_semanal.xlsx",
                                "content": base64.b64encode(conteo_bytes_hist).decode("utf-8")
                            }
                            if sha_hist:
                                payload_hist["sha"] = sha_hist
                                
                            requests.put(url_api_hist, json=payload_hist, headers=headers_github, timeout=15)
                    
                    # Limpiamos el caché de Streamlit para que cargue los nuevos archivos xls
                    st.cache_data.clear()
                    
                    # Incrementamos el contador para resetear la caja de archivos y guardamos el mensaje de éxito
                    st.session_state["uploader_key_counter"] += 1
                    st.session_state["mensaje_exito"] = f"✅ ¡{success_count} archivo(s) guardado(s) y sincronizado(s) en GitHub con éxito!"
                    
                    status.update(label="✅ ¡Archivos e historial sincronizados!", state="complete")
                    st.rerun()
        
    # Selección de Hora Límite
    hora_limite_input = st.sidebar.time_input(
        "Hora límite de Entrada:", 
        value=datetime.strptime("08:01:00", "%H:%M:%S").time()
    )
    
    # Selección de Fechas de Quincena
    st.sidebar.subheader("📅 Fechas de la Quincena")
    fecha_inicio = st.sidebar.date_input("Fecha Inicio:", value=defecto_inicio)
    fecha_fin = st.sidebar.date_input("Fecha Fin:", value=defecto_fin)
else:
    st.sidebar.info("🔐 Por favor, inicie sesión en la pantalla principal para configurar la aplicación.")

# --- FUNCIÓN DE AUTOGENERACIÓN Y CARGA DE EXCEL DE PERSONAL ---
def cargar_catalogo_personal():
    if not os.path.exists(ARCHIVO_PERSONAL):
        df_base = pd.DataFrame(columns=["id_empleado", "nombre", "area"])
        df_base.to_excel(ARCHIVO_PERSONAL, index=False)
        return df_base
    try:
        df = pd.read_excel(ARCHIVO_PERSONAL, dtype=str)
        df['id_empleado'] = df['id_empleado'].str.strip()
        df['nombre'] = df['nombre'].str.strip()
        df['area'] = df['area'].str.strip()
        return df[df['id_empleado'].notna() & (df['id_empleado'] != 'nan')]
    except:
        return pd.DataFrame(columns=["id_empleado", "nombre", "area"])


# ==============================================================================
# SECCIÓN 5 - INTERFAZ CORPORATIVA Y PARSER DE HORAS (CORREGIDA SIN DUPLICADOS)
# ==============================================================================
st.markdown("<h2 style='text-align: center;'>👥 Portal de Capital Humano</h2>", unsafe_allow_html=True)
st.markdown("---")




def aplicar_colores_matriz(val):
    if val in ["A", "R"]:
        return 'background-color: #d4edda; color: #155724; font-weight: bold; text-align: center;'
    elif val == "F":
        return 'background-color: #f8d7da; color: #721c24; font-weight: bold; text-align: center;'
    elif val in ["S", "D"]:
        return 'background-color: #fff3cd; color: #856404; font-weight: bold; text-align: center;'
    elif val == "TxT":
        return 'background-color: #ffe0b2; color: #e65100; font-weight: bold; text-align: center;'
    return 'text-align: center;'

def dibujar_reloj_donut(porcentaje, titulo, color_linea):
    fig = go.Figure(data=[go.Pie(
        labels=['Cumplimiento', 'Restante'],
        values=[porcentaje, max(0, 100 - porcentaje)],
        hole=.75, marker=dict(colors=[color_linea, '#f2f2f2']),
        textinfo='none', hoverinfo='none'
    )])
    fig.update_layout(
        title=dict(text=f"<b>{titulo}</b>", x=0.5, y=0.05, xanchor='center', font=dict(size=14)),
        showlegend=False, margin=dict(t=10, b=40, l=10, r=10), height=180, width=180,
        annotations=[dict(text=f"<b>{int(porcentaje)}%</b>", x=0.5, y=0.5, font=dict(size=20), showarrow=False)]
    )
    return fig
# ==============================================================================
# SECCIÓN 6 - LECTURA EXTRACTORA XLS Y PANEL DE CONTROL DE PERSONAL
# ==============================================================================




# Declaración del control de sesión en pantalla principal
if st.session_state["usuario_rol"] is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background-color: #f8f9fa; border: 1px solid #D2D3D5; border-radius: 8px; padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center;">
            <h3 style="color: #111111; margin-bottom: 20px; font-family: 'Montserrat', sans-serif;">🔒 Acceso al Sistema de Control</h3>
            <p style="color: #555555; font-size: 14px; font-family: 'Questrial', sans-serif;">Por favor, ingrese sus credenciales para operar el Portal de Capital Humano.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        main_user = st.text_input("Usuario:", key="main_login_user")
        main_pass = st.text_input("Contraseña:", type="password", key="main_login_pass")
        
        if st.button("🔓 Iniciar Sesión", use_container_width=True, key="main_login_btn"):
            if main_user == "admin" and main_pass == "admin123":
                st.session_state["usuario_rol"] = "Administrador"
                st.session_state["usuario_name"] = "admin"
                st.rerun()
            elif main_user == "operador" and main_pass == "rh123":
                st.session_state["usuario_rol"] = "Operador"
                st.session_state["usuario_name"] = "operador"
                st.rerun()
            else:
                st.error("❌ Credenciales inválidas. Por favor intente de nuevo.")
                
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="slogan-resultados-container">'
        '<span class="slogan-resultados">Ingeniería que da resultados!!</span>'
        '</div>', 
        unsafe_allow_html=True
    )
    st.stop()

# Declaración actualizada de las pestañas de la aplicación
tab_reportes, tab_areas, tab_historico, tab_industria, tab_expedientes, tab_txt = st.tabs([
    "📊 Pre-Nómina y Reportes", 
    "📁 Asignación de Áreas y Personal",
    "📈 Histórico Semanal",
    "🤖 Manufactura Inteligente & Stack",
    "🎓 Expedientes & Capacitaciones",
    "⏱️ Banco TxT"
])







# ==============================================================================
# REEMPLAZA LA LÍNEA 241 CON ESTA NUEVA LISTA DE ÁREAS
# ==============================================================================
AREAS_LISTA_RAW = [
    "⚪ Sin Asignar",
    "👑 Dirección",
    "⚙️ Ingeniería",
    "🔍 Calidad",
    "📐 Doblez",
    "✂️ Corte Laser",
    "📦 Almacen",
    "📦 Embarque",
    "🎨 Pintura",
    "👥 Recursos Humanos"
]






with tab_areas:
    st.subheader("📝 Panel de Control de Plantilla y Estructura Organizacional")
    
    # 1. Cargamos de forma estricta el catálogo actual (base de datos real)
    df_db = cargar_catalogo_personal()
    
    # Aseguramos que los IDs sean texto limpio para comparar correctamente
    if not df_db.empty:
        df_db['id_empleado'] = df_db['id_empleado'].astype(str).str.strip()
    
    # 2. Procesamos las asistencias
    df_asistencias_raw = procesar_base_asistencias(ruta_carpeta)
    
    cambio_detectado = False
    
    # 3. Solo si hay asistencias nuevas, buscamos si hay gente que NO exista en la base
    if df_asistencias_raw is not None:
        empleados_nuevos = df_asistencias_raw[['#Empleado', 'Nombre del Empleado']].drop_duplicates()
        nuevos_registros = []
        
        for _, emp in empleados_nuevos.iterrows():
            id_e = str(emp['#Empleado']).strip()
            nom_e = str(emp['Nombre del Empleado']).strip()
            
            if id_e != 'nan' and id_e != '':
                # REVISIÓN CRÍTICA: ¿El ID existe en nuestra base de datos guardada?
                if id_e in df_db['id_empleado'].values:
                    # SI YA EXISTE, NO MODIFICAMOS EL ÁREA NI EL RENGLÓN.
                    # Solo actualizamos el nombre si venía vacío en el registro
                    idx = df_db[df_db['id_empleado'] == id_e].index[0]
                    if pd.isna(df_db.loc[idx, 'nombre']) or df_db.loc[idx, 'nombre'] == '':
                        df_db.loc[idx, 'nombre'] = nom_e
                        cambio_detectado = True
                else:
                    # SI ES UN ID TOTALMENTE NUEVO, se agrega al final como Sin Asignar
                    nuevos_registros.append({
                        "id_empleado": id_e, 
                        "nombre": nom_e, 
                        "area": "⚪ Sin Asignar"
                    })
                    cambio_detectado = True

        if nuevos_registros:
            df_db = pd.concat([df_db, pd.DataFrame(nuevos_registros)], ignore_index=True)
        
        if cambio_detectado:
            df_db.to_excel(ARCHIVO_PERSONAL, index=False)



    


    
    is_admin = st.session_state.get("usuario_rol") == "Administrador"
    num_rows_val = "dynamic" if is_admin else "fixed"
    
    if not is_admin:
        st.info("ℹ️ **Modo Consulta:** Solo el Administrador puede agregar o eliminar colaboradores de la lista (borrar registros).")

    df_editor = st.data_editor(
        df_db, 
        column_config={
            "id_empleado": st.column_config.TextColumn("ID Empleado", required=True, disabled=not is_admin), 
            "nombre": st.column_config.TextColumn("Nombre Completo del Colaborador", required=True, disabled=not is_admin), 
            "area": st.column_config.SelectboxColumn("Área Operativa Asignada", options=AREAS_LISTA_RAW, required=True)
        }, 
        num_rows=num_rows_val, 
        use_container_width=True, 
        key="maestro_personal_editor"
    )
    
    st.markdown("---")
    st.markdown("#### 🔒 Autorización de Cambios")
    clave_usuario = st.text_input("Ingresa la Clave de Usuario para guardar en GitHub:", type="password")
    
    if st.button("💾 Guardar Cambios ESTRUCTURALES de la Tabla y Sincronizar con GitHub"):
        if not is_admin:
            st.error("❌ Acción no autorizada. Solo el Administrador puede guardar cambios estructurales.")
        elif clave_usuario != "RHSigrama":
            st.error("❌ Clave de Autorización incorrecta. No tienes autorización.")
        else:
            try:
                # 1. Guardar archivo de forma local en el servidor de Streamlit
                df_editor.to_excel(ARCHIVO_PERSONAL, index=False)
                
                # 2. Subir de forma automática el archivo actualizado a tu Repositorio de GitHub
                if GITHUB_TOKEN:
                    # Dirección de la API oficial formateada con barras diagonales estrictas
                    url_api_personal = f"https://api.github.com/repos/jesusalbertomoraleslopez-byte/sigrama-prenomina-app/contents/{ARCHIVO_PERSONAL}"
                    
                    headers_github = {
                        "Authorization": f"token {GITHUB_TOKEN}",
                        "Accept": "application/vnd.github.v3+json",
                        "User-Agent": "Streamlit-App"
                    }

                    
                    # Obtener el SHA del archivo actual en GitHub para poder reemplazarlo
                    sha_personal = None
                    res_get = requests.get(url_api_personal, headers=headers_github, timeout=10)



                    if res_get.status_code == 200:
                        sha_personal = res_get.json().get("sha")
                    
                    with open(ARCHIVO_PERSONAL, "rb") as f:
                        contenido_bytes_personal = f.read()
                    payload_personal = {"message": "Sincronización de personal.xlsx", "content": base64.b64encode(contenido_bytes_personal).decode("utf-8")}
                    if sha_personal:
                        payload_personal["sha"] = sha_personal
                    
                    res_put = requests.put(url_api_personal, json=payload_personal, headers=headers_github, timeout=15)
                    if res_put.status_code in [200, 201]:
                        st.success("¡Catálogo sincronizado en GitHub con éxito!")
                        st.rerun()
                    else:
                        st.error(f"Error API GitHub: {res_put.status_code}")
                else:
                    st.warning("⚠️ Guardado local. Falta GITHUB_TOKEN.")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")





from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.piecharts import Pie

def generar_pdf_reporte(fecha_inicio, fecha_fin, hora_limite, ga_pct, gp_pct, aus_pct, matriz_final, columnas_dias, areas_lista):
    buffer = io.BytesIO()
    from reportlab.lib.pagesizes import letter, landscape
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    style_titulo = ParagraphStyle('Titulo', parent=styles['Heading1'], alignment=1, spaceAfter=5, fontName="Helvetica-Bold", fontSize=18)
    style_sub = ParagraphStyle('Sub', parent=styles['Normal'], alignment=1, spaceAfter=15, fontSize=10, textColor=colors.HexColor("#555555"))
    style_area = ParagraphStyle('Area', parent=styles['Heading2'], spaceBefore=12, spaceAfter=8, fontName="Helvetica-Bold", fontSize=12, textColor=colors.HexColor("#333333"))
    style_seccion = ParagraphStyle('Seccion', parent=styles['Heading3'], spaceBefore=10, spaceAfter=10, fontName="Helvetica-Bold", fontSize=11, textColor=colors.HexColor("#FF0000"))
    
    # Estilos internos para evitar textos encimados en las celdas
    style_celda_nombre = ParagraphStyle('CeldaNombre', parent=styles['Normal'], fontSize=8, fontName="Helvetica")
    style_celda_header = ParagraphStyle('CeldaHeader', parent=styles['Normal'], fontSize=8, fontName="Helvetica-Bold", textColor=colors.white, alignment=1)

    # 1. Encabezado del PDF
    story.append(Paragraph("INDUSTRIA SIGRAMA S.A. DE C.V.", style_titulo))
    story.append(Paragraph("<b>CONTROL DE PRE-NÓMINA</b>", style_sub))
    story.append(Spacer(1, 10))
    
    # 2. Bloque de Filtros del Periodo Seleccionado
    story.append(Paragraph("📌 FILTROS Y CONFIGURACIÓN DEL PERIODO", style_seccion))
    data_filtros = [
        ["Fecha de Inicio Real:", f"{fecha_inicio}", "Hora Límite de Entrada:"],
        ["Fecha de Fin Real:", f"{fecha_fin}", f"{hora_limite}"]
    ]
    t_filtros = Table(data_filtros, colWidths=[130, 200, 150, 100])
    t_filtros.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#333333")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_filtros)
    story.append(Spacer(1, 15))
    
    # 3. Dibujo de Relojes Indicadores (Dashboard Real)
    story.append(Paragraph("📊 RELOJES INDICADORES DEL DASHBOARD GLOBAL", style_seccion))
    
    tabla_relojes_datos = [[], []]
    anchos_relojes = [240, 240, 240]
    
    relojes_config = [
        {"pct": ga_pct, "tit": "Asistencia Institucional", "col": colors.HexColor("#FFA500")},
        {"pct": gp_pct, "tit": "Puntualidad Global", "col": colors.HexColor("#00A2E8")},
        {"pct": aus_pct, "tit": "Tasa Ausentismo", "col": colors.HexColor("#FF0000")}
    ]
    
    for r in relojes_config:
        d = Drawing(160, 100)
        pc = Pie()
        pc.x = 40
        pc.y = 10
        pc.width = 80
        pc.height = 80
        pc.data = [r["pct"], max(0.1, 100 - r["pct"])]
        pc.slices[0].fillColor = r["col"]
        pc.slices[1].fillColor = colors.HexColor("#EAEAEA")
        d.add(pc)
        d.add(String(80, 42, f"{int(r['pct'])}%", textAnchor='middle', fontName='Helvetica-Bold', fontSize=14))
        
        tabla_relojes_datos[0].append(d)
        tabla_relojes_datos[1].append(Paragraph(f"<b>{r['tit']}</b>", ParagraphStyle('Tc', alignment=1, fontSize=10)))
        
    t_relojes = Table(tabla_relojes_datos, colWidths=anchos_relojes)
    t_relojes.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,1), (-1,1), 10),
    ]))
    story.append(t_relojes)
    story.append(Spacer(1, 15))
    
    # 4. Tablas Separadas por Área Operativa con Columna BONO
    story.append(Paragraph("🏭 DESGLOSE ESTRUCTURADO POR ÁREA OPERATIVA", style_seccion))
    
    columnas_encabezado = ['#Empleado', 'Nombre del Colaborador'] + columnas_dias + ['PUNTUALIDAD', 'ASISTENCIA', 'BONO']
    
    cant_dias = len(columnas_dias)
    ancho_id = 55
    ancho_nombre = 170
    ancho_metrica = 75
    ancho_bono = 65  
    ancho_dia_celda = max(20, (720 - ancho_id - ancho_nombre - (ancho_metrica * 2) - ancho_bono) / cant_dias)
    
    ancho_columnas = [ancho_id, ancho_nombre] + [ancho_dia_celda] * cant_dias + [ancho_metrica, ancho_metrica, ancho_bono]
    
    for ar in areas_lista:
        # CORRECCIÓN CLAVE: Buscamos el área usando 'ar' directamente con su ícono para que coincida con el DataFrame
        df_area = matriz_final[matriz_final['area'] == ar]
        if df_area.empty:
            continue
            
        # Imprimimos el título de la sección mostrando el ícono completo en el PDF
        story.append(Paragraph(f"📌 Área Operativa: {ar}", style_area))
        
        # Estructuramos los encabezados de la tabla de forma segura
        encabezados_parrafos = [Paragraph(f"<b>{col}</b>", style_celda_header) for col in columnas_encabezado]
        tabla_datos = [encabezados_parrafos]
        
        for _, fila in df_area.iterrows():
            fila_valores = []
            fila_valores.append(str(fila['#Empleado']))
            
            # Formateamos el nombre como un párrafo para evitar que se encime con otras columnas
            fila_valores.append(Paragraph(str(fila['Nombre del Empleado']), style_celda_nombre))
            
            lista_asistencias_dias = []
            for d_str in columnas_dias:
                valor_dia = str(fila[d_str]) if pd.notna(fila[d_str]) else "-"
                fila_valores.append(valor_dia)
                lista_asistencias_dias.append(valor_dia)
                
            fila_valores.append(str(fila['PUNTUALIDAD']))
            fila_valores.append(str(fila['ASISTENCIA']))
            
            # Cálculo automático del Bono
            faltas = lista_asistencias_dias.count("F")
            retardos = lista_asistencias_dias.count("R")
            
            if faltas > 0:
                porcentaje_bono = "40%"
            elif retardos > 0:
                porcentaje_bono = "70%"
            else:
                porcentaje_bono = "100%"
                
            fila_valores.append(porcentaje_bono)
            tabla_datos.append(fila_valores)
            
        t_area = Table(tabla_datos, colWidths=ancho_columnas, repeatRows=1)
        
        estilos_celdas = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#FF0000")),
            ('ALIGN', (0,0), (0,-1), 'CENTER'),
            ('ALIGN', (1,0), (1,-1), 'LEFT'),
            ('ALIGN', (2,0), (-1,-1), 'CENTER'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D3D3D3")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]
        
        for r_idx in range(1, len(tabla_datos)):
            for c_idx in range(2, 2 + cant_dias):
                valor_celda = tabla_datos[r_idx][c_idx]
                if valor_celda in ["A", "R"]:
                    estilos_celdas.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor("#D4EDDA")))
                    estilos_celdas.append(('TEXTCOLOR', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor("#155724")))
                elif valor_celda == "F":
                    estilos_celdas.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor("#F8D7DA")))
                    estilos_celdas.append(('TEXTCOLOR', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor("#721C24")))
                elif valor_celda in ["S", "D"]:
                    estilos_celdas.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor("#FFF3CD")))
                    estilos_celdas.append(('TEXTCOLOR', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor("#856404")))

        t_area.setStyle(TableStyle(estilos_celdas))
        story.append(t_area)
        story.append(Spacer(1, 10))
        
    doc.build(story)
    buffer.seek(0)
    return buffer






# ==============================================================================
# SECCIÓN 7 - PIVOTACIÓN DE INCIDENCIAS Y MATRIZ DE CRUCE DE ÁREAS
# ==============================================================================
with tab_reportes:
    if os.path.exists(ruta_carpeta):
        df_raw = procesar_base_asistencias(ruta_carpeta)
        if df_raw is not None:
            df_raw['util_hora'] = df_raw['Hora Entrada Raw'].apply(limpiar_registro_hora)
            lista_dias = []
            curr = fecha_inicio
            while curr <= fecha_fin:
                lista_dias.append(curr)
                curr += timedelta(days=1)
                
            codigos = []
            for _, fila in df_raw.iterrows():
                nave = str(fila.get('Nave Entrada', '')).strip().upper()
                if "FALTA" in nave or pd.isna(fila['util_hora']): codigos.append("F")
                elif fila['util_hora'] > hora_limite_input: codigos.append("R")
                else: codigos.append("A")
                
            df_raw['Cod_Incidencia'] = codigos
            df_raw['Dia_Num'] = pd.to_datetime(df_raw['Fecha_Clean']).dt.day
            df_raw['Fecha_date'] = pd.to_datetime(df_raw['Fecha_Clean'], errors='coerce').dt.date
            df_raw_filtrado = df_raw[(df_raw['Fecha_date'] >= fecha_inicio) & (df_raw['Fecha_date'] <= fecha_fin)]
            columnas_dias_str = [str(d.day) for d in lista_dias]
            
            if df_raw_filtrado.empty:
                st.info("💡 **Aviso del Sistema:** No se encontraron asistencias en el rango de fechas seleccionado.")
            else:
                # Pivotar agrupando únicamente por #Empleado para evitar duplicación de filas por variación de nombres
                matriz = df_raw_filtrado.pivot_table(
                    index='#Empleado', 
                    columns='Dia_Num', 
                    values='Cod_Incidencia', 
                    aggfunc=lambda x: 'A' if 'A' in list(x) else ('R' if 'R' in list(x) else 'F')
                )
                for col_dia in [d.day for d in lista_dias]:
                    if col_dia not in matriz.columns: matriz[col_dia] = None
                matriz = matriz[[d.day for d in lista_dias]]
                matriz_final = matriz.copy().reset_index()
                matriz_final['#Empleado'] = matriz_final['#Empleado'].astype(str).str.strip()
                
                # Obtener catálogo de personal oficial para asociar Nombre y Área
                df_personal_cat = cargar_catalogo_personal()[['id_empleado', 'nombre', 'area']]
                df_personal_cat['id_empleado'] = df_personal_cat['id_empleado'].astype(str).str.strip()
                
                # Nombres de respaldo de las lecturas si no están en el catálogo
                nombres_fallback = df_raw_filtrado.groupby('#Empleado')['Nombre del Empleado'].last().to_dict()
                
                # Unir con el catálogo oficial
                matriz_final = matriz_final.merge(df_personal_cat, left_on='#Empleado', right_on='id_empleado', how='left')
                
                # Si el nombre viene nulo (colaborador no registrado en catálogo), usar nombre de respaldo
                matriz_final['Nombre del Empleado'] = matriz_final.apply(
                    lambda r: r['nombre'] if (pd.notna(r['nombre']) and str(r['nombre']).strip() != "") else nombres_fallback.get(r['#Empleado'], f"Empleado {r['#Empleado']}"), 
                    axis=1
                )
                
                for d in lista_dias:
                    num_dia = d.day
                    if d.weekday() == 5: matriz_final[num_dia] = matriz_final[num_dia].fillna("S")
                    elif d.weekday() == 6: matriz_final[num_dia] = matriz_final[num_dia].fillna("D")
                    else: matriz_final[num_dia] = matriz_final[num_dia].fillna("F")
                    
                puntualidades, asistencias, desempenos = [], [], []
                global_f, global_r, global_a = 0, 0, 0
                for idx, fila in matriz_final.iterrows():
                    record_dias = [fila[d.day] for d in lista_dias]
                    dias_laborables = len([r for r in record_dias if r not in ["S", "D"]])
                    f, r, a = record_dias.count("F"), record_dias.count("R"), record_dias.count("A")
                    global_f += f; global_r += r; global_a += a
                    asistencias.append(f"{((dias_laborables - f) / dias_laborables * 100) if dias_laborables > 0 else 0:.0f}%")
                    puntualidades.append(f"{(a / (a + r) * 100) if (a + r) > 0 else 0:.0f}%")
                    desempenos.append("40%" if f > 0 else ("70%" if r > 0 else "100%"))
                    
                matriz_final['PUNTUALIDAD'] = puntualidades
                matriz_final['ASISTENCIA'] = asistencias
                matriz_final['DESEMPEÑO'] = desempenos
                matriz_final.columns = [str(c) for c in matriz_final.columns]
                
                # Limpiamos los espacios en blanco del área
                matriz_final['area'] = matriz_final['area'].fillna("⚪ Sin Asignar").astype(str).str.strip()
        
                # Diccionario de equivalencias automáticas para corregir acentos o emojis mal puestos
                equivalencias_areas = {
                    "Sin Asignar": "⚪ Sin Asignar",
                    "Dirección": "👑 Dirección",
                    "Direccion": "👑 Dirección",
                    "Ingeniería": "⚙️ Ingeniería",
                    "Ingenieria": "⚙️ Ingeniería",
                    "Calidad": "🔍 Calidad",
                    "Doblez": "📐 Doblez",
                    "Corte": "✂️ Corte Laser",
                    "Almacen": "📦 Almacen",
                    "Embarque": "📦 Embarque",
                    "Pintura": "🎨 Pintura",
                    "Recursos Humanos": "👥 Recursos Humanos"
                }
        
                # Corregimos el texto buscando palabras clave para que siempre aparezca el emoji correcto
                for area_llave, area_oficial in equivalencias_areas.items():
                    matriz_final.loc[matriz_final['area'].str.contains(area_llave, case=False, na=False), 'area'] = area_oficial




                


                
                    
                st.subheader("📊 Dashboard Global de Asistencias e Incidencias")
                gt = global_a + global_r + global_f
                ga_pct = (((gt - global_f) / gt * 100) if gt > 0 else 0)
                gp_pct = ((global_a / (global_a + global_f + global_r) * 100) if (global_a + global_f + global_r) > 0 else 0)
                
                col_d1, col_d2, col_d3, col_d4 = st.columns(4)
                with col_d1: st.plotly_chart(dibujar_reloj_donut(ga_pct, "Asistencia Institucional", "#ffa500"), use_container_width=False)
                with col_d2: st.plotly_chart(dibujar_reloj_donut(gp_pct, "Puntualidad Global", "#00a2e8"), use_container_width=False)
                with col_d3: st.plotly_chart(dibujar_reloj_donut(max(0, 100 - ga_pct), "Tasa Ausentismo", "#ff0000"), use_container_width=False)
                with col_d4:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.metric("Total Colaboradores", f"{len(matriz_final)} Activos")
                    st.metric("Inasistencias Quincena", f"{global_f} Faltas")
                    
                st.write("---")
                st.subheader("🏭 Desglose Estructurado y Matrices por Área Operativa")
# ==============================================================================
# SECCIÓN 8 (PARTE 1) - CONFIGURACIÓN DE FORMATOS DE EXCEL
# ==============================================================================
                buffer_excel = io.BytesIO()
                with pd.ExcelWriter(buffer_excel, engine='xlsxwriter') as writer:
                    workbook = writer.book
                    
                    # Formatos de Celda Base
                    fmt_header = workbook.add_format({'bold': True, 'font_name': 'Arial', 'font_size': 10, 'bg_color': '#FFFFFF', 'color': '#000000', 'border': 1, 'border_color': '#FF0000', 'align': 'center', 'valign': 'vcenter'})
                    fmt_data = workbook.add_format({'font_name': 'Arial', 'font_size': 10, 'border': 1, 'border_color': '#FF0000', 'align': 'left', 'valign': 'vcenter'})
                    fmt_data_center = workbook.add_format({'font_name': 'Arial', 'font_size': 10, 'border': 1, 'border_color': '#FF0000', 'align': 'center', 'valign': 'vcenter'})
                    
                    # Formatos con Código de Color para Incidencias
                    fmt_celda_a = workbook.add_format({'bg_color': '#d4edda', 'color': '#155724', 'bold': True, 'border': 1, 'border_color': '#FF0000', 'align': 'center'})
                    fmt_celda_f = workbook.add_format({'bg_color': '#f8d7da', 'color': '#721c24', 'bold': True, 'border': 1, 'border_color': '#FF0000', 'align': 'center'})
                    fmt_celda_sd = workbook.add_format({'bg_color': '#fff3cd', 'color': '#856404', 'bold': True, 'border': 1, 'border_color': '#FF0000', 'align': 'center'})
                    
                    # Formatos de Encabezados Oficiales e Identidad Documental
                    fmt_meta_title = workbook.add_format({'bold': True, 'font_name': 'Arial', 'font_size': 16, 'align': 'center'})
                    fmt_meta_code = workbook.add_format({'bold': True, 'font_name': 'Arial', 'font_size': 11, 'color': '#FF0000'})
                    fmt_meta_sub = workbook.add_format({'font_name': 'Arial', 'font_size': 9, 'color': '#555555'})
                    fmt_fecha_titulo = workbook.add_format({'bold': True, 'font_name': 'Arial', 'font_size': 11})
                    
                    cols_mostrar = ['#Empleado', 'Nombre del Empleado'] + columnas_dias_str + ['PUNTUALIDAD', 'ASISTENCIA', 'DESEMPEÑO']
                    
                    # Preparación de hojas: Consolidado General + Una hoja independiente por cada área operativa
                    lista_hojas_excel = [('CONSOLIDADO', matriz_final)] + [
                        (ar.replace("👑 ", "").replace("⚙️ ", "").replace("🔍 ", "").replace("📐 ", "").replace("✂️ ", "").replace("🎨 ", "").replace("📦 ", "").replace("⚪ ", "")[:31], 
                         matriz_final[matriz_final['area'] == ar]) for ar in AREAS_LISTA_RAW
                    ]
# ==============================================================================
# SECCIÓN 8 (PARTE 2) - ESCRITURA DINÁMICA DE REGISTROS POR HOJA
# ==============================================================================
                    for nombre_hoja, df_hoja in lista_hojas_excel:
                        if df_hoja.empty: 
                            continue
                            
                        fila_inicio_datos = 4
                        df_hoja[cols_mostrar].to_excel(writer, sheet_name=nombre_hoja, index=False, startrow=3)
                        ws = writer.sheets[nombre_hoja]
                        
                        # Dimensionamiento de Filas y Columnas Oficiales
                        ws.set_row(0, 18); ws.set_row(1, 15); ws.set_row(2, 15); ws.set_row(3, 22)
                        ws.set_column('A:A', 12); ws.set_column('B:B', 35); ws.set_column('C:R', 4); ws.set_column('S:V', 14)
                        
                        # Encabezado del Formato Oficial de Calidad
                        ws.write('A1', 'PRE-NÓMINA', fmt_meta_code)
                        ws.write('A2', 'Revisión 01', fmt_meta_sub)
                        ws.write('A3', '25 de mayo 2020', fmt_meta_sub)
                        ws.merge_range('D1:N2', 'PRE-NÓMINA', fmt_meta_title)
                        ws.write('A4', f'PRENÓMINA AL {fecha_fin.strftime("%d DE %B DE %Y").upper()}', fmt_fecha_titulo)
                        
                        encabezados_oficiales = ["#Empleado", "Nombre del Empleado"] + columnas_dias_str + ["TE", "PUNTUALIDAD", "ASISTENCIA", "DESEMPEÑO"]
                        for col_num, header_text in enumerate(encabezados_oficiales): 
                            ws.write(fila_inicio_datos, col_num, header_text, fmt_header)
                            
                        # Volcado con Estilos Condicionales aplicados al Libro
                        for idx_fila in range(len(df_hoja)):
                            fila_excel = fila_inicio_datos + 1 + idx_fila
                            ws.set_row(fila_excel, 20)
                            ws.write(fila_excel, 0, df_hoja.iloc[idx_fila]['#Empleado'], fmt_data_center)
                            ws.write(fila_excel, 1, df_hoja.iloc[idx_fila]['Nombre del Empleado'], fmt_data)
                            
                            for idx_dia, dia_str in enumerate(columnas_dias_str):
                                col_excel = 2 + idx_dia
                                valor_dia = df_hoja.iloc[idx_fila][dia_str]
                                if valor_dia in ["A", "R"]: 
                                    ws.write(fila_excel, col_excel, valor_dia, fmt_celda_a)
                                elif valor_dia == "F": 
                                    ws.write(fila_excel, col_excel, valor_dia, fmt_celda_f)
                                elif valor_dia in ["S", "D"]: 
                                    ws.write(fila_excel, col_excel, valor_dia, fmt_celda_sd)
                                else: 
                                    ws.write(fila_excel, col_excel, valor_dia, fmt_data_center)
                                    
                            ws.write(fila_excel, 2 + len(columnas_dias_str), "", fmt_data_center) # Celda para "Tiempo Extra (TE)"
                            ws.write(fila_excel, 3 + len(columnas_dias_str), df_hoja.iloc[idx_fila]['PUNTUALIDAD'], fmt_data_center)
                            ws.write(fila_excel, 4 + len(columnas_dias_str), df_hoja.iloc[idx_fila]['ASISTENCIA'], fmt_data_center)
                            ws.write(fila_excel, 5 + len(columnas_dias_str), df_hoja.iloc[idx_fila]['DESEMPEÑO'], fmt_data_center)
                            
# ==============================================================================
# SECCIÓN 8 (PARTE 3) - RECUADROS TOTALMENTE SEPARADOS SIN COLISIÓN
# ==============================================================================
                            # Dejamos 2 renglones de espacio después del último empleado
                            fila_obs = fila_inicio_datos + len(df_hoja) + 2
                            
                            # NOTA: Escribimos en texto plano en la Columna B (columna 1) sin combinar celdas
                            # Esto evita al 100% que XlsxWriter arroje OverlappingRange
                            ws.write(fila_obs, 1, " OBSERVACIONES: ", workbook.add_format({'bold': True, 'font_name': 'Arial', 'font_size': 9, 'color': '#FF0000'}))
                            
                            # Glosario Reglamentario de Incidencias en renglones independientes en la columna B
                            fila_firmas = fila_obs + 4
                            ws.write(fila_firmas, 1, "ASISTENCIA= A | TIEMPO EXTRA= TE | TRABAJO FORANEO= TF | PERMISO= P", workbook.add_format({'font_name': 'Arial', 'font_size': 9, 'bold': True}))
                            ws.write(fila_firmas + 1, 1, "FALTA= F | VACACIONES= V | INCAPACIDAD= I | SÁBADO= S | DOMINGO= D", workbook.add_format({'font_name': 'Arial', 'font_size': 9, 'bold': True}))
                            ws.write(fila_firmas + 2, 1, "NO LABORABLE CONVENIO= NLC | DÍA FESTIVO LABORADO= DFL | DIA DE DESCANSO LABORADO= DDL", workbook.add_format({'font_name': 'Arial', 'font_size': 9, 'bold': True}))
                            
                            # Formatos limpios para las Firmas Autorizadas
                            fmt_linea_firma = workbook.add_format({'top': 1, 'top_color': '#000000', 'align': 'center', 'font_name': 'Arial', 'font_size': 9, 'bold': True})
                            fmt_texto_firma = workbook.add_format({'align': 'center', 'font_name': 'Arial', 'font_size': 9, 'bold': True})
                            
                            # Espacio para Firmas Oficiales de forma segura
                            # Firma Director General colocada limpiamente en la columna B (Nombre)
                            ws.write_blank(fila_firmas + 6, 1, fmt_linea_firma)
                            ws.write(fila_firmas + 7, 1, "FIRMA DIRECTOR GENERAL", fmt_texto_firma)
                            
                            # Firma Gerente de Área colocada limpiamente en la columna S (Métricas)
                            ws.write_blank(fila_firmas + 6, 19, fmt_linea_firma)
                            ws.write(fila_firmas + 7, 19, "FIRMA GERENTE DE ÁREA", fmt_texto_firma)
                            
                            # Pie de Página de Protección Intelectual de Industria Sigrama
                            ws.write(fila_firmas + 10, 0, "FO-SGC-02 PROHIBIDA LA REPRODUCCIÓN TOTAL O PARCIAL, SIN AUTORIZACIÓN POR ESCRITO DE INDUSTRIA SIGRAMA S.A. DE C.V.", workbook.add_format({'font_name': 'Arial', 'font_size': 8, 'italic': True, 'color': '#777777'}))

                # Renderizado de Tablas Desglosadas por Área en la Interfaz de la Aplicación (UI)
                for ar in AREAS_LISTA_RAW:
                    df_area_actual = matriz_final[matriz_final['area'] == ar]
                    if not df_area_actual.empty:
                        conteo_flat_area = df_area_actual[columnas_dias_str].values.flatten()
                        c_a = list(conteo_flat_area).count("A")
                        c_r = list(conteo_flat_area).count("R")
                        c_f = list(conteo_flat_area).count("F")
                        area_total_dias = c_a + c_r + c_f
                        
                        st.markdown(f"#### {ar}")
                        st.markdown(f"**Factor Asistencia de la Celda:** `{((area_total_dias - c_f) / area_total_dias * 100) if area_total_dias > 0 else 0:.1f}%` | **Puntualidad:** `{((c_a / (c_a + c_r) * 100) if (c_a + c_r) > 0 else 0):.1f}%`")
                        st.dataframe(df_area_actual[cols_mostrar].style.map(aplicar_colores_matriz, subset=columnas_dias_str), use_container_width=True)

                # Sección Final de Descarga de los Reportes divididos
                st.markdown("---")
                st.subheader("📥 Guardar Libro de Pre-Nómina por Áreas")
                st.download_button(
                    label="📄 Descargar Reporte Dividido por Áreas (.xlsx)", 
                    data=buffer_excel.getvalue(), 
                    file_name=f"PRENOMINA_POR_AREAS_{fecha_fin.strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                # Generar el archivo PDF en memoria

                # 1. Ejecuta la función mejorada pasando las variables de control y horas
                pdf_data = generar_pdf_reporte(
                    fecha_inicio=fecha_inicio.strftime('%d/%m/%Y'),
                    fecha_fin=fecha_fin.strftime('%d/%m/%Y'),
                    hora_limite=hora_limite_input.strftime('%H:%M:%S'),
                    ga_pct=ga_pct,
                    gp_pct=gp_pct,
                    aus_pct=max(0, 100 - ga_pct),
                    matriz_final=matriz_final,
                    columnas_dias=columnas_dias_str,
                    areas_lista=AREAS_LISTA_RAW
                )

                # 2. Botón interactivo en la pantalla principal
                st.download_button(
                    label="📄 Descargar Reporte de Pre-Nómina en PDF",
                    data=pdf_data,
                    file_name=f"PRENOMINA_{fecha_fin.strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )


# ==============================================================================
# SECCIÓN - HISTÓRICO SEMANAL (CÁLCULO, REGISTRO Y GRÁFICAS)
# ==============================================================================



# ==============================================================================
# SECCIÓN - HISTÓRICO SEMANAL (CÁLCULO, REGISTRO Y GRÁFICAS ESTILO EXCEL)
# ==============================================================================




with tab_historico:
    st.subheader("📈 Histórico General por Semana")
    st.write("Resumen consolidado de indicadores clave de la empresa.")


    # Cálculo automático e inmediato de todos los periodos registrados en los archivos XLS
    df_hist = recalcular_historico_completo(ruta_carpeta, ARCHIVO_PERSONAL, hora_limite_input)

    if not df_hist.empty:
        try:
            df_hist.to_excel(ARCHIVO_HISTORICO, index=False)
            st.success("✅ **Sincronización automática activa:** Los indicadores semanales se calculan dinámicamente y se respaldan en `asistencias/historico_semanal.xlsx`.")
        except Exception as e:
            st.warning(f"⚠️ Historial calculado, pero no se pudo guardar en archivo: {e}")
    else:
        st.info("La tabla histórica está vacía. No se encontraron archivos de asistencias para calcular.")

    st.markdown("---")
    if not df_hist.empty:
        df_visual_tabla = df_hist.copy()
        
        # Saca promedios numéricos limpios separando el porcentaje del detalle
        asist_num = df_visual_tabla['Asistencia'].str.split('%').str[0].astype(float)
        punt_num = df_visual_tabla['Puntualidad'].str.split('%').str[0].astype(float)
        ausen_num = df_visual_tabla['Tasa de Ausencia'].str.split('%').str[0].astype(float)
        
        promedio_asist_val = round(asist_num.mean())
        promedio_punt_val = round(punt_num.mean())
        promedio_ausen_val = round(ausen_num.mean())
        
        fila_promedio = pd.DataFrame([{
            "Semana": "PROMEDIO",
            "Fecha Inicio": "",
            "Fecha Fin": "",
            "Asistencia": f"{promedio_asist_val}%",
            "Puntualidad": f"{promedio_punt_val}%",
            "Tasa de Ausencia": f"{promedio_ausen_val}%"
        }])
        
        df_visual_tabla = pd.concat([df_visual_tabla, fila_promedio], ignore_index=True)
        st.dataframe(df_visual_tabla, use_container_width=True, hide_index=True)

        # ==============================================================================
        # SECCIÓN HISTÓRICO - PARTE 3: MOTOR DE PDF PREMIUM Y BOTÓN
        # ==============================================================================
        def generar_pdf_historico_premium(dataframe_final, v_asist, v_punt, v_ausen):
            import io
            import math
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.graphics.shapes import Drawing, Circle, Line, String, Polygon
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            story = []
            styles = getSampleStyleSheet()
            
            # A. ENCABEZADO: BANNER CORPORATIVO (Proporción exacta 2000x450 -> Alto 124)
            ruta_banner = "RH BANNER APP.png"
            if os.path.exists(ruta_banner):
                try:
                    story.append(RLImage(ruta_banner, width=550, height=124))
                    story.append(Spacer(1, 10))
                except Exception:
                    pass
            
            # B. TÍTULOS DE PLANTA METALES
            titulo_estilo = ParagraphStyle(
                'TituloPlanta', parent=styles['Heading1'], fontSize=22, leading=26,
                textColor=colors.HexColor('#2E4053'), alignment=1, spaceAfter=4
            )
            sub_estilo = ParagraphStyle(
                'SubPlanta', fontSize=11, textColor=colors.HexColor('#566573'),
                alignment=1, spaceAfter=15
            )
            
            story.append(Paragraph("PLANTA METALES SIGRAMA", titulo_estilo))
            story.append(Paragraph("<b>Reporte Histórico de Indicadores Semanales</b>", sub_estilo))
            
            # C. TABLA CON FILA PROMEDIO ESTILIZADA
            encabezados = [["Semana", "Fecha Inicio", "Fecha Fin", "Asistencia", "Puntualidad", "Tasa de Ausencia"]]
            cuerpo_tabla = dataframe_final.values.tolist()
            tabla_datos = encabezados + cuerpo_tabla
            
            t = Table(tabla_datos, colWidths=[80, 85, 85, 95, 95, 110])
            estilo_tabla = TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E4053')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
            ])
            
            total_filas = len(tabla_datos) - 1
            estilo_tabla.add('FONTNAME', (0, total_filas), (-1, total_filas), 'Helvetica-Bold')
            estilo_tabla.add('BACKGROUND', (0, total_filas), (-1, total_filas), colors.HexColor('#EAEDED'))
            estilo_tabla.add('TEXTCOLOR', (0, total_filas), (-1, total_filas), colors.HexColor('#2C3E50'))
            
            t.setStyle(estilo_tabla)
            story.append(t)
            story.append(Spacer(1, 20))
            
            # D. CONSTRUCCIÓN DE CANVAS GRÁFICO PARA LOS 3 RELOJES HORIZONTALES
            story.append(Paragraph("<b>Paneles de Control de Rendimiento Histórico Promedio</b>", ParagraphStyle('Lbl', alignment=1, fontSize=12, textColor=colors.HexColor('#2C3E50'))))
            story.append(Spacer(1, 10))
            
            d = Drawing(550, 110)
            
            relojes_config = [
                {"cx": 90,  "val": v_asist, "titulo": "Asistencia", "color_txt": "#1E8449", "invertido": False},
                {"cx": 275, "val": v_punt,  "titulo": "Puntualidad", "color_txt": "#2471A3", "invertido": False},
                {"cx": 460, "val": v_ausen, "titulo": "Ausentismo", "color_txt": "#922B21", "invertido": True}
            ]
            
            r = 75  
            cy = 15 
            
            for conf in relojes_config:
                cx = conf["cx"]
                val = max(0, min(100, conf["val"]))
                
                c_bueno = colors.HexColor('#D5F5E3') if not conf["invertido"] else colors.HexColor('#FADBD8')
                c_malo = colors.HexColor('#FADBD8') if not conf["invertido"] else colors.HexColor('#D5F5E3')
                c_regular = colors.HexColor('#FCF3CF')
                
                d.add(Polygon([cx-r, cy, cx-(r*0.8), cy+(r*0.6), cx, cy], fillColor=c_malo, strokeColor=None))
                d.add(Polygon([cx-(r*0.8), cy+(r*0.6), cx, cy+r, cx+(r*0.5), cy+(r*0.86), cx, cy], fillColor=c_regular, strokeColor=None))
                d.add(Polygon([cx+(r*0.5), cy+(r*0.86), cx+r, cy, cx, cy], fillColor=c_bueno, strokeColor=None))
                
                d.add(Line(cx-r, cy, cx+r, cy, strokeColor=colors.HexColor('#7F8C8D'), strokeWidth=1.5))
                
                angulo_rad = math.radians(180 - (val * 1.8))
                ax = cx + (r - 10) * math.cos(angulo_rad)
                ay = cy + (r - 10) * math.sin(angulo_rad)
                
                d.add(Line(cx, cy, ax, ay, strokeColor=colors.HexColor('#2C3E50'), strokeWidth=3))
                d.add(Circle(cx, cy, 6, fillColor=colors.HexColor('#34495E'), strokeColor=colors.white, strokeWidth=1))
                
                d.add(String(cx - r - 12, cy + 3, "0%", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#7F8C8D')))
                d.add(String(cx + r + 3, cy + 3, "100%", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#7F8C8D')))
                
                d.add(String(cx - 18, cy + 18, f"{val}%", fontName="Helvetica-Bold", fontSize=14, fillColor=colors.HexColor(conf["color_txt"])))
                d.add(String(cx - 30, cy + r + 8, conf["titulo"], fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor('#34495E')))
            
            story.append(d)
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
        
        # --- INTERFAZ: BOTÓN DE DESCARGA ---
        pdf_data = generar_pdf_historico_premium(df_visual_tabla, promedio_asist_val, promedio_punt_val, promedio_ausen_val)
        
        st.download_button(
            label="📄 Descargar Reporte Premium Planta Metales en PDF",
            data=pdf_data,
            file_name="Reporte_Historico_Metales_Sigrama.pdf",
            mime="application/pdf"
        )
        
        # --- SEGUNDO NIVEL: DETALLE DIARIO DESPLEGABLE POR SEMANA ---
        st.markdown("---")
        st.subheader("🔍 Desglose Diario por Semana (Menú Desplegable)")
        st.write("Expande una semana para ver la asistencia diaria detallada de los colaboradores contratados.")
        
        df_personal = cargar_catalogo_personal()
        df_personal['id_empleado'] = df_personal['id_empleado'].astype(str).str.strip()
        employees_cat = df_personal[['id_empleado', 'nombre', 'area']].dropna(subset=['id_empleado'])
        
        df_m = procesar_base_asistencias(ruta_carpeta)
        if df_m is not None and not df_m.empty:
            df_m['util_hora'] = df_m['Hora Entrada Raw'].apply(limpiar_registro_hora)
            codigos_w = []
            for _, fila in df_m.iterrows():
                nave = str(fila.get('Nave Entrada', '')).strip().upper()
                if "FALTA" in nave or pd.isna(fila['util_hora']): codigos_w.append("F")
                elif fila['util_hora'] > hora_limite_input: codigos_w.append("R")
                else: codigos_w.append("A")
            df_m['Cod_Incidencia'] = codigos_w
            df_m['Fecha_Clean'] = pd.to_datetime(df_m['Fecha_Clean']).dt.date
            
            # Mapeamos primeras fechas de reloj
            primeros_ingresos = (
                df_m.dropna(subset=['Fecha_Clean'])
                .groupby('#Empleado')['Fecha_Clean']
                .min()
                .to_dict()
            )
            unique_dates = sorted(df_m['Fecha_Clean'].dropna().unique())
            
            # Agrupamos por semana ISO
            semanas_agrupadas = {}
            for d in unique_dates:
                if d.weekday() <= 4: # Lunes a Viernes
                    year, week_num, weekday = d.isocalendar()
                    week_key = (year, week_num)
                    if week_key not in semanas_agrupadas:
                        semanas_agrupadas[week_key] = []
                    semanas_agrupadas[week_key].append(d)
                    
            for k, v in sorted(semanas_agrupadas.items(), reverse=True):
                semana_nombre = f"Semana {k[1]}"
                v_sorted = sorted(v)
                f_ini_str = v_sorted[0].strftime("%d-%b-%y").lower()
                f_fin_str = v_sorted[-1].strftime("%d-%b-%y").lower()
                
                with st.expander(f"📅 {semana_nombre} ({f_ini_str} al {f_fin_str})"):
                    # Construimos la matriz diaria para esta semana
                    df_week_raw = df_m[df_m['Fecha_Clean'].isin(v)]
                    
                    if not df_week_raw.empty:
                        # Pivot table agrupando únicamente por #Empleado
                        matriz_semana = df_week_raw.pivot_table(
                            index='#Empleado', 
                            columns='Fecha_Clean', 
                            values='Cod_Incidencia', 
                            aggfunc=lambda x: 'A' if 'A' in list(x) else ('R' if 'R' in list(x) else 'F')
                        )
                        
                        # Nos aseguramos de incluir todas las fechas activas de la semana como columnas
                        for col_fecha in v:
                            if col_fecha not in matriz_semana.columns:
                                matriz_semana[col_fecha] = None
                                
                        matriz_semana = matriz_semana[v]
                        matriz_semana = matriz_semana.reset_index()
                        
                        # Combinamos con el catálogo de personal para traer Nombre y Área
                        matriz_semana['#Empleado'] = matriz_semana['#Empleado'].astype(str).str.strip()
                        matriz_semana = employees_cat.merge(matriz_semana, left_on='id_empleado', right_on='#Empleado', how='left')
                        
                        # Filtramos para mostrar solo colaboradores contratados hasta la fecha final de la semana
                        matriz_semana['primer_ingreso'] = matriz_semana['id_empleado'].map(primeros_ingresos)
                        # Omitimos colaboradores cuyo primer ingreso sea posterior a la semana evaluada
                        matriz_semana = matriz_semana[matriz_semana['primer_ingreso'].notna() & (matriz_semana['primer_ingreso'] <= v_sorted[-1])]
                        
                        # Rellenamos asistencias/faltas de los días laborados
                        for col_fecha in v:
                            # Si es posterior o igual a su ingreso, rellenamos con 'F' (Falta), si es previo, dejamos '-' (No contratado)
                            for idx_fila, fila_emp in matriz_semana.iterrows():
                                if pd.isna(fila_emp[col_fecha]):
                                    if col_fecha >= fila_emp['primer_ingreso']:
                                        matriz_semana.at[idx_fila, col_fecha] = "F"
                                    else:
                                        matriz_semana.at[idx_fila, col_fecha] = "-"
                        
                        # Renombramos columnas de fecha a string legible (ej. "Lun 18", "Mar 19")
                        nom_columnas = {
                            "id_empleado": "ID Empleado",
                            "nombre": "Colaborador",
                            "area": "Área"
                        }
                        dias_map = {0: "Lun", 1: "Mar", 2: "Mié", 3: "Jue", 4: "Vie", 5: "Sáb", 6: "Dom"}
                        for col_fecha in v:
                            dia_nombre = dias_map.get(col_fecha.weekday(), "")
                            nom_columnas[col_fecha] = f"{dia_nombre} {col_fecha.day}"
                            
                        # Columnas finales a mostrar
                        columnas_str_fechas = [nom_columnas[col_fecha] for col_fecha in v]
                        matriz_semana = matriz_semana.rename(columns=nom_columnas)
                        cols_finales = ["ID Empleado", "Colaborador", "Área"] + columnas_str_fechas
                        
                        st.markdown(f"**Matriz de Asistencia de la {semana_nombre}:**")
                        st.dataframe(
                            matriz_semana[cols_finales].style.map(aplicar_colores_matriz, subset=columnas_str_fechas),
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("No hay registros de asistencia para esta semana.")
    else:
        st.info("La tabla histórica está vacía. No se encontraron archivos de asistencias para calcular.")

# ==============================================================================
# SECCIÓN - MANUFACTURA INTELIGENTE & INDUSTRIA 4.0
# ==============================================================================
with tab_industria:
    st.subheader("🤖 Manufactura Inteligente & Industria 4.0")
    st.write("Estrategia de transformación digital e innovación tecnológica en Industria Sigrama.")
    
    st.markdown("---")
    
    # 1. Justificación de Manufactura Inteligente
    st.markdown("### 💡 Justificación de Manufactura Inteligente")
    st.markdown(
        "En la era del IoT industrial y la automatización, la gestión de personal requiere flujos de información instantáneos y libres de error. "
        "Este panel automatizado digitaliza la captura de registros del reloj checador, eliminando las ineficiencias de transcripción manual, previniendo errores "
        "en los cálculos de nóminas y sentando las bases para un ecosistema transparente e interconectado de Industria 4.0 en Industria Sigrama."
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Beneficios Estratégicos
    st.markdown("### 🚀 Beneficios Estratégicos del Proyecto")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown("""
        <div style="background-color: #f8f9fa; border-left: 5px solid #EC2024; border-radius: 4px; padding: 15px; margin-bottom: 10px;">
            <strong style="color: #111111;">⚡ Eficiencia de Procesos</strong><br>
            <span style="color: #555555; font-size: 13px;">Reducción del 95% en tiempos de captura administrativa mediante consolidación automática de incidencias.</span>
        </div>
        <div style="background-color: #f8f9fa; border-left: 5px solid #EC2024; border-radius: 4px; padding: 15px; margin-bottom: 10px;">
            <strong style="color: #111111;">📈 Transparencia y Trazabilidad</strong><br>
            <span style="color: #555555; font-size: 13px;">Garantiza la inmutabilidad y auditoría de asistencia, retardos e inasistencias en cada quincena.</span>
        </div>
        """, unsafe_allow_html=True)
    with col_b2:
        st.markdown("""
        <div style="background-color: #f8f9fa; border-left: 5px solid #EC2024; border-radius: 4px; padding: 15px; margin-bottom: 10px;">
            <strong style="color: #111111;">📊 Inteligencia de Negocios</strong><br>
            <span style="color: #555555; font-size: 13px;">Dashboard interactivo global con KPIs críticos para la toma de decisiones directivas de Recursos Humanos.</span>
        </div>
        <div style="background-color: #f8f9fa; border-left: 5px solid #EC2024; border-radius: 4px; padding: 15px; margin-bottom: 10px;">
            <strong style="color: #111111;">💰 Optimización Financiera</strong><br>
            <span style="color: #555555; font-size: 13px;">Cálculo preciso del bono de puntualidad y productividad quincenal en tiempo real según incidencias reales.</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3. Resumen del Stack Tecnológico
    st.markdown("### 🛠️ Resumen del Stack Tecnológico")
    st.markdown(
        "El desarrollo del portal operativo está cimentado en tecnologías ágiles y de alto rendimiento que garantizan robustez y escalabilidad:"
    )
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown("""
        <div style="text-align: center; background-color: #f8f9fa; border: 1px solid #D2D3D5; border-radius: 6px; padding: 15px; height: 100%;">
            <span style="font-size: 24px;">🐍</span><br>
            <strong style="color: #111111;">Python Core & Pandas</strong><br>
            <span style="color: #555555; font-size: 12px;">Motores eficientes para la lectura y estructuración de matrices de tiempos y cálculo de promedios semanales.</span>
        </div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown("""
        <div style="text-align: center; background-color: #f8f9fa; border: 1px solid #D2D3D5; border-radius: 6px; padding: 15px; height: 100%;">
            <span style="font-size: 24px;">🎨</span><br>
            <strong style="color: #111111;">Streamlit & Vanilla CSS</strong><br>
            <span style="color: #555555; font-size: 12px;">Interfaz dinámica e inyección de estilos corporativos con fuentes Montserrat y Questrial para diseño responsivo.</span>
        </div>
        """, unsafe_allow_html=True)
    with col_s3:
        st.markdown("""
        <div style="text-align: center; background-color: #f8f9fa; border: 1px solid #D2D3D5; border-radius: 6px; padding: 15px; height: 100%;">
            <span style="font-size: 24px;">☁️</span><br>
            <strong style="color: #111111;">API GitHub & ReportLab</strong><br>
            <span style="color: #555555; font-size: 12px;">Sincronización automatizada de base de datos de personal y renderizado de reportes PDF oficiales listos para firma.</span>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# SECCIÓN DE CIERRE - ESLÓGANES INSTITUCIONALES Y PIE DE PÁGINA
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown(
    '<div style="text-align: center; margin-top: 30px;">'
    '<span class="slogan-resultados-sidebar">Ingeniería que da resultados!!</span>'
    '</div>', 
    unsafe_allow_html=True
)

st.markdown("---")
st.markdown(
    '<div class="slogan-resultados-container">'
    '<span class="slogan-resultados">Ingeniería que da resultados!!</span>'
    '</div>', 
    unsafe_allow_html=True
)

# ==============================================================================
# SECCIÓN EXPEDIENTES & CAPACITACIONES — MÓDULO DC-3 Y PERFIL COLABORADOR
# ==============================================================================

RUTA_ACCESS_DB = "PERSONAL.accdb"
PS32 = r"C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe"

import subprocess
import json as _json


@st.cache_data(ttl=300, show_spinner=False)
def leer_tabla_access(tabla: str) -> pd.DataFrame:
    """Lee una tabla de la base de datos Access usando PowerShell 32-bit + ACE OLEDB."""
    if not os.path.exists(PS32):
        return pd.DataFrame()
    ps_script = f"""
$conn = New-Object -ComObject ADODB.Connection
$conn.Open("Provider=Microsoft.ACE.OLEDB.16.0;Data Source={RUTA_ACCESS_DB};")
$rs = New-Object -ComObject ADODB.Recordset
$rs.Open("SELECT * FROM [{tabla}]", $conn, 1, 1)
$cols = @()
for ($i=0; $i -lt $rs.Fields.Count; $i++) {{ $cols += $rs.Fields.Item($i).Name }}
$rows = @()
while (-not $rs.EOF) {{
    $row = @{{}}
    for ($i=0; $i -lt $rs.Fields.Count; $i++) {{
        $fname = $rs.Fields.Item($i).Name
        $fval = $rs.Fields.Item($i).Value
        if ($fval -is [DateTime]) {{ $fval = $fval.ToString("yyyy-MM-dd") }}
        $row[$fname] = if ($fval -eq $null) {{ "" }} else {{ [string]$fval }}
    }}
    $rows += [PSCustomObject]$row
    $rs.MoveNext()
}}
$rs.Close()
$conn.Close()
$rows | ConvertTo-Json -Depth 3
"""
    try:
        res = subprocess.run(
            [PS32, "-Command", ps_script],
            capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=30
        )
        if not res.stdout.strip():
            return pd.DataFrame()
        raw = res.stdout.strip()
        # PowerShell returns a single object if 1 row, wrap it
        if raw.startswith("{"):
            raw = f"[{raw}]"
        datos = _json.loads(raw)
        return pd.DataFrame(datos)
    except Exception:
        return pd.DataFrame()


def _limpiar_texto(val) -> str:
    s = str(val).strip()
    return "" if s in ("None", "nan", "NULL", "") else s


with tab_expedientes:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #111111 0%, #2c2c2c 100%);
                border-radius: 12px; padding: 24px 32px; margin-bottom: 24px;">
        <h2 style="color:#FFFFFF; font-family:'Montserrat',sans-serif; margin:0;">
            🎓 Expedientes Digitales & Control de Capacitación DC-3
        </h2>
        <p style="color:#EC2024; font-family:'Questrial',sans-serif; margin:6px 0 0 0; font-size:15px;">
            Industria Sigrama S.A. de C.V. — Dirección de Capital Humano
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Verificar si la DB local existe
    db_disponible = os.path.exists(RUTA_ACCESS_DB)

    if not db_disponible:
        st.warning(
            "⚠️ **Base de datos no encontrada:** `PERSONAL.accdb` no está en la carpeta del proyecto. "
            "Por favor copia el archivo ahí para habilitar este módulo.",
            icon="⚠️"
        )
    else:
        # Carga de tablas
        with st.spinner("🔄 Cargando base de datos de Capital Humano..."):
            df_personal_acc = leer_tabla_access("PERSONAL")
            df_cursos_acc   = leer_tabla_access("CURSOS")
            df_puestos_acc  = leer_tabla_access("PUESTOS")
            df_cursos_cat   = leer_tabla_access("Cusos_Disponibles")

        if df_personal_acc.empty:
            st.error("❌ No se pudo conectar a la base de datos Access. Verifica que el motor ACE OLEDB esté instalado.")
        else:
            # ---- Limpiar datos ----
            df_personal_acc = df_personal_acc.fillna("").astype(str).applymap(str.strip)
            df_cursos_acc   = df_cursos_acc.fillna("").astype(str).applymap(str.strip)

            # ---- KPI banner superior ----
            total_emp  = len(df_personal_acc)
            total_cur  = len(df_cursos_acc)
            dc3_count  = len(df_cursos_acc[df_cursos_acc.get("DCIII", pd.Series(dtype=str)).apply(
                lambda v: str(v).strip() not in ("", "None", "nan"))])
            horas_col  = "Horas_Invertidas"
            total_hrs  = 0
            if horas_col in df_cursos_acc.columns:
                total_hrs = pd.to_numeric(df_cursos_acc[horas_col], errors="coerce").fillna(0).sum()

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("👤 Colaboradores en BD", total_emp)
            k2.metric("📚 Registros de Capacitación", total_cur)
            k3.metric("📜 Constancias DC-3", dc3_count)
            k4.metric("⏱️ Horas Totales de Capacitación", f"{int(total_hrs):,} hrs")

            st.markdown("---")

            # ====== SUB-PESTAÑAS ======
            sub_ficha, sub_cursos, sub_dashboard, sub_catalogos = st.tabs([
                "👤 Ficha del Colaborador",
                "📚 Historial de Capacitación",
                "📊 Dashboard DC-3",
                "📋 Catálogos"
            ])

            # ─────────────────────────────────────────────
            # SUB-TAB 1: FICHA DEL COLABORADOR
            # ─────────────────────────────────────────────
            with sub_ficha:
                st.subheader("👤 Expediente Digital del Colaborador")

                col_sel, col_info = st.columns([1, 2])

                with col_sel:
                    nombres_emp = df_personal_acc.get("Nombre_Empleado_Robotica",
                                                       pd.Series(dtype=str)).tolist()
                    ids_emp     = df_personal_acc.get("Numero_Control_Personal",
                                                       pd.Series(dtype=str)).tolist()
                    opciones    = [f"{nid} — {nom}" for nid, nom in zip(ids_emp, nombres_emp)]
                    sel         = st.selectbox("🔍 Selecciona un colaborador:", opciones, key="ficha_sel_emp")

                if sel:
                    idx_sel = opciones.index(sel)
                    fila    = df_personal_acc.iloc[idx_sel]

                    with col_info:
                        nombre_disp = _limpiar_texto(fila.get("Nombre_Empleado_Robotica", ""))
                        id_disp     = _limpiar_texto(fila.get("Numero_Control_Personal", ""))
                        puesto_disp = _limpiar_texto(fila.get("Puesto", ""))
                        ingreso     = _limpiar_texto(fila.get("Fecha_de_Ingreso", ""))

                        st.markdown(f"""
                        <div style="background:#f8f9fa; border-left: 4px solid #EC2024;
                                    border-radius: 8px; padding: 20px; margin-bottom: 16px;">
                            <h3 style="color:#111111; margin:0 0 4px 0; font-family:'Montserrat',sans-serif;">
                                {nombre_disp}
                            </h3>
                            <p style="color:#EC2024; font-weight:bold; margin:0 0 8px 0;">
                                ID: {id_disp} &nbsp;|&nbsp; {puesto_disp}
                            </p>
                            <p style="color:#555; font-size:13px; margin:0;">
                                📅 Fecha de ingreso: {ingreso if ingreso else "No registrada"}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

                    # Expediente en grid
                    campos_expte = {
                        "🪪 CURP":          fila.get("CURP", ""),
                        "📋 RFC":            fila.get("RFC", ""),
                        "🏥 NSS":            fila.get("NSS", ""),
                        "🩸 Tipo de Sangre": fila.get("Tipo_Sangre", ""),
                        "⚠️ Padecimientos":  fila.get("Padecimientos:", ""),
                        "🌿 Alergias":       fila.get("Alergias:", ""),
                        "📞 Teléfono":       fila.get("Telefono:", ""),
                    }

                    g1, g2 = st.columns(2)
                    items = list(campos_expte.items())
                    for i, (campo, valor) in enumerate(items):
                        val_clean = _limpiar_texto(valor) or "—"
                        target_col = g1 if i % 2 == 0 else g2
                        target_col.markdown(f"""
                        <div style="background:#ffffff; border: 1px solid #e0e0e0;
                                    border-radius: 6px; padding: 12px 16px; margin-bottom: 10px;">
                            <span style="font-size:12px; color:#888; display:block;">{campo}</span>
                            <span style="font-size:15px; font-weight:600; color:#111;">{val_clean}</span>
                        </div>
                        """, unsafe_allow_html=True)

                    # Cursos de este colaborador
                    st.markdown("#### 📚 Capacitaciones registradas")
                    emp_id_str = _limpiar_texto(fila.get("Numero_Control_Personal", ""))
                    if "Empleado" in df_cursos_acc.columns:
                        df_emp_cursos = df_cursos_acc[
                            df_cursos_acc["Empleado"].str.strip() == emp_id_str
                        ].copy()
                    else:
                        df_emp_cursos = pd.DataFrame()

                    if df_emp_cursos.empty:
                        st.info("Este colaborador no tiene cursos registrados en la base de datos.")
                    else:
                        cols_vis = [c for c in [
                            "Nombre_del_Curso", "Fecha_del_curso", "Horas_Invertidas",
                            "Quien_imparte", "DCIII", "Donde_curso", "Competencias_adquiridas"
                        ] if c in df_emp_cursos.columns]
                        st.dataframe(
                            df_emp_cursos[cols_vis].rename(columns={
                                "Nombre_del_Curso": "Curso",
                                "Fecha_del_curso": "Fecha",
                                "Horas_Invertidas": "Horas",
                                "Quien_imparte": "Impartidor",
                                "DCIII": "Constancia DC-3",
                                "Donde_curso": "Lugar",
                                "Competencias_adquiridas": "Competencias"
                            }),
                            use_container_width=True,
                            hide_index=True
                        )

            # ─────────────────────────────────────────────
            # SUB-TAB 2: HISTORIAL DE CAPACITACIÓN
            # ─────────────────────────────────────────────
            with sub_cursos:
                st.subheader("📚 Historial Completo de Capacitación")

                if df_cursos_acc.empty:
                    st.info("No hay registros de capacitación disponibles.")
                else:
                    c_fil1, c_fil2, c_fil3 = st.columns(3)
                    with c_fil1:
                        cursos_unicos = ["— Todos —"] + sorted(
                            df_cursos_acc.get("Nombre_del_Curso", pd.Series(dtype=str))
                            .apply(lambda x: _limpiar_texto(x))
                            .replace("", "Sin nombre").unique().tolist()
                        )
                        curso_fil = st.selectbox("🔍 Filtrar por curso:", cursos_unicos, key="hist_curso_fil")

                    with c_fil2:
                        emps_unicos = ["— Todos —"] + sorted(
                            df_cursos_acc.get("Empleado", pd.Series(dtype=str))
                            .apply(_limpiar_texto).unique().tolist()
                        )
                        emp_fil = st.selectbox("👤 Filtrar por empleado:", emps_unicos, key="hist_emp_fil")

                    with c_fil3:
                        dc3_fil = st.selectbox(
                            "📜 Constancia DC-3:",
                            ["— Todos —", "✅ Con DC-3", "❌ Sin DC-3"],
                            key="hist_dc3_fil"
                        )

                    df_hist_view = df_cursos_acc.copy()

                    if curso_fil != "— Todos —":
                        df_hist_view = df_hist_view[
                            df_hist_view.get("Nombre_del_Curso", pd.Series(dtype=str))
                            .apply(lambda x: _limpiar_texto(x)) == curso_fil
                        ]
                    if emp_fil != "— Todos —":
                        df_hist_view = df_hist_view[
                            df_hist_view.get("Empleado", pd.Series(dtype=str))
                            .apply(_limpiar_texto) == emp_fil
                        ]
                    if dc3_fil == "✅ Con DC-3":
                        df_hist_view = df_hist_view[
                            df_hist_view.get("DCIII", pd.Series(dtype=str))
                            .apply(lambda x: _limpiar_texto(x) not in ("", "None", "nan"))
                        ]
                    elif dc3_fil == "❌ Sin DC-3":
                        df_hist_view = df_hist_view[
                            df_hist_view.get("DCIII", pd.Series(dtype=str))
                            .apply(lambda x: _limpiar_texto(x) in ("", "None", "nan"))
                        ]

                    st.markdown(f"**{len(df_hist_view)}** registros encontrados.")

                    cols_tabla = [c for c in [
                        "Empleado", "Nombre_del_Curso", "Fecha_del_curso", "Cierre_del_Curso",
                        "Horas_Invertidas", "Quien_imparte", "DCIII", "Donde_curso",
                        "Valor_Curricular", "Competencias_adquiridas"
                    ] if c in df_hist_view.columns]

                    st.dataframe(
                        df_hist_view[cols_tabla].rename(columns={
                            "Empleado": "# Empleado",
                            "Nombre_del_Curso": "Curso",
                            "Fecha_del_curso": "Inicio",
                            "Cierre_del_Curso": "Cierre",
                            "Horas_Invertidas": "Horas",
                            "Quien_imparte": "Impartidor",
                            "DCIII": "Constancia DC-3",
                            "Donde_curso": "Lugar",
                            "Valor_Curricular": "Valor Curr.",
                            "Competencias_adquiridas": "Competencias"
                        }),
                        use_container_width=True,
                        hide_index=True
                    )

                    # Descarga
                    buf_cursos = io.BytesIO()
                    df_hist_view.to_excel(buf_cursos, index=False)
                    buf_cursos.seek(0)
                    st.download_button(
                        "⬇️ Descargar Historial (.xlsx)",
                        data=buf_cursos,
                        file_name="historial_capacitacion_sigrama.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="dl_historial_cap"
                    )

            # ─────────────────────────────────────────────
            # SUB-TAB 3: DASHBOARD DC-3
            # ─────────────────────────────────────────────
            with sub_dashboard:
                st.subheader("📊 Dashboard de Capacitación e Indicadores DC-3")

                if df_cursos_acc.empty:
                    st.info("Sin datos suficientes para generar el dashboard.")
                else:
                    d1, d2 = st.columns(2)

                    # Horas por empleado
                    with d1:
                        if "Empleado" in df_cursos_acc.columns and "Horas_Invertidas" in df_cursos_acc.columns:
                            df_hrs = df_cursos_acc.copy()
                            df_hrs["Horas_Invertidas"] = pd.to_numeric(
                                df_hrs["Horas_Invertidas"], errors="coerce").fillna(0)
                            hrs_emp = (
                                df_hrs.groupby("Empleado")["Horas_Invertidas"]
                                .sum()
                                .sort_values(ascending=False)
                                .reset_index()
                            )
                            fig_hrs = go.Figure(go.Bar(
                                x=hrs_emp["Empleado"],
                                y=hrs_emp["Horas_Invertidas"],
                                marker_color="#EC2024",
                                text=hrs_emp["Horas_Invertidas"].astype(int),
                                textposition="outside"
                            ))
                            fig_hrs.update_layout(
                                title="⏱️ Horas de Capacitación por Empleado",
                                xaxis_title="# Empleado",
                                yaxis_title="Horas",
                                font=dict(family="Questrial", size=13),
                                plot_bgcolor="#ffffff",
                                paper_bgcolor="#ffffff",
                                margin=dict(t=50, b=40, l=30, r=10),
                                height=350
                            )
                            st.plotly_chart(fig_hrs, use_container_width=True)

                    # Cursos más frecuentes
                    with d2:
                        if "Nombre_del_Curso" in df_cursos_acc.columns:
                            top_cursos = (
                                df_cursos_acc["Nombre_del_Curso"]
                                .apply(_limpiar_texto)
                                .value_counts()
                                .head(10)
                                .reset_index()
                            )
                            top_cursos.columns = ["Curso", "Participantes"]
                            fig_top = go.Figure(go.Bar(
                                y=top_cursos["Curso"],
                                x=top_cursos["Participantes"],
                                orientation="h",
                                marker_color="#111111",
                                text=top_cursos["Participantes"],
                                textposition="outside"
                            ))
                            fig_top.update_layout(
                                title="🏆 Top 10 Cursos más Impartidos",
                                xaxis_title="Participantes",
                                font=dict(family="Questrial", size=12),
                                plot_bgcolor="#ffffff",
                                paper_bgcolor="#ffffff",
                                margin=dict(t=50, b=40, l=160, r=30),
                                height=350
                            )
                            st.plotly_chart(fig_top, use_container_width=True)

                    # Indicador DC-3 donut
                    st.markdown("#### 📜 Cobertura de Constancias DC-3 (STPS)")
                    if "DCIII" in df_cursos_acc.columns:
                        con_dc3 = df_cursos_acc["DCIII"].apply(
                            lambda x: _limpiar_texto(x) not in ("", "None", "nan")).sum()
                        sin_dc3 = len(df_cursos_acc) - con_dc3
                        pct_dc3 = (con_dc3 / len(df_cursos_acc) * 100) if len(df_cursos_acc) > 0 else 0

                        dc1, dc2, dc3 = st.columns([1, 2, 1])
                        with dc2:
                            fig_dc3 = go.Figure(data=[go.Pie(
                                labels=["Con DC-3", "Sin DC-3"],
                                values=[con_dc3, sin_dc3],
                                hole=0.7,
                                marker=dict(colors=["#EC2024", "#e0e0e0"]),
                                textinfo="label+percent",
                                hoverinfo="label+value"
                            )])
                            fig_dc3.update_layout(
                                title=dict(
                                    text=f"<b>Cobertura DC-3: {pct_dc3:.1f}%</b>",
                                    x=0.5, y=0.02, xanchor="center",
                                    font=dict(size=15)
                                ),
                                showlegend=True,
                                font=dict(family="Questrial"),
                                height=320,
                                margin=dict(t=20, b=60, l=20, r=20),
                                annotations=[dict(
                                    text=f"<b>{int(pct_dc3)}%</b>",
                                    x=0.5, y=0.5, font=dict(size=26), showarrow=False
                                )]
                            )
                            st.plotly_chart(fig_dc3, use_container_width=True)

                    # Tabla resumen de horas por curso con promedio
                    st.markdown("#### 📋 Resumen por Curso")
                    if "Nombre_del_Curso" in df_cursos_acc.columns and "Horas_Invertidas" in df_cursos_acc.columns:
                        df_resumen = df_cursos_acc.copy()
                        df_resumen["Horas_Invertidas"] = pd.to_numeric(
                            df_resumen["Horas_Invertidas"], errors="coerce").fillna(0)
                        resumen_tab = (
                            df_resumen.groupby("Nombre_del_Curso")
                            .agg(
                                Participantes=("Empleado", "count"),
                                Horas_Total=("Horas_Invertidas", "sum"),
                                Horas_Promedio=("Horas_Invertidas", "mean")
                            )
                            .reset_index()
                            .sort_values("Horas_Total", ascending=False)
                        )
                        resumen_tab["Horas_Promedio"] = resumen_tab["Horas_Promedio"].round(1)
                        st.dataframe(
                            resumen_tab.rename(columns={
                                "Nombre_del_Curso": "Curso",
                                "Participantes": "# Participantes",
                                "Horas_Total": "Horas Totales",
                                "Horas_Promedio": "Horas Promedio"
                            }),
                            use_container_width=True,
                            hide_index=True
                        )

            # ─────────────────────────────────────────────
            # SUB-TAB 4: CATÁLOGOS INSTITUCIONALES
            # ─────────────────────────────────────────────
            with sub_catalogos:
                st.subheader("📋 Catálogos Institucionales de Sigrama")

                cat1, cat2 = st.columns(2)

                with cat1:
                    st.markdown("#### 🏷️ Puestos y Disciplinas")
                    if df_puestos_acc.empty:
                        st.info("No hay puestos disponibles en la base de datos.")
                    else:
                        for _, row in df_puestos_acc.iterrows():
                            val = _limpiar_texto(row.iloc[0])
                            if val:
                                st.markdown(
                                    f'<div style="padding:8px 14px; margin-bottom:6px; '
                                    f'background:#f8f9fa; border-left:3px solid #EC2024; '
                                    f'border-radius:4px; font-family:Questrial; font-size:14px;">'
                                    f'💼 {val}</div>',
                                    unsafe_allow_html=True
                                )

                with cat2:
                    st.markdown("#### 📖 Cursos Disponibles en Sigrama")
                    if df_cursos_cat.empty:
                        st.info("No hay cursos disponibles en la base de datos.")
                    else:
                        for _, row in df_cursos_cat.iterrows():
                            val = _limpiar_texto(row.iloc[0])
                            if val:
                                st.markdown(
                                    f'<div style="padding:8px 14px; margin-bottom:6px; '
                                    f'background:#f8f9fa; border-left:3px solid #111111; '
                                    f'border-radius:4px; font-family:Questrial; font-size:14px;">'
                                    f'🎓 {val}</div>',
                                    unsafe_allow_html=True
                                )

# ==============================================================================
# SECCIÓN BANCO TIEMPO POR TIEMPO (TxT) — FO-RHU-22 SOLICITUD DE PERMISOS
# ==============================================================================

ARCHIVO_BANCO_TXT = os.path.join(ruta_carpeta, "banco_txt.xlsx").replace("\\", "/")

COLUMNAS_TXT = [
    "folio", "fecha_emision", "id_empleado", "nombre_empleado",
    "tipo", "dias", "fecha_inicio", "fecha_fin", "horas",
    "causa", "periodo", "autoriza", "aplicado_en", "estatus"
]


def cargar_banco_txt() -> pd.DataFrame:
    """Lee el banco_txt.xlsx o crea uno vacío si no existe."""
    if not os.path.exists(ARCHIVO_BANCO_TXT):
        df_vacio = pd.DataFrame(columns=COLUMNAS_TXT)
        df_vacio.to_excel(ARCHIVO_BANCO_TXT, index=False)
        return df_vacio
    try:
        df = pd.read_excel(ARCHIVO_BANCO_TXT, dtype=str)
        # Aseguramos que existan todas las columnas esperadas
        for col in COLUMNAS_TXT:
            if col not in df.columns:
                df[col] = ""
        return df[COLUMNAS_TXT].fillna("")
    except Exception:
        return pd.DataFrame(columns=COLUMNAS_TXT)


def guardar_banco_txt(df: pd.DataFrame) -> bool:
    """Guarda el banco_txt.xlsx localmente y lo sube a GitHub si hay token."""
    try:
        df.to_excel(ARCHIVO_BANCO_TXT, index=False)
        if GITHUB_TOKEN:
            url_api = f"https://api.github.com/repos/{REPO_NAME}/contents/asistencias/banco_txt.xlsx"
            headers_gh = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Streamlit-App"
            }
            sha_val = None
            res_get = requests.get(url_api, headers=headers_gh, timeout=10)
            if res_get.status_code == 200:
                sha_val = res_get.json().get("sha")
            with open(ARCHIVO_BANCO_TXT, "rb") as fh:
                contenido_b64 = base64.b64encode(fh.read()).decode("utf-8")
            payload = {
                "message": "Sincronizacion banco_txt.xlsx",
                "content": contenido_b64
            }
            if sha_val:
                payload["sha"] = sha_val
            requests.put(url_api, json=payload, headers=headers_gh, timeout=15)
        return True
    except Exception:
        return False


def _generar_folio(df_existing: pd.DataFrame) -> str:
    """Genera el próximo folio correlativo en formato TXT-YYYY-NNN."""
    anio = datetime.now().year
    registros_anio = df_existing[
        df_existing["folio"].str.startswith(f"TXT-{anio}-", na=False)
    ]
    siguiente = len(registros_anio) + 1
    return f"TXT-{anio}-{siguiente:03d}"


def _calcular_saldo(df_txt: pd.DataFrame, id_emp: str) -> float:
    """Calcula el saldo neto de horas TxT de un colaborador."""
    if df_txt.empty:
        return 0.0
    df_emp = df_txt[
        (df_txt["id_empleado"].str.strip() == str(id_emp).strip()) &
        (df_txt["estatus"].str.strip().str.lower() != "cancelado")
    ].copy()
    if df_emp.empty:
        return 0.0
    df_emp["horas_num"] = pd.to_numeric(df_emp["horas"], errors="coerce").fillna(0)
    cargas   = df_emp[df_emp["tipo"] == "CARGA"]["horas_num"].sum()
    descargas = df_emp[df_emp["tipo"] == "DESCARGA"]["horas_num"].sum()
    return round(cargas - descargas, 2)


with tab_txt:
    # ── Banner institucional ──────────────────────────────────────────────────
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e65100 0%, #bf360c 100%);
                border-radius: 12px; padding: 24px 32px; margin-bottom: 24px;">
        <h2 style="color:#FFFFFF; font-family:'Montserrat',sans-serif; margin:0;">
            ⏱️ Banco de Tiempo por Tiempo (TxT)
        </h2>
        <p style="color:#ffe0b2; font-family:'Questrial',sans-serif; margin:6px 0 0 0; font-size:15px;">
            Control de Permisos FO-RHU-22 · Industria Sigrama S.A. de C.V.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Cargar datos
    df_txt_data = cargar_banco_txt()
    df_personal_base = cargar_catalogo_personal()

    # ── KPI banner ───────────────────────────────────────────────────────────
    total_inc  = len(df_txt_data)
    total_cargas = len(df_txt_data[df_txt_data["tipo"] == "CARGA"]) if not df_txt_data.empty else 0
    total_desc = len(df_txt_data[df_txt_data["tipo"] == "DESCARGA"]) if not df_txt_data.empty else 0

    hrs_cargadas  = pd.to_numeric(df_txt_data[df_txt_data["tipo"] == "CARGA"]["horas"],   errors="coerce").fillna(0).sum() if not df_txt_data.empty else 0
    hrs_descarg   = pd.to_numeric(df_txt_data[df_txt_data["tipo"] == "DESCARGA"]["horas"], errors="coerce").fillna(0).sum() if not df_txt_data.empty else 0

    k1t, k2t, k3t, k4t = st.columns(4)
    k1t.metric("📋 Total Incidencias", total_inc)
    k2t.metric("➕ Cargas (permisos)", total_cargas, delta=f"+{hrs_cargadas:.1f} hrs")
    k3t.metric("➖ Descargas (extras)", total_desc,  delta=f"-{hrs_descarg:.1f} hrs")
    k4t.metric("📊 Saldo Sistema Total", f"{hrs_cargadas - hrs_descarg:.1f} hrs")

    st.markdown("---")

    # ── Sub-tabs ─────────────────────────────────────────────────────────────
    txt_reg, txt_saldo, txt_hist = st.tabs([
        "📋 Registrar Incidencia",
        "📊 Banco por Colaborador",
        "🗂️ Historial de Incidencias"
    ])

    # ════════════════════════════════════════════════════════════════════════
    # SUB-TAB 1: REGISTRAR INCIDENCIA
    # ════════════════════════════════════════════════════════════════════════
    with txt_reg:
        if st.session_state.get("usuario_rol") != "Administrador":
            st.warning("🔒 Solo el Administrador puede registrar incidencias TxT.")
        else:
            st.subheader("📋 Nueva Incidencia — Solicitud de Permisos FO-RHU-22")

            # Selector de colaborador
            if df_personal_base.empty:
                st.error("No hay colaboradores en el catálogo de personal.")
            else:
                ids_p   = df_personal_base["id_empleado"].tolist()
                noms_p  = df_personal_base["nombre"].tolist()
                opts_p  = [f"{i} — {n}" for i, n in zip(ids_p, noms_p)]

                col_form1, col_form2 = st.columns(2)

                with col_form1:
                    sel_emp_txt = st.selectbox(
                        "👤 Colaborador:", opts_p, key="txt_sel_emp"
                    )
                    idx_emp_sel = opts_p.index(sel_emp_txt)
                    id_emp_sel  = ids_p[idx_emp_sel]
                    nom_emp_sel = noms_p[idx_emp_sel]

                    # Saldo actual del colaborador seleccionado
                    saldo_actual = _calcular_saldo(df_txt_data, id_emp_sel)
                    color_saldo  = "#2e7d32" if saldo_actual >= 0 else "#c62828"
                    st.markdown(
                        f'<div style="background:#f5f5f5; border-left:4px solid {color_saldo}; '
                        f'border-radius:6px; padding:12px 16px; margin:8px 0;">'
                        f'<span style="font-size:12px;color:#666;">Saldo actual de horas TxT</span><br>'
                        f'<span style="font-size:22px;font-weight:700;color:{color_saldo};">'
                        f'{saldo_actual:.2f} hrs</span></div>',
                        unsafe_allow_html=True
                    )

                    tipo_inc = st.radio(
                        "Tipo de movimiento:",
                        ["➕ CARGA (permiso presentado)", "➖ DESCARGA (tiempo extra trabajado)"],
                        key="txt_tipo_radio"
                    )
                    tipo_val = "CARGA" if "CARGA" in tipo_inc else "DESCARGA"

                    folio_auto = _generar_folio(df_txt_data)
                    folio_inp  = st.text_input(
                        "📄 Folio del Formato FO-RHU-22:",
                        value=folio_auto,
                        key="txt_folio"
                    )
                    fecha_emision_inp = st.date_input(
                        "📅 Fecha de Emisión del Formato:",
                        value=datetime.now().date(),
                        key="txt_fecha_emision"
                    )

                with col_form2:
                    num_dias_inp = st.number_input(
                        "📆 Número de días que abarca:",
                        min_value=1, max_value=30, value=1,
                        key="txt_num_dias"
                    )
                    fecha_inicio_inp = st.date_input(
                        "📅 Fecha Inicio (primer día afectado):",
                        value=datetime.now().date(),
                        key="txt_fecha_ini"
                    )
                    fecha_fin_inp = st.date_input(
                        "📅 Fecha Fin (último día afectado):",
                        value=datetime.now().date(),
                        key="txt_fecha_fin"
                    )
                    horas_inp = st.number_input(
                        "⏱️ Cantidad de Horas:",
                        min_value=0.5, max_value=48.0,
                        value=1.0, step=0.5,
                        format="%.1f",
                        key="txt_horas"
                    )
                    periodo_inp = st.text_input(
                        "📋 Periodo (ej: 16-31 Jul 2026):",
                        key="txt_periodo"
                    )
                    autoriza_inp = st.text_input(
                        "✍️ Autoriza (Jefe de Depto / Nombre):",
                        key="txt_autoriza"
                    )

                causa_inp = st.text_area(
                    "📝 Causa o Descripción de la Incidencia:",
                    placeholder="Ej: Permiso por cita médica. Se presentó formato FO-RHU-22 folio TXT-2026-001 autorizado por Jefe de Área.",
                    height=80,
                    key="txt_causa"
                )

                # Validación previa
                if tipo_val == "DESCARGA":
                    if saldo_actual - horas_inp < 0:
                        st.warning(
                            f"⚠️ Esta descarga de **{horas_inp:.1f} hrs** dejaría el banco en "
                            f"**{saldo_actual - horas_inp:.1f} hrs** (saldo negativo). "
                            f"¿Deseas continuar?"
                        )

                col_btn1, col_btn2 = st.columns([3, 1])
                with col_btn1:
                    guardar_btn = st.button(
                        "💾 Registrar Incidencia TxT",
                        use_container_width=True,
                        type="primary",
                        key="txt_guardar_btn"
                    )
                with col_btn2:
                    st.markdown("<br>", unsafe_allow_html=True)

                if guardar_btn:
                    if not folio_inp.strip():
                        st.error("❌ El folio es obligatorio.")
                    elif not causa_inp.strip():
                        st.error("❌ La causa/descripción es obligatoria.")
                    elif fecha_fin_inp < fecha_inicio_inp:
                        st.error("❌ La fecha fin no puede ser anterior a la fecha inicio.")
                    else:
                        nuevo_registro = {
                            "folio":            folio_inp.strip().upper(),
                            "fecha_emision":    str(fecha_emision_inp),
                            "id_empleado":      id_emp_sel,
                            "nombre_empleado":  nom_emp_sel,
                            "tipo":             tipo_val,
                            "dias":             str(num_dias_inp),
                            "fecha_inicio":     str(fecha_inicio_inp),
                            "fecha_fin":        str(fecha_fin_inp),
                            "horas":            str(horas_inp),
                            "causa":            causa_inp.strip(),
                            "periodo":          periodo_inp.strip(),
                            "autoriza":         autoriza_inp.strip(),
                            "aplicado_en":      str(datetime.now().date()),
                            "estatus":          "Aplicado"
                        }
                        df_txt_data = pd.concat(
                            [df_txt_data, pd.DataFrame([nuevo_registro])],
                            ignore_index=True
                        )
                        ok = guardar_banco_txt(df_txt_data)
                        st.cache_data.clear()
                        if ok:
                            signo = "+" if tipo_val == "CARGA" else "-"
                            nuevo_saldo = _calcular_saldo(df_txt_data, id_emp_sel)
                            st.success(
                                f"✅ Incidencia **{folio_inp.upper()}** registrada correctamente. "
                                f"Movimiento: **{signo}{horas_inp:.1f} hrs**. "
                                f"Nuevo saldo de **{nom_emp_sel}**: **{nuevo_saldo:.2f} hrs**"
                            )
                            st.rerun()
                        else:
                            st.error("❌ Error al guardar el archivo. Verifique permisos de escritura.")

    # ════════════════════════════════════════════════════════════════════════
    # SUB-TAB 2: BANCO POR COLABORADOR
    # ════════════════════════════════════════════════════════════════════════
    with txt_saldo:
        st.subheader("📊 Saldo de Horas TxT por Colaborador")

        if df_personal_base.empty:
            st.info("No hay colaboradores registrados en el catálogo de personal.")
        else:
            filas_saldo = []
            for _, row_p in df_personal_base.iterrows():
                id_e   = str(row_p.get("id_empleado", "")).strip()
                nom_e  = str(row_p.get("nombre", "")).strip()
                area_e = str(row_p.get("area", "")).strip()
                saldo  = _calcular_saldo(df_txt_data, id_e)

                df_emp_mov = df_txt_data[
                    (df_txt_data["id_empleado"].str.strip() == id_e) &
                    (df_txt_data["estatus"].str.strip().str.lower() != "cancelado")
                ] if not df_txt_data.empty else pd.DataFrame()

                cargas_e   = pd.to_numeric(df_emp_mov[df_emp_mov["tipo"] == "CARGA"]["horas"],    errors="coerce").fillna(0).sum() if not df_emp_mov.empty else 0
                descargas_e = pd.to_numeric(df_emp_mov[df_emp_mov["tipo"] == "DESCARGA"]["horas"], errors="coerce").fillna(0).sum() if not df_emp_mov.empty else 0
                num_inc_e  = len(df_emp_mov)

                filas_saldo.append({
                    "# Empleado":    id_e,
                    "Nombre":        nom_e,
                    "Área":          area_e,
                    "Horas Cargadas (+)":   round(cargas_e, 2),
                    "Horas Descargadas (-)": round(descargas_e, 2),
                    "Saldo Actual (hrs)":   saldo,
                    "# Incidencias":  num_inc_e
                })

            df_saldo_view = pd.DataFrame(filas_saldo)

            # Resaltar con colores
            def _color_saldo_col(val):
                try:
                    v = float(val)
                    if v > 0:   return "color: #2e7d32; font-weight: bold;"
                    elif v < 0: return "color: #c62828; font-weight: bold;"
                    else:       return "color: #555;"
                except Exception:
                    return ""

            styled_saldo = df_saldo_view.style.map(
                _color_saldo_col, subset=["Saldo Actual (hrs)"]
            )
            st.dataframe(styled_saldo, use_container_width=True, hide_index=True)

            # Descarga del resumen
            buf_saldo = io.BytesIO()
            df_saldo_view.to_excel(buf_saldo, index=False)
            buf_saldo.seek(0)
            st.download_button(
                "⬇️ Descargar Resumen Banco TxT (.xlsx)",
                data=buf_saldo,
                file_name="resumen_banco_txt_sigrama.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_saldo_txt"
            )

            # Gráfica de barras de saldo
            if not df_saldo_view.empty and df_saldo_view["Saldo Actual (hrs)"].sum() != 0:
                st.markdown("#### 📊 Comparativa de Saldos")
                colores_barras = [
                    "#2e7d32" if v >= 0 else "#c62828"
                    for v in df_saldo_view["Saldo Actual (hrs)"]
                ]
                fig_saldo = go.Figure(go.Bar(
                    x=df_saldo_view["Nombre"],
                    y=df_saldo_view["Saldo Actual (hrs)"],
                    marker_color=colores_barras,
                    text=[f"{v:.1f}" for v in df_saldo_view["Saldo Actual (hrs)"]],
                    textposition="outside"
                ))
                fig_saldo.update_layout(
                    title="Saldo de Horas TxT por Colaborador",
                    xaxis_title="Colaborador",
                    yaxis_title="Horas",
                    font=dict(family="Questrial", size=13),
                    plot_bgcolor="#ffffff",
                    paper_bgcolor="#ffffff",
                    margin=dict(t=50, b=80, l=40, r=20),
                    height=350,
                    shapes=[dict(
                        type="line", x0=-0.5, x1=len(df_saldo_view)-0.5,
                        y0=0, y1=0,
                        line=dict(color="#111", width=1.5, dash="dash")
                    )]
                )
                st.plotly_chart(fig_saldo, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # SUB-TAB 3: HISTORIAL DE INCIDENCIAS
    # ════════════════════════════════════════════════════════════════════════
    with txt_hist:
        st.subheader("🗂️ Historial Completo de Incidencias TxT")

        if df_txt_data.empty:
            st.info("📋 Aún no hay incidencias registradas. Usa la pestaña '📋 Registrar Incidencia' para comenzar.")
        else:
            # ── Filtros ──────────────────────────────────────────────────
            hf1, hf2, hf3 = st.columns(3)
            with hf1:
                emp_opts_h = ["— Todos —"] + sorted(df_txt_data["nombre_empleado"].unique().tolist())
                emp_fil_h  = st.selectbox("👤 Empleado:", emp_opts_h, key="hist_txt_emp")
            with hf2:
                tipo_opts_h = ["— Todos —", "CARGA", "DESCARGA"]
                tipo_fil_h  = st.selectbox("🔄 Tipo:", tipo_opts_h, key="hist_txt_tipo")
            with hf3:
                est_opts_h = ["— Todos —"] + sorted(df_txt_data["estatus"].unique().tolist())
                est_fil_h  = st.selectbox("📌 Estatus:", est_opts_h, key="hist_txt_est")

            df_hist_view = df_txt_data.copy()
            if emp_fil_h  != "— Todos —":
                df_hist_view = df_hist_view[df_hist_view["nombre_empleado"] == emp_fil_h]
            if tipo_fil_h != "— Todos —":
                df_hist_view = df_hist_view[df_hist_view["tipo"] == tipo_fil_h]
            if est_fil_h  != "— Todos —":
                df_hist_view = df_hist_view[df_hist_view["estatus"] == est_fil_h]

            st.markdown(f"**{len(df_hist_view)}** incidencias encontradas.")

            st.dataframe(
                df_hist_view.rename(columns={
                    "folio":           "Folio",
                    "fecha_emision":   "Fecha Emisión",
                    "id_empleado":     "# Empleado",
                    "nombre_empleado": "Nombre",
                    "tipo":            "Tipo",
                    "dias":            "Días",
                    "fecha_inicio":    "Fecha Inicio",
                    "fecha_fin":       "Fecha Fin",
                    "horas":           "Horas",
                    "causa":           "Causa",
                    "periodo":         "Periodo",
                    "autoriza":        "Autoriza",
                    "aplicado_en":     "Aplicado en",
                    "estatus":         "Estatus"
                }),
                use_container_width=True,
                hide_index=True
            )

            # Cancelar incidencia (solo Admin)
            if st.session_state.get("usuario_rol") == "Administrador":
                st.markdown("---")
                st.markdown("#### 🗑️ Cancelar una Incidencia")
                folios_act = df_txt_data[
                    df_txt_data["estatus"].str.strip().str.lower() != "cancelado"
                ]["folio"].tolist()

                if folios_act:
                    folio_cancel = st.selectbox(
                        "Selecciona el folio a cancelar:",
                        folios_act,
                        key="txt_cancel_sel"
                    )
                    motivo_cancel = st.text_input(
                        "Motivo de la cancelación:",
                        key="txt_cancel_motivo"
                    )
                    if st.button("🗑️ Cancelar Incidencia", key="txt_cancel_btn", type="secondary"):
                        if not motivo_cancel.strip():
                            st.error("❌ Debes indicar el motivo de la cancelación.")
                        else:
                            df_txt_data.loc[
                                df_txt_data["folio"] == folio_cancel, "estatus"
                            ] = "Cancelado"
                            df_txt_data.loc[
                                df_txt_data["folio"] == folio_cancel, "causa"
                            ] = df_txt_data.loc[
                                df_txt_data["folio"] == folio_cancel, "causa"
                            ].astype(str) + f" [CANCELADO: {motivo_cancel.strip()}]"
                            ok_cancel = guardar_banco_txt(df_txt_data)
                            st.cache_data.clear()
                            if ok_cancel:
                                st.success(f"✅ Incidencia **{folio_cancel}** cancelada.")
                                st.rerun()
                            else:
                                st.error("❌ Error al guardar la cancelación.")
                else:
                    st.info("No hay incidencias activas para cancelar.")

            # Descarga del historial filtrado
            buf_hist = io.BytesIO()
            df_hist_view.to_excel(buf_hist, index=False)
            buf_hist.seek(0)
            st.download_button(
                "⬇️ Descargar Historial (.xlsx)",
                data=buf_hist,
                file_name="historial_incidencias_txt_sigrama.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_hist_txt"
            )
