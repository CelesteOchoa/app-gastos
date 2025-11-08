import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
import gspread
from google.oauth2 import service_account
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
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Función para conectar con Google Sheets
@st.cache_resource
def load_data_from_sheets(sheet):
    """Carga todos los datos desde Google Sheets con depuración"""
    try:
        data = sheet.get_all_records()  # Cargar registros
        st.write("Datos crudos cargados desde Google Sheets:", data)  # Mostrar datos crudos
        
        if data:
            df = pd.DataFrame(data)  # Convertir a DataFrame
            # Validar encabezados y contenido
            st.write("DataFrame previo a modificación:", df)
            # Convertir fecha a datetime si existe la columna 'Fecha'
            if 'Fecha' in df.columns:
                df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y', errors='coerce')
            # Asegurarse de que 'Monto' sea numérico para evitar errores
            if 'Monto' in df.columns:
                df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce')
            return df
        else:
            st.warning("No se encontraron datos en la hoja de cálculo.")
            return pd.DataFrame(columns=['Fecha', 'Categoría', 'Descripción', 'Monto', 'Método de Pago'])
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return pd.DataFrame(columns=['Fecha', 'Categoría', 'Descripción', 'Monto', 'Método de Pago'])

# Función para cargar datos desde Google Sheets
def load_data_from_sheets(sheet):
    """Carga todos los datos desde Google Sheets"""
    try:
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            # Convertir fecha a datetime
            if 'Fecha' in df.columns:
                df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y', errors='coerce')
            return df
        else:
            return pd.DataFrame(columns=['Fecha', 'Categoría', 'Descripción', 'Monto', 'Método de Pago'])
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return pd.DataFrame(columns=['Fecha', 'Categoría', 'Descripción', 'Monto', 'Método de Pago'])

# Función para guardar un nuevo gasto
def save_expense_to_sheets(sheet, fecha, categoria, descripcion, monto, metodo_pago):
    """Guarda un nuevo gasto en Google Sheets"""
    try:
        # Formatear fecha
        fecha_str = fecha.strftime('%d/%m/%Y')
        
        # Agregar nueva fila
        row = [fecha_str, categoria, descripcion, float(monto), metodo_pago]
        sheet.append_row(row)
        
        return True
    except Exception as e:
        st.error(f"Error al guardar gasto: {str(e)}")
        return False

# Función para inicializar la hoja con encabezados si está vacía
def initialize_sheet(sheet):
    """Inicializa la hoja con encabezados si está vacía"""
    try:
        if len(sheet.get_all_values()) == 0:
            headers = ['Fecha', 'Categoría', 'Descripción', 'Monto', 'Método de Pago']
            sheet.append_row(headers)
    except Exception as e:
        st.error(f"Error al inicializar hoja: {str(e)}")

# Nueva función: get_google_sheet()
def get_google_sheet():
    """Establece conexión con Google Sheets y devuelve una referencia a la hoja de cálculo."""
    try:
        # Cargar credenciales desde Streamlit Secrets
        creds_dict = st.secrets["gcp_service_account"]  # Verifica que las credenciales estén configuradas correctamente
        credentials = service_account.Credentials.from_service_account_info(creds_dict)

        # Autorizar con gspread
        client = gspread.authorize(credentials)

        # Abrir la hoja de cálculo por ID definido en Secrets
        sheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
        sheet = client.open_by_key(sheet_id).sheet1
        return sheet
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {str(e)}")
        return None

