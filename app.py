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

# Configuración estética de la interfaz del navegador
st.set_page_config(
    page_title="Portal RH - Industria Sigrama", 
    layout="wide", 
    page_icon="👥"
)

# Constantes del Sistema
ARCHIVO_PERSONAL = "personal.xlsx"
ruta_carpeta = "./asistencias"

if not os.path.exists(ruta_carpeta):
    os.makedirs(ruta_carpeta)

# --- RECONOCIMIENTO DEL TOKEN DESDE SECRETS ---
try:
    GITHUB_TOKEN = st.secrets["github"]["token"]
except:
    GITHUB_TOKEN = None

REPO_NAME = "jesusalbertomoraleslopez-byte/sigrama-prenomina-app"
# ==============================================================================
# SECCIÓN 2 - PANEL LATERAL Y CARGADOR DE ARCHIVOS
# ==============================================================================
st.sidebar.header("⚙️ Configuración del Periodo")

# Cargador de archivos en espera
st.sidebar.subheader("📥 Cargar Nuevas Asistencias")
archivos_correo = st.sidebar.file_uploader(
    "Arrastra aquí tus archivos .xls del correo:", 
    type=["xls"], 
    accept_multiple_files=True
)

if archivos_correo:
    st.sidebar.info(f"📋 {len(archivos_correo)} archivo(s) listos.")
# ==============================================================================
# SECCIÓN 3 - ENLACE DE ARCHIVOS ENTRANTES CON GITHUB
# ==============================================================================
if archivos_correo:
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
# ==============================================================================
# SECCIÓN 4 - GESTIÓN DE TIEMPO Y MANEJO DE PERSONAL PERSISTENTE
# ==============================================================================
hora_limite_input = st.sidebar.time_input(
    "Hora límite de Entrada:", 
    value=datetime.strptime("08:01:00", "%H:%M:%S").time()
)

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
# SECCIÓN 5 - INTERFAZ CORPORATIVA Y PARSER DE HORAS
# ==============================================================================
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
# ==============================================================================
# SECCIÓN 6 - LECTURA EXTRACTORA XLS Y PANEL DE CONTROL DE PERSONAL
# ==============================================================================
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

tab_reporte, tab_areas = st.tabs(["📊 Pre-Nómina y Reportes", "📂 Asignación de Áreas y Personal"])
AREAS_LISTA_RAW = ["⚪ Sin Asignar", "👑 Dirección", "⚙️ Ingeniería", "🔍 Calidad", "📐 Doblez", "✂️ Corte Laser", "🎨 Pintura", "📦 Embarque"]

