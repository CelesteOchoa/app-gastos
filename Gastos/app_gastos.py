import streamlit as st
import pandas as pd
import openpyxl
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json

# Configuración de la página
st.set_page_config(
    page_title="📊 Registro de Gastos",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Archivo de datos
DATA_FILE = "gastos_data.json"

# Categorías predefinidas
CATEGORIAS_FIJAS = [
    "Alquiler", "Expensas", "Luz", "Gas", "Agua", 
    "Personal (Internet + Línea)", "Terapia", "Pilates",
    "Espacio El Peregrino", "La Coopi cloacas servicio",
    "La Coopi cloacas capitalización"
]

TARJETAS = ["BBVA", "Naranja", "Macro", "Santander", "Cencosud"]

CATEGORIAS_VARIABLES = [
    "Supermercado", "Verdulería", "Farmacia", "Transporte",
    "Restaurante", "Entretenimiento", "Ropa", "Otros"
]

# Funciones de manejo de datos
def cargar_datos():
    """Carga los datos desde el archivo JSON"""
    if Path(DATA_FILE).exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"gastos": []}

def guardar_datos(datos):
    """Guarda los datos en el archivo JSON"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def agregar_gasto(datos_nuevos):
    """Agrega un nuevo gasto"""
    datos = cargar_datos()
    datos["gastos"].append(datos_nuevos)
    guardar_datos(datos)
    return True

def obtener_gastos_df():
    """Obtiene los gastos como DataFrame de pandas"""
    datos = cargar_datos()
    if not datos["gastos"]:
        return pd.DataFrame()
    
    df = pd.DataFrame(datos["gastos"])
    # Convertir fecha a datetime
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

def exportar_a_excel(df, nombre_archivo):
    """Exporta los datos a Excel con formato similar al original"""
    if df.empty:
        return None
    
    # Crear workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    
    # Agrupar por mes
    df['mes'] = df['fecha'].dt.to_period('M')
    meses = df['mes'].unique()
    
    for idx, mes in enumerate(meses):
        if idx > 0:
            ws = wb.create_sheet(title=str(mes))
        else:
            ws.title = str(mes)
        
        # Datos del mes
        df_mes = df[df['mes'] == mes]
        
        # Encabezados
        ws['A1'] = 'GASTOS MENSUALES'
        ws['A2'] = 'Fecha'
        ws['B2'] = 'Concepto'
        ws['C2'] = 'Categoría'
        ws['D2'] = 'Importe'
        ws['E2'] = 'Método de Pago'
        ws['F2'] = 'Notas'
        
        # Datos
        for i, (_, row) in enumerate(df_mes.iterrows(), start=3):
            ws[f'A{i}'] = row['fecha'].strftime('%d/%m/%Y')
            ws[f'B{i}'] = row['concepto']
            ws[f'C{i}'] = row['categoria']
            ws[f'D{i}'] = row['importe']
            ws[f'E{i}'] = row.get('metodo_pago', '')
            ws[f'F{i}'] = row.get('notas', '')
    
    wb.save(nombre_archivo)
    return nombre_archivo

# Título principal
st.markdown('<h1 class="main-header">💰 Registro de Gastos Mensuales</h1>', unsafe_allow_html=True)

# Sidebar para navegación
with st.sidebar:
    st.image("https://em-content.zobj.net/thumbs/240/apple/354/money-bag_1f4b0.png", width=100)
    st.title("📋 Menú")
    
    opcion = st.radio(
        "Selecciona una opción:",
        ["📝 Registrar Gasto", "📊 Ver Gastos", "📈 Análisis", "⚙️ Configuración"]
    )
    
    st.markdown("---")
    st.markdown("### 📅 Fecha de hoy")
    st.info(datetime.now().strftime("%d/%m/%Y"))

# Contenido principal según la opción seleccionada
if opcion == "📝 Registrar Gasto":
    st.header("📝 Registrar un Nuevo Gasto")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tipo_gasto = st.selectbox(
            "Tipo de gasto:",
            ["💳 Gasto con Tarjeta", "💵 Gasto Fijo", "🛒 Gasto Variable"]
        )
        
        fecha = st.date_input("Fecha del gasto:", value=date.today())
        
        if tipo_gasto == "💵 Gasto Fijo":
            concepto = st.selectbox("Concepto:", CATEGORIAS_FIJAS)
        else:
            concepto = st.text_input("Concepto:", placeholder="Ej: Compra supermercado")
        
        importe = st.number_input("Importe ($):", min_value=0.0, step=100.0, format="%.2f")
    
    with col2:
        if tipo_gasto == "💳 Gasto con Tarjeta":
            tarjeta = st.selectbox("Tarjeta:", TARJETAS)
            cuotas = st.number_input("Cuotas:", min_value=1, max_value=48, value=1)
            metodo_pago = tarjeta
        else:
            metodo_pago = st.selectbox("Método de pago:", 
                ["Efectivo", "Transferencia", "Débito", "Otro"])
            cuotas = 1
        
        if tipo_gasto == "🛒 Gasto Variable":
            categoria = st.selectbox("Categoría:", CATEGORIAS_VARIABLES)
        else:
            categoria = concepto
        
        notas = st.text_area("Notas adicionales:", placeholder="Información extra...")
    
    st.markdown("---")
    
    if st.button("💾 Guardar Gasto", use_container_width=True, type="primary"):
        if concepto and importe > 0:
            nuevo_gasto = {
                "fecha": fecha.strftime("%Y-%m-%d"),
                "concepto": concepto,
                "categoria": categoria,
                "importe": importe,
                "tipo_gasto": tipo_gasto,
                "metodo_pago": metodo_pago,
                "cuotas": cuotas if tipo_gasto == "💳 Gasto con Tarjeta" else 1,
                "notas": notas,
                "timestamp": datetime.now().isoformat()
            }
            
            if agregar_gasto(nuevo_gasto):
                st.success("✅ ¡Gasto registrado exitosamente!")
                st.balloons()
        else:
            st.error("⚠️ Por favor completa todos los campos obligatorios")

elif opcion == "📊 Ver Gastos":
    st.header("📊 Historial de Gastos")
    
    df = obtener_gastos_df()
    
    if df.empty:
        st.warning("⚠️ No hay gastos registrados aún")
    else:
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            mes_filtro = st.selectbox(
                "Filtrar por mes:",
                ["Todos"] + list(df['fecha'].dt.to_period('M').astype(str).unique())
            )
        
        with col2:
            categoria_filtro = st.multiselect(
                "Filtrar por categoría:",
                options=df['categoria'].unique(),
                default=None
            )
        
        with col3:
            tipo_filtro = st.multiselect(
                "Filtrar por tipo:",
                options=df['tipo_gasto'].unique(),
                default=None
            )
        
        # Aplicar filtros
        df_filtrado = df.copy()
        
        if mes_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['fecha'].dt.to_period('M').astype(str) == mes_filtro]
        
        if categoria_filtro:
            df_filtrado = df_filtrado[df_filtrado['categoria'].isin(categoria_filtro)]
        
        if tipo_filtro:
            df_filtrado = df_filtrado[df_filtrado['tipo_gasto'].isin(tipo_filtro)]
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Total Gastado", f"${df_filtrado['importe'].sum():,.2f}")
        
        with col2:
            st.metric("📝 Cantidad de Gastos", len(df_filtrado))
        
        with col3:
            st.metric("📊 Promedio", f"${df_filtrado['importe'].mean():,.2f}")
        
        with col4:
            st.metric("💳 Gasto Máximo", f"${df_filtrado['importe'].max():,.2f}")
        
        st.markdown("---")
        
        # Tabla de gastos
        st.subheader("📋 Detalle de Gastos")
        
        # Preparar DataFrame para mostrar
        df_mostrar = df_filtrado[['fecha', 'concepto', 'categoria', 'importe', 'metodo_pago', 'notas']].copy()
        df_mostrar['fecha'] = df_mostrar['fecha'].dt.strftime('%d/%m/%Y')
        df_mostrar['importe'] = df_mostrar['importe'].apply(lambda x: f"${x:,.2f}")
        
        st.dataframe(
            df_mostrar,
            use_container_width=True,
            hide_index=True
        )
        
        # Botón de exportación
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("📥 Exportar a Excel", use_container_width=True):
                nombre_archivo = f"gastos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                archivo = exportar_a_excel(df_filtrado, nombre_archivo)
                if archivo:
                    with open(archivo, 'rb') as f:
                        st.download_button(
                            label="⬇️ Descargar Excel",
                            data=f,
                            file_name=nombre_archivo,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

elif opcion == "📈 Análisis":
    st.header("📈 Análisis de Gastos")
    
    df = obtener_gastos_df()
    
    if df.empty:
        st.warning("⚠️ No hay gastos registrados para analizar")
    else:
        # Gráficos en tabs
        tab1, tab2, tab3 = st.tabs(["📊 Por Categoría", "📅 Por Mes", "💳 Por Método de Pago"])
        
        with tab1:
            st.subheader("Gastos por Categoría")
            gastos_categoria = df.groupby('categoria')['importe'].sum().reset_index()
            gastos_categoria = gastos_categoria.sort_values('importe', ascending=False)
            
            fig1 = px.pie(
                gastos_categoria,
                values='importe',
                names='categoria',
                title='Distribución de Gastos por Categoría',
                hole=0.4
            )
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig1, use_container_width=True)
            
            # Tabla de desglose
            st.dataframe(gastos_categoria, use_container_width=True, hide_index=True)
        
        with tab2:
            st.subheader("Evolución Mensual")
            df['mes'] = df['fecha'].dt.to_period('M').astype(str)
            gastos_mes = df.groupby('mes')['importe'].sum().reset_index()
            
            fig2 = px.line(
                gastos_mes,
                x='mes',
                y='importe',
                title='Evolución de Gastos por Mes',
                markers=True
            )
            fig2.update_layout(xaxis_title="Mes", yaxis_title="Importe ($)")
            st.plotly_chart(fig2, use_container_width=True)
            
            # Gráfico de barras por categoría por mes
            gastos_mes_cat = df.groupby(['mes', 'categoria'])['importe'].sum().reset_index()
            fig3 = px.bar(
                gastos_mes_cat,
                x='mes',
                y='importe',
                color='categoria',
                title='Gastos por Categoría y Mes',
                barmode='stack'
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        with tab3:
            st.subheader("Gastos por Método de Pago")
            gastos_metodo = df.groupby('metodo_pago')['importe'].sum().reset_index()
            gastos_metodo = gastos_metodo.sort_values('importe', ascending=True)
            
            fig4 = px.bar(
                gastos_metodo,
                x='importe',
                y='metodo_pago',
                orientation='h',
                title='Distribución por Método de Pago'
            )
            st.plotly_chart(fig4, use_container_width=True)

elif opcion == "⚙️ Configuración":
    st.header("⚙️ Configuración")
    
    st.subheader("🗑️ Gestión de Datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Reiniciar Datos", type="secondary"):
            if st.checkbox("⚠️ Confirmar reinicio (se perderán todos los datos)"):
                guardar_datos({"gastos": []})
                st.success("✅ Datos reiniciados correctamente")
                st.rerun()
    
    with col2:
        st.info("💡 **Tip:** Puedes exportar tus datos antes de reiniciar desde la sección 'Ver Gastos'")
    
    st.markdown("---")
    st.subheader("📊 Estadísticas Generales")
    
    df = obtener_gastos_df()
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📝 Total de registros", len(df))
        with col2:
            st.metric("💰 Gasto total acumulado", f"${df['importe'].sum():,.2f}")
        with col3:
            meses_unicos = df['fecha'].dt.to_period('M').nunique()
            st.metric("📅 Meses registrados", meses_unicos)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>💰 Sistema de Registro de Gastos Mensuales | Desarrollado con ❤️ usando Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