# APLICACIÓN PRINCIPAL
def main():
    # Título principal
    st.markdown('<h1 class="main-header">💰 Registro de Gastos</h1>', unsafe_allow_html=True)
    st.markdown("---")    
    # Conectar con Google Sheets
    sheet = get_google_sheet()
    
    if sheet is None:
        st.error("⚠️ No se pudo conectar con Google Sheets. Verifica la configuración de Secrets.")
        st.info("""
        **Pasos para configurar:**
        1. Ve a Settings de tu app en Streamlit Cloud
        2. Agrega tus credenciales en la sección Secrets
        3. Reinicia la app
        """)
        return
    
    # Inicializar hoja si está vacía
    initialize_sheet(sheet)
    
    # Cargar datos existentes
    df_gastos = load_data_from_sheets(sheet)
    
    # Sidebar para agregar nuevo gasto
    with st.sidebar:
        st.header("➕ Agregar Nuevo Gasto")
        
        with st.form("form_gasto"):
            fecha = st.date_input(
                "Fecha",
                value=date.today(),
                format="DD/MM/YYYY"
            )
            
            categoria = st.selectbox(
                "Categoría",
                ["Alimentos", "Transporte", "Salud", "Educación", 
                 "Entretenimiento", "Servicios", "Ropa", "Otros"]
            )
            
            descripcion = st.text_input("Descripción", placeholder="Ej: Supermercado")
            
            monto = st.number_input(
                "Monto ($)",
                min_value=0.0,
                step=100.0,
                format="%.2f"
            )
            
            metodo_pago = st.selectbox(
                "Método de Pago",
                ["Efectivo", "Tarjeta de Débito", "Tarjeta de Crédito", 
                 "Transferencia", "Otro"]
            )
            
            submitted = st.form_submit_button("💾 Guardar Gasto", use_container_width=True)
            
            if submitted:
                if descripcion and monto > 0:
                    with st.spinner("Guardando gasto..."):
                        if save_expense_to_sheets(sheet, fecha, categoria, descripcion, monto, metodo_pago):
                            st.success("✅ Gasto guardado exitosamente!")
                            st.balloons()
                            # Recargar datos
                            st.rerun()
                        else:
                            st.error("❌ Error al guardar el gasto")
                else:
                    st.warning("⚠️ Por favor completa todos los campos")
        
        st.markdown("---")
        st.info("💡 **Tip:** Todos los gastos se guardan automáticamente en Google Sheets")
    
    # Contenido principal
    if len(df_gastos) == 0:
        st.info("📝 No hay gastos registrados. ¡Agrega tu primer gasto en el panel lateral!")
    else:
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_gastos = df_gastos['Monto'].sum()
            st.metric("💵 Total Gastos", f"${total_gastos:,.2f}")
        
        with col2:
            promedio = df_gastos['Monto'].mean()
            st.metric("📊 Promedio", f"${promedio:,.2f}")
        
        with col3:
            num_transacciones = len(df_gastos)
            st.metric("🔢 Transacciones", num_transacciones)
        
        with col4:
            categoria_top = df_gastos.groupby('Categoría')['Monto'].sum().idxmax()
            st.metric("🏆 Categoría Top", categoria_top)
        
        st.markdown("---")
        
        # Tabs para diferentes vistas
        tab1, tab2, tab3 = st.tabs(["📋 Historial", "📊 Análisis", "📥 Exportar"])
        
        with tab1:
            st.subheader("📋 Historial Completo de Gastos")
            
            # Filtros
            col_filtro1, col_filtro2 = st.columns(2)
            
            with col_filtro1:
                categorias_filtro = st.multiselect(
                    "Filtrar por categoría",
                    options=df_gastos['Categoría'].unique(),
                    default=df_gastos['Categoría'].unique()
                )
            
            with col_filtro2:
                metodos_filtro = st.multiselect(
                    "Filtrar por método de pago",
                    options=df_gastos['Método de Pago'].unique(),
                    default=df_gastos['Método de Pago'].unique()
                )
            
            # Aplicar filtros
            df_filtrado = df_gastos[
                (df_gastos['Categoría'].isin(categorias_filtro)) &
                (df_gastos['Método de Pago'].isin(metodos_filtro))
            ]
            
            # Mostrar tabla
            st.dataframe(
                df_filtrado.sort_values('Fecha', ascending=False),
                use_container_width=True,
                hide_index=True
            )
            
            # Resumen del filtro
            st.info(f"📊 Mostrando {len(df_filtrado)} de {len(df_gastos)} transacciones | Total: ${df_filtrado['Monto'].sum():,.2f}")
        
        with tab2:
            st.subheader("📊 Análisis de Gastos")
            
            col_graph1, col_graph2 = st.columns(2)
            
            with col_graph1:
                # Gráfico de gastos por categoría
                gastos_categoria = df_gastos.groupby('Categoría')['Monto'].sum().sort_values(ascending=False)
                fig1 = px.bar(
                    x=gastos_categoria.values,
                    y=gastos_categoria.index,
                    orientation='h',
                    title="Gastos por Categoría",
                    labels={'x': 'Monto ($)', 'y': 'Categoría'},
                    color=gastos_categoria.values,
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col_graph2:
                # Gráfico de distribución por método de pago
                gastos_metodo = df_gastos.groupby('Método de Pago')['Monto'].sum()
                fig2 = px.pie(
                    values=gastos_metodo.values,
                    names=gastos_metodo.index,
                    title="Distribución por Método de Pago",
                    hole=0.4
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # Gráfico de evolución temporal
            st.subheader("📈 Evolución de Gastos en el Tiempo")
            df_tiempo = df_gastos.groupby('Fecha')['Monto'].sum().reset_index()
            fig3 = px.line(
                df_tiempo,
                x='Fecha',
                y='Monto',
                title="Gastos Diarios",
                markers=True
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        with tab3:
            st.subheader("📥 Exportar Datos")
            
            col_export1, col_export2 = st.columns(2)
            
            with col_export1:
                # Exportar a CSV
                csv = df_gastos.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📄 Descargar CSV",
                    data=csv,
                    file_name=f'gastos_{datetime.now().strftime("%Y%m%d")}.csv',
                    mime='text/csv',
                    use_container_width=True
                )
            
            with col_export2:
                # Exportar a Excel
                from io import BytesIO
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_gastos.to_excel(writer, index=False, sheet_name='Gastos')
                
                st.download_button(
                    label="📊 Descargar Excel",
                    data=buffer.getvalue(),
                    file_name=f'gastos_{datetime.now().strftime("%Y%m%d")}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True
                )
            
            st.info("💾 Los datos también están disponibles en tu Google Sheet")
            st.markdown(f"[🔗 Abrir Google Sheet](https://docs.google.com/spreadsheets/d/{st.secrets['google_sheets']['spreadsheet_id']})")

if __name__ == "__main__":
    main()