with tab_areas:
    st.subheader("📝 Panel de Control de Plantilla y Estructura Organizacional")
    df_db = cargar_catalogo_personal()
    
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
            df_db = pd.concat([df_db, pd.DataFrame(nuevos_registros)], ignore_index=True)
            df_db.to_excel(ARCHIVO_PERSONAL, index=False)
            
    df_editor = st.data_editor(df_db, column_config={"id_empleado": st.column_config.TextColumn("ID Empleado", required=True), "nombre": st.column_config.TextColumn("Nombre Completo del Colaborador", required=True), "area": st.column_config.SelectboxColumn("Área Operativa Asignada", options=AREAS_LISTA_RAW, required=True)}, num_rows="dynamic", use_container_width=True, key="maestro_personal_editor")
    
    st.markdown("---")
    st.markdown("#### 🔒 Autorización de Cambios")
    clave_usuario = st.text_input("Ingresa la Clave de Usuario para guardar en GitHub:", type="password")
    
    if st.button("💾 Guardar Cambios ESTRUCTURALES de la Tabla y Sincronizar con GitHub"):
        if clave_usuario != "RHSigrama":
            st.error("❌ Clave de Usuario incorrecta. No tienes autorización.")
        else:
            try:
                df_editor.to_excel(ARCHIVO_PERSONAL, index=False)
                if GITHUB_TOKEN:
                    url_api_personal = f"https://github.com{REPO_NAME}/contents/{ARCHIVO_PERSONAL}"
                    headers_github = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json", "User-Agent": "Streamlit-App"}
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
# ==============================================================================
# SECCIÓN 7 - PIVOTACIÓN DE INCIDENCIAS Y MATRIZ DE CRUCE DE ÁREAS
# ==============================================================================
with tab_reporte:
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
                matriz = df_raw_filtrado.pivot_table(index=['#Empleado', 'Nombre del Empleado'], columns='Dia_Num', values='Cod_Incidencia', aggfunc='first')
                for col_dia in [d.day for d in lista_dias]:
                    if col_dia not in matriz.columns: matriz[col_dia] = None
                matriz = matriz[[d.day for d in lista_dias]]
                matriz_final = matriz.copy().reset_index()
                
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
                    puntualidades.append(f"{((a + r - r) / (a + r) * 100) if (a + r) > 0 else 0:.0f}%")
                    desempenos.append("40%" if f > 0 else ("70%" if r > 0 else "100%"))
                    
                matriz_final['PUNTUALIDAD'] = puntualidades
                matriz_final['ASISTENCIA'] = asistencias
                matriz_final['DESEMPEÑO'] = desempenos
                matriz_final.columns = [str(c) for c in matriz_final.columns]
                matriz_final['#Empleado'] = matriz_final['#Empleado'].astype(str).str.strip()
                
                # Sincronización directa desde Excel de Personal
                df_db_mapping = cargar_catalogo_personal()[['id_empleado', 'area']]
                df_db_mapping['id_empleado'] = df_db_mapping['id_empleado'].astype(str).str.strip()
                matriz_final = matriz_final.merge(df_db_mapping, left_on='#Empleado', right_on='id_empleado', how='left')
                matriz_final['area'] = matriz_final['area'].fillna("⚪ Sin Asignar").str.strip()
                
                for vv, vn in [("Sin Asignar", "⚪ Sin Asignar"), ("Corte Laser", "✂️ Corte Laser"), ("Doblez", "📐 Doblez"), ("Pintura", "🎨 Pintura"), ("Embarque", "📦 Embarque"), ("Calidad", "🔍 Calidad"), ("Dirección", "👑 Dirección"), ("Ingeniería", "⚙️ Ingeniería")]:
                    matriz_final.loc[matriz_final['area'] == vv, 'area'] = vn
                    
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
        ws.write('A1', 'FO-RHU-23', fmt_meta_code)
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
# SECCIÓN 8 (PARTE 3) - CORRECCIÓN DINÁMICA ABSOLUTA ANTI-OVERLAPPING
# ==============================================================================
            # Calculamos de forma dinámica el límite seguro de columnas para no tocar las métricas finales
            total_columnas_datos = len(cols_mostrar)
            columna_limite_seguro = max(2, total_columnas_datos - 4) 
            
            # Recuadro de Observaciones dinámico (Nunca choca con las métricas finales)
            fila_obs = fila_inicio_datos + len(df_hoja) + 2
            ws.merge_range(fila_obs, 0, fila_obs + 2, columna_limite_seguro, "", workbook.add_format({'border': 1, 'border_color': '#FF0000', 'valign': 'top'}))
            ws.write(fila_obs, 0, " OBSERVACIONES: ", workbook.add_format({'bold': True, 'font_name': 'Arial', 'font_size': 9, 'color': '#FF0000'}))
            
            # Glosario de Incidencias escalado asimétricamente según el ancho disponible
            fila_firmas = fila_obs + 5
            ws.write(fila_firmas, 1, "ASISTENCIA= A\nTIEMPO EXTRA= TE\nTRABAJO FORANEO= TF\nPERMISO= P\nFALTA= F\nVACACIONES= V\nINCAPACIDAD= I\nBONO PUNTUALIDAD= SÍ O NO\nBONO ASISTENCIA= SÍ O NO\nBONO DESEMPEÑO= 50, 75 ó 100%", workbook.add_format({'font_name': 'Arial', 'font_size': 9, 'text_wrap': True}))
            
            col_glosario_der = max(6, columna_limite_seguro - 4)
            ws.write(fila_firmas, col_glosario_der, "NO LABORABLE CONVENIO= NLC\nDÍA FESTIVO LABORADO= DFL\nDIA DE DESCANSO LABORADO= DDL\nTIEMPO POR TIEMPO= TxT\nPERMISO SIN GOCE DE SUELDO= PSG\nSÁBADO= S\nDOMINGO= D", workbook.add_format({'font_name': 'Arial', 'font_size': 9, 'text_wrap': True}))
            
            # Espacios y Leyendas Estructurales de Firmas Autorizadas de manera segura
            fmt_linea_firma = workbook.add_format({'top': 1, 'top_color': '#000000', 'align': 'center', 'font_name': 'Arial', 'font_size': 9, 'bold': True})
            fmt_texto_firma = workbook.add_format({'align': 'center', 'font_name': 'Arial', 'font_size': 9, 'bold': True})
            
            # Posicionamiento matemático de las firmas en base al tamaño del reporte
            col_firma1_ini = 2
            col_firma1_fin = max(3, int(columna_limite_seguro / 2))
            col_firma2_ini = col_firma1_fin + 2
            col_firma2_fin = columna_limite_seguro
            
            # Línea y Texto de Firma Director General
            ws.merge_range(fila_firmas + 4, col_firma1_ini, fila_firmas + 4, col_firma1_fin, "", fmt_linea_firma)
            ws.merge_range(fila_firmas + 5, col_firma1_ini, fila_firmas + 5, col_firma1_fin, "FIRMA DIRECTOR GENERAL", fmt_texto_firma)
            
            # Línea y Texto de Firma Gerente de Área
            ws.merge_range(fila_firmas + 4, col_firma2_ini, fila_firmas + 4, col_firma2_fin, "", fmt_linea_firma)
            ws.merge_range(fila_firmas + 5, col_firma2_ini, fila_firmas + 5, col_firma2_fin, "FIRMA GERENTE DE ÁREA", fmt_texto_firma)
            
            # Pie de Página de Protección Intelectual de Industria Sigrama
            ws.write(fila_firmas + 8, 0, "FO-SGC-02 PROHIBIDA LA REPRODUCCIÓN TOTAL O PARCIAL, SIN AUTORIZACIÓN POR ESCRITO DE INDUSTRIA SIGRAMA S.A. DE C.V.", workbook.add_format({'font_name': 'Arial', 'font_size': 8, 'italic': True, 'color': '#777777'}))

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
    label="📄 Descargar Reporte FO-RHU-23 Dividido por Áreas (.xlsx)", 
    data=buffer_excel.getvalue(), 
    file_name=f"FO-RHU-23_PRENOMINA_POR_AREAS_{fecha_fin.strftime('%Y%m%d')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
