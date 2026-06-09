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
import streamlit as st
import os
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

st.markdown("---") # Línea divisoria estética antes de iniciar los paneles y pestañas

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
# SECCIÓN 5 - INTERFAZ CORPORATIVA Y PARSER DE HORAS (CORREGIDA SIN DUPLICADOS)
# ==============================================================================
st.markdown("<h2 style='text-align: center;'>👥 Portal de Capital Humano: Formato FO-RHU-23</h2>", unsafe_allow_html=True)
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



# Declaración actualizada de las pestañas de la aplicación
tab_reportes, tab_areas, tab_historico = st.tabs([
    "📊 Pre-Nómina y Reportes", 
    "📁 Asignación de Áreas y Personal",
    "📈 Histórico Semanal"
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



    


    
    df_editor = st.data_editor(df_db, column_config={"id_empleado": st.column_config.TextColumn("ID Empleado", required=True), "nombre": st.column_config.TextColumn("Nombre Completo del Colaborador", required=True), "area": st.column_config.SelectboxColumn("Área Operativa Asignada", options=AREAS_LISTA_RAW, required=True)}, num_rows="dynamic", use_container_width=True, key="maestro_personal_editor")
    
    st.markdown("---")
    st.markdown("#### 🔒 Autorización de Cambios")
    clave_usuario = st.text_input("Ingresa la Clave de Usuario para guardar en GitHub:", type="password")
    
    if st.button("💾 Guardar Cambios ESTRUCTURALES de la Tabla y Sincronizar con GitHub"):
        if clave_usuario != "RHSigrama":
            st.error("❌ Clave de Usuario incorrecta. No tienes autorización.")
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
    story.append(Paragraph("<b>CONTROL DE PRE-NÓMINA - FORMATO OFICIAL FO-RHU-23</b>", style_sub))
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
                


                # Sincronización directa desde Excel de Personal (Corregida)
                df_db_mapping = cargar_catalogo_personal()[['id_empleado', 'area']]
                df_db_mapping['id_empleado'] = df_db_mapping['id_empleado'].astype(str).str.strip()
                
                # Unimos las tablas de forma limpia
                matriz_final = matriz_final.merge(df_db_mapping, left_on='#Empleado', right_on='id_empleado', how='left')
                
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
    label="📄 Descargar Reporte FO-RHU-23 Dividido por Áreas (.xlsx)", 
    data=buffer_excel.getvalue(), 
    file_name=f"FO-RHU-23_PRENOMINA_POR_AREAS_{fecha_fin.strftime('%Y%m%d')}.xlsx",
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
    label="📄 Descargar Reporte FO-RHU-23 en PDF",
    data=pdf_data,
    file_name=f"FO-RHU-23_PRENOMINA_{fecha_fin.strftime('%Y%m%d')}.pdf",
    mime="application/pdf"
)


# ==============================================================================
# SECCIÓN - HISTÓRICO SEMANAL (CÁLCULO, REGISTRO Y GRÁFICAS)
# ==============================================================================
with tab_historico:
    st.subheader("📈 Histórico General por Semana")
    st.write("Resumen consolidado de indicadores clave de la empresa.")

    ARCHIVO_HISTORICO = "historico_semanal.xlsx"

    # 1. CARGAMOS EL HISTÓRICO EXISTENTE
    if os.path.exists(ARCHIVO_HISTORICO):
        try:
            df_hist = pd.read_excel(ARCHIVO_HISTORICO)
        except Exception:
            df_hist = pd.DataFrame(columns=["Semana", "Fecha Inicio", "Fecha Fin", "Asistencia", "Puntualidad", "Tasa de Ausencia"])
    else:
        df_hist = pd.DataFrame(columns=["Semana", "Fecha Inicio", "Fecha Fin", "Asistencia", "Puntualidad", "Tasa de Ausencia"])

    # 2. PROCESAMOS LA SEMANA ACTUAL SI HAY DATOS CARGADOS
    if 'matriz_final' in locals() and not matriz_final.empty and 'fecha_inicio' in locals():
        # Calculamos la fecha de fin sumando 6 días a la fecha de inicio
        f_inicio = pd.to_datetime(fecha_inicio).date()
        f_fin = f_inicio + pd.timedelta(days=6)
        
        # Obtenemos el número de semana del año de forma automática
        num_semana = pd.to_datetime(fecha_inicio).isocalendar().week
        etiqueta_semana = f"Semana {num_semana}"

        # --- Extracción y Cálculo Limpio de Métricas ---
        columnas_dias_num = [c for c in matriz_final.columns if isinstance(c, (int, float)) or (isinstance(c, str) and c.isdigit())]
        
        if columnas_dias_num:
            valores_totales = matriz_final[columnas_dias_num].values.flatten()
            total_registros = len(valores_totales)
            
            conteo_asistencias = sum(1 for v in valores_totales if v in ['A', 'R'])
            conteo_puntuales = sum(1 for v in valores_totales if v == 'A')
            conteo_faltas = sum(1 for v in valores_totales if v in ['F', 'S', 'D'])
            
            porcentaje_asistencia = round((conteo_asistencias / total_registros) * 100, 2) if total_registros > 0 else 0.0
            porcentaje_puntualidad = round((conteo_puntuales / conteo_asistencias) * 100, 2) if conteo_asistencias > 0 else 0.0
            porcentaje_ausentismo = round((conteo_faltas / total_registros) * 100, 2) if total_registros > 0 else 0.0
            
            st.info(f"📊 Datos listos para archivar: **{etiqueta_semana}** ({f_inicio.strftime('%d-%b-%y')} al {f_fin.strftime('%d-%b-%y')})")
            
            # Botón estructurado para guardar renglón
            if st.button("💾 Guardar esta Semana en la Tabla Histórica"):
                # Si la semana ya existe, actualizamos sus datos para evitar duplicados
                if etiqueta_semana in df_hist['Semana'].values:
                    idx = df_hist[df_hist['Semana'] == etiqueta_semana].index
                    df_hist.loc[idx, ["Asistencia", "Puntualidad", "Tasa de Ausencia"]] = [f"{porcentaje_asistencia}%", f"{porcentaje_puntualidad}%", f"{porcentaje_ausentismo}%"]
                    st.warning(f"⚠️ Los datos de la {etiqueta_semana} se han actualizado.")
                else:
                    # Creamos el nuevo renglón con el formato exacto de tu tabla
                    nuevo_renglon = pd.DataFrame([{
                        "Semana": etiqueta_semana,
                        "Fecha Inicio": f_inicio.strftime('%d-%b-%y').lower(),
                        "Fecha Fin": f_fin.strftime('%d-%b-%y').lower(),
                        "Asistencia": f"{porcentaje_asistencia}%",
                        "Puntualidad": f"{porcentaje_puntualidad}%",
                        "Tasa de Ausencia": f"{porcentaje_ausentismo}%"
                    }])
                    df_hist = pd.concat([df_hist, nuevo_renglon], ignore_index=True)
                    st.success(f"✅ ¡{etiqueta_semana} añadida con éxito!")
                
                df_hist.to_excel(ARCHIVO_HISTORICO, index=False)
                st.rerun()
    else:
        st.caption("💡 Ve a la primera pestaña para cargar un rango de asistencias y poder agregarlo aquí.")

    # 3. DESPLIEGUE DE LA TABLA ESTILO EXCEL CON SU FILA DE PROMEDIO
    st.markdown("---")
    if not df_hist.empty:
        # Hacemos una copia limpia para mostrar en pantalla sin alterar el archivo original
        df_visual de la tabla = df_hist.copy()
        
        # --- Cálculo automático de la fila PROMEDIO ---
        # Convertimos los textos con '%' a números flotantes para poder promediar de forma exacta
        asist_num = df_visual de la tabla['Asistencia'].str.rstrip('%').astype(float)
        punt_num = df_visual de la tabla['Puntualidad'].str.rstrip('%').astype(float)
        ausen_num = df_visual de la tabla['Tasa de Ausencia'].str.rstrip('%').astype(float)
        
        fila_promedio = pd.DataFrame([{
            "Semana": "PROMEDIO",
            "Fecha Inicio": "",
            "Fecha Fin": "",
            "Asistencia": f"{round(asist_num.mean())}%",
            "Puntualidad": f"{round(punt_num.mean())}%",
            "Tasa de Ausencia": f"{round(ausen_num.mean())}%"
        }])
        
        # Unimos la fila de promedios al final de la tabla visual
        df_visual de la tabla = pd.concat([df_visual de la tabla, fila_promedio], ignore_index=True)
        
        # Mostramos la tabla formateada en Streamlit ocultando el índice por defecto
        st.dataframe(df_visual de la tabla, use_container_width=True, hide_index=True)
        
        # Gráfica de líneas interactiva (No toma en cuenta la fila PROMEDIO para no distorsionar)
        st.markdown("### 📈 Tendencia de Indicadores")
        df_grafica = df_hist.copy()
        df_grafica['Asistencia'] = df_grafica['Asistencia'].str.rstrip('%').astype(float)
        df_grafica['Puntualidad'] = df_grafica['Puntualidad'].str.rstrip('%').astype(float)
        df_grafica['Tasa de Ausencia'] = df_grafica['Tasa de Ausencia'].str.rstrip('%').astype(float)
        st.line_chart(df_grafica.set_index("Semana")[["Asistencia", "Puntualidad", "Tasa de Ausencia"]])
    else:
        st.info("La tabla histórica está vacía. Guarda una semana para ver el formato estilo Excel.")
