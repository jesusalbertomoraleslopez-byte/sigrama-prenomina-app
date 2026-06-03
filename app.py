# ==============================================================================
# PORTAL DE CAPITAL HUMANO - INDUSTRIA SIGRAMA S.A. DE C.V. (FORMATO FO-RHU-23)
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

# Configuración estética de la interfaz del navegador
st.set_page_config(
    page_title="Portal RH - Industria Sigrama", 
    layout="wide", 
    page_icon="👥"
)

# Constantes del Sistema de Archivos
ARCHIVO_PERSONAL = "personal.xlsx"
AREAS_LISTA_RAW = ["⚪ Sin Asignar", "👑 Dirección", "⚙️ Ingeniería", "🔍 Calidad", "📐 Doblez", "✂️ Corte Laser", "🎨 Pintura", "📦 Embarque"]

# Función para interactuar de forma segura con el catálogo maestro en Excel
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
st.sidebar.header("⚙️ Configuración del Periodo")
ruta_carpeta = "./asistencias"
if not os.path.exists(ruta_carpeta):
    os.makedirs(ruta_carpeta)

# --- RECONOCIMIENTO DEL TOKEN DESDE SECRETS ---
try:
    GITHUB_TOKEN = st.secrets["github"]["token"]
except:
    GITHUB_TOKEN = None

REPO_NAME = "jesusalbertomoraleslopez-byte/sigrama-prenomina-app"

# Cargador de archivos en espera
st.sidebar.subheader("📥 Cargar Nuevas Asistencias")
archivos_correo = st.sidebar.file_uploader(
    "Arrastra aquí tus archivos .xls del correo:", 
    type=["xls"], 
    accept_multiple_files=True
)

if archivos_correo:
    st.sidebar.info(f"📋 {len(archivos_correo)} archivo(s) listos.")

if st.sidebar.button("🚀 Subir y Guardar directamente en GitHub", use_container_width=True):
    if not GITHUB_TOKEN:
        st.sidebar.error("⚠️ Error: No se encontró el Token en los Secrets.")
    else:
        exitos = 0
        for archivo in archivos_correo:
            ruta_local = os.path.join(ruta_carpeta, archivo.name).replace("\\", "/")
            contenido_bytes = archivo.getbuffer()
            with open(ruta_local, "wb") as f:
                f.write(contenido_bytes)
            
            url_api = f"https://github.com{REPO_NAME}/contents/asistencias/{archivo.name}"
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Streamlit-App"
            }
            sha = None
            try:
                res_get = requests.get(url_api, headers=headers, timeout=10)
                if res_get.status_code == 200:
                    sha = res_get.json().get("sha")
            except:
                pass
            
            contenido_base64 = base64.b64encode(contenido_bytes).decode("utf-8")
            payload = {
                "message": f"Carga de asistencia diaria: {archivo.name}",
                "content": contenido_base64
            }
            if sha:
                payload["sha"] = sha
            try:
                res_put = requests.put(url_api, json=payload, headers=headers, timeout=15)
                if res_put.status_code in [200, 201]:
                    exitos += 1
            except:
                pass
        if exitos > 0:
            st.sidebar.success(f"¡{exitos} archivo(s) guardado(s) en GitHub!")
            st.rerun()

hora_limite_input = st.sidebar.time_input("Hora límite de Entrada:", value=datetime.strptime("08:01:00", "%H:%M:%S").time())

# Cálculo dinámico de la quincena actual real del calendario (Año 2026)
hoy_real = datetime.now().date()
if hoy_real.day <= 15:
    defecto_inicio = hoy_real.replace(day=1)
    defecto_fin = hoy_real.replace(day=15)
else:
    defecto_inicio = hoy_real.replace(day=16)
    siguiente_mes = hoy_real.replace(day=28) + timedelta(days=4)
    defecto_fin = siguiente_mes - timedelta(days=siguiente_mes.day)

st.sidebar.subheader("📅 Fechas de la Quincena")
fecha_inicio = st.sidebar.date_input("Fecha Inicio:", value=defecto_inicio)
fecha_fin = st.sidebar.date_input("Fecha Fin:", value=defecto_fin)
# Renderizado del Logotipo corporativo al 30% de la pantalla
logo_path = "LOGOTIPO COLOR (1).jfif"
if os.path.exists(logo_path):
    col_izq, col_logo, col_der = st.columns([0.35, 0.30, 0.35])
    with col_logo:
        st.image(logo_path, use_container_width=True)
else:
    st.title("Industria Sigrama - Control de Asistencias")

st.markdown("<h3 style='text-align: center;'>👥 Portal de Capital Humano: Formato FO-RHU-23</h3>", unsafe_allow_html=True)
st.markdown("---")

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

def aplicar_colores_matriz(val):
    if val in ["A", "R"]:
        return 'background-color: #d4edda; color: #155724; font-weight: bold; text-align: center;'
    elif val == "F":
        return 'background-color: #f8d7da; color: #721c24; font-weight: bold; text-align: center;'
    elif val in ["S", "D"]:
        return 'background-color: #fff3cd; color: #856404; font-weight: bold; text-align: center;'
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
            df_limpio['Fecha_Raw'] = df[col_fecha[0]] if col_fecha else df.iloc[:, 4]
            df_limpio['Hora Entrada Raw'] = df[col_hora[0]] if col_hora else df.iloc[:, 6]
            df_limpio['Nave Entrada'] = df[col_nave[0]] if col_nave else df.iloc[:, 7]
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

tab_reporte, tab_areas = st.tabs(["📊 Pre-Nómina y Reportes", "📂 Asignación de Áreas y Personal"])
with tab_areas:
    st.subheader("📝 Panel de Control de Plantilla y Estructura Organizacional")
    
    # 1. Lectura desde el archivo Excel
    df_db = cargar_catalogo_personal()
    
    # Inyección y detección automática de personal nuevo desde asistencias .xls
    df_asistencias_raw = procesar_base_asistencias(ruta_carpeta)
    cambio_detectado = False
    
    if df_asistencias_raw is not None:
        empleados_nuevos = df_asistencias_raw[['#Empleado', 'Nombre del Empleado']].drop_duplicates()
        nuevos_registros = []
        for _, emp in empleados_nuevos.iterrows():
            id_e = str(emp['#Empleado']).strip()
            nom_e = str(emp['Nombre del Empleado']).strip()
            
            if id_e not in df_db['id_empleado'].values and id_e != 'nan' and id_e != '':
                nuevos_registros.append({"id_empleado": id_e, "nombre": nom_e, "area": "⚪ Sin Asignar"})
                cambio_detectado = True
                
        if cambio_detectado:
            df_nuevos = pd.DataFrame(nuevos_registros)
            df_db = pd.concat([df_db, df_nuevos], ignore_index=True)
            df_db.to_excel(ARCHIVO_PERSONAL, index=False)
            
    st.markdown("#### Catálogo Maestro de Personal")
    df_editor = st.data_editor(
        df_db, 
        column_config={
            "id_empleado": st.column_config.TextColumn("ID Empleado", required=True), 
            "nombre": st.column_config.TextColumn("Nombre Completo del Colaborador", required=True), 
            "area": st.column_config.SelectboxColumn("Área Operativa Asignada", options=AREAS_LISTA_RAW, required=True)
        }, 
        num_rows="dynamic", 
        use_container_width=True, 
        key="maestro_personal_editor"
    )
    
    if st.button("💾 Guardar Cambios ESTRUCTURALES de la Tabla y Enviar a GitHub"):
        try:
            # Guardado local temporal en el contenedor de Streamlit
            df_editor.to_excel(ARCHIVO_PERSONAL, index=False)
            
            if GITHUB_TOKEN:
                url_api_personal = f"https://github.com{REPO_NAME}/contents/{ARCHIVO_PERSONAL}"
                headers_github = {
                    "Authorization": f"token {GITHUB_TOKEN}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "Streamlit-App"
                }
                
                # Obtener SHA de la versión en GitHub para reemplazarlo sin conflictos
                sha_personal = None
                res_get = requests.get(url_api_personal, headers=headers_github, timeout=10)
                if res_get.status_code == 200:
                    sha_personal = res_get.json().get("sha")
                
                with open(ARCHIVO_PERSONAL, "rb") as f:
                    contenido_bytes_personal = f.read()
                
                contenido_b64_personal = base64.b64encode(contenido_bytes_personal).decode("utf-8")
                
                payload_personal = {
                    "message": "Actualización automática del catálogo maestro (personal.xlsx)",
                    "content": contenido_b64_personal
                }
                if sha_personal:
                    payload_personal["sha"] = sha_personal
                    
                res_put = requests.put(url_api_personal, json=payload_personal, headers=headers_github, timeout=15)
                
                if res_put.status_code in [200, 201]:
                    st.success("¡Catálogo guardado en el servidor y sincronizado exitosamente en tu repositorio de GitHub!")
                    st.rerun()
                else:
                    st.error(f"Error al empujar archivo a GitHub (Código: {res_put.status_code})")
            else:
                st.warning("⚠️ Cambios guardados localmente de forma provisional. No se subieron a GitHub porque falta el GITHUB_TOKEN.")
                st.rerun()
        except Exception as e:
            st.error(f"Error al ejecutar actualización estructural: {e}")

    st.markdown("---")
    st.markdown("#### 📥 Importación Masiva de Personal")
    col_down, col_up = st.columns(2)
    with col_down:
        st.markdown("**1. Descarga la estructura oficial:**")
        df_plantilla = pd.DataFrame(columns=["id_empleado", "nombre", "area"])
        buffer_plantilla = io.BytesIO()
        with pd.ExcelWriter(buffer_plantilla, engine='xlsxwriter') as writer:
            df_plantilla.to_excel(writer, index=False, sheet_name='Plantilla')
        st.download_button(label="⬇️ Descargar Plantilla Oficial (.xlsx)", 
            data=buffer_plantilla.getvalue(), file_name="plantilla_carga_personal_sigrama.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            
    with col_up:
        st.markdown("**2. Sube tu archivo lleno:**")
        archivo_carga = st.file_uploader("Cargar Excel de Personal:", type=["xlsx", "xls"])
        if archivo_carga is not None:
            try:
                df_cargado = pd.read_excel(archivo_carga, dtype=str)
                df_cargado.columns = df_cargado.columns.str.strip()
                if "id_empleado" in df_cargado.columns and "nombre" in df_cargado.columns:
                    df_cargado['area'] = df_cargado['area'].fillna("⚪ Sin Asignar").str.strip()
                    df_db = pd.concat([df_db, df_cargado]).drop_duplicates(subset=['id_empleado'], keep='last')
                    df_db.to_excel(ARCHIVO_PERSONAL, index=False)
                    st.success("¡Personal importado con éxito! Haz clic arriba en 'Guardar Cambios ESTRUCTURALES' para guardarlo permanentemente.")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
# ==============================================================================
# SECCIÓN E (PARTE 1) - INTEGRACIÓN DEL ARCHIVO EXCEL EN REPORTES
# ==============================================================================
# Reemplazo de la consulta SQL por la lectura directa de personal.xlsx
df_db_mapping = cargar_catalogo_personal()[['id_empleado', 'area']]
df_db_mapping['id_empleado'] = df_db_mapping['id_empleado'].astype(str).str.strip()

# Unión de la matriz calculada con el catálogo de personal oficial
matriz_final = matriz_final.merge(df_db_mapping, left_on='#Empleado', right_on='id_empleado', how='left')
matriz_final['area'] = matriz_final['area'].fillna("⚪ Sin Asignar").str.strip()
# ==============================================================================
# SECCIÓN E (PARTE 2) - NORMALIZACIÓN DE ESTRUCTURA Y EMOJIS DE ÁREAS
# ==============================================================================
mapeo_nombres_areas = [
    ("Sin Asignar", "⚪ Sin Asignar"), 
    ("Corte Laser", "✂️ Corte Laser"), 
    ("Doblez", "📐 Doblez"), 
    ("Pintura", "🎨 Pintura"), 
    ("Embarque", "📦 Embarque"), 
    ("Calidad", "🔍 Calidad"), 
    ("Dirección", "👑 Dirección"),
    ("Ingeniería", "⚙️ Ingeniería")
]

for vv, vn in mapeo_nombres_areas: 
    matriz_final.loc[matriz_final['area'] == vv, 'area'] = vn

st.subheader("📊 Dashboard Global de Asistencias e Incidencias")
# ==============================================================================
# SECCIÓN E (PARTE 3) - FILTRADO INTERACTIVO Y CLASIFICACIÓN DE HOJAS EXCEL
# ==============================================================================
cols_mostrar = ['#Empleado', 'Nombre del Empleado'] + columnas_dias_str + ['PUNTUALIDAD', 'ASISTENCIA', 'DESEMPEÑO']

st.markdown("### 📋 Reporte General Consolidado")
st.dataframe(matriz_final[cols_mostrar].style.map(aplicar_colores_matriz, subset=columnas_dias_str), use_container_width=True)

# Generación dinámica del listado de hojas para el archivo de Excel final
lista_hojas_excel = [('CONSOLIDADO', matriz_final)] + [
    (ar.replace("👑 ", "").replace("⚙️ ", "").replace("🔍 ", "").replace("📐 ", "").replace("✂️ ", "").replace("🎨 ", "").replace("📦 ", "").replace("⚪ ", "")[:31], 
     matriz_final[matriz_final['area'] == ar]) for ar in AREAS_LISTA_RAW
]
