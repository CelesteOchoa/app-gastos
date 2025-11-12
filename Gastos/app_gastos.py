import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
import gspread
from google.oauth2 import service_account
from io import BytesIO
import openpyxl
import time

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

# Función para formatear montos en formato argentino
def format_pesos(monto):
    """Formatea un monto en pesos argentinos: 10.000,30"""
    return f"${monto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Función para conectar con Google Sheets
@st.cache_resource
def get_google_sheet():
    """Establece conexión con Google Sheets y devuelve una referencia a la hoja de cálculo."""
    try:
        # Cargar credenciales desde Streamlit Secrets
        creds_dict = st.secrets["gcp_service_account"]
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets',  # Acceso a Google Sheets
                  'https://www.googleapis.com/auth/drive']  # Acceso opcional a Google Drive

        credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(credentials)

        # Abrir la hoja de cálculo por ID definido en Secrets
        sheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
        sheet = client.open_by_key(sheet_id).sheet1
        return sheet
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {str(e)}")
        return None

def load_data_from_sheets():
    """Carga datos desde Google Sheets sin caché para obtener datos actualizados."""
    try:
        sheet = get_google_sheet()
        if sheet is None:
            return pd.DataFrame(columns=['Fecha', 'Categoría', 'Descripción', 'Monto', 'Método de Pago'])

        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            # Limpiar nombres de columnas eliminando espacios en blanco
            df.columns = df.columns.str.strip()

            if 'Fecha' in df.columns:
                df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y', errors='coerce')
            if 'Monto' in df.columns:
                df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce')
            return df
        else:
            return pd.DataFrame(columns=['Fecha', 'Categoría', 'Descripción', 'Monto', 'Método de Pago'])
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return pd.DataFrame(columns=['Fecha', 'Categoría', 'Descripción', 'Monto', 'Método de Pago'])

def save_expense_to_sheets(sheet, fecha, categoria, descripcion, monto, metodo_pago):
    try:
        fecha_str = fecha.strftime('%d/%m/%Y')
        row = [fecha_str, categoria, descripcion, float(monto), metodo_pago]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error al guardar gasto: {str(e)}")
        return False

def delete_expense_from_sheets(sheet, row_index):
    """Elimina un gasto de Google Sheets por índice de fila (1-indexed, incluyendo header)"""
    try:
        sheet.delete_rows(row_index)
        return True
    except Exception as e:
        st.error(f"Error al eliminar gasto: {str(e)}")
        return False

def initialize_sheet(sheet):
    try:
        if len(sheet.get_all_values()) == 0:
            headers = ['Fecha', 'Categoría', 'Descripción', 'Monto', 'Método de Pago']
            sheet.append_row(headers)
    except Exception as e:
        st.error(f"Error al inicializar hoja: {str(e)}")

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
    df_gastos = load_data_from_sheets()

    # Sidebar para agregar nuevo gasto
    with st.sidebar:
        st.header("➕ Agregar Nuevo Gasto")

        # Inicializar session_state para limpiar formulario
        if 'form_submitted' not in st.session_state:
            st.session_state.form_submitted = False

        with st.form("form_gasto", clear_on_submit=True):
            fecha = st.date_input(
                "Fecha",
                value=date.today(),
                format="DD/MM/YYYY"
            )

            categoria = st.selectbox(
                "Categoría",
                ["", "Alimentos", "Transporte", "Salud", "Educación",
                 "Entretenimiento", "Servicios", "Ropa", "Casa"],
                format_func=lambda x: "Seleccionar categoría..." if x == "" else x
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
                ["", "BBVA", "Macro", "Naranja",
                 "Santander", "Transferencia"],
                format_func=lambda x: "Seleccionar método..." if x == "" else x
            )

            submitted = st.form_submit_button("💾 Guardar Gasto", use_container_width=True)

            if submitted:
                if descripcion and monto > 0 and categoria and metodo_pago:
                    with st.spinner("Guardando gasto..."):
                        if save_expense_to_sheets(sheet, fecha, categoria, descripcion, monto, metodo_pago):
                            st.success("✅ Gasto guardado exitosamente!")
                            st.balloons()
                            st.session_state.form_submitted = True
                            # Recargar datos
                            time.sleep(0.5)  # Pequeña pausa para que el usuario vea el mensaje de éxito
                            st.rerun()
                        else:
                            st.error("❌ Error al guardar el gasto")
                else:
                    st.warning("⚠️ Por favor completa todos los campos")

        st.markdown("---")

        # Botón para abrir Google Sheets
        sheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"

        st.markdown(
            f'<a href="{sheet_url}" target="_blank" style="text-decoration: none;">'
            f'<button style="'
            f'background-color: #4CAF50; '
            f'border: none; '
            f'color: white; '
            f'padding: 10px 20px; '
            f'text-align: center; '
            f'text-decoration: none; '
            f'display: inline-block; '
            f'font-size: 14px; '
            f'margin: 4px 2px; '
            f'cursor: pointer; '
            f'border-radius: 5px; '
            f'width: 100%;'
            f'">'
            f'📊 Abrir Google Sheets'
            f'</button></a>',
            unsafe_allow_html=True
        )

    # Contenido principal
    if len(df_gastos) == 0 or 'Monto' not in df_gastos.columns:
        st.info("📝 No hay gastos registrados. ¡Agrega tu primer gasto en el panel lateral!")
    else:
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_gastos = df_gastos['Monto'].sum()
            st.metric("💵 Total Gastos", format_pesos(total_gastos))

        with col2:
            promedio = df_gastos['Monto'].mean()
            st.metric("📊 Promedio", format_pesos(promedio))

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

            # Opciones predefinidas (las mismas del formulario)
            todas_categorias = ["Alimentos", "Transporte", "Salud", "Educación",
                               "Entretenimiento", "Servicios", "Ropa", "Casa"]
            todos_metodos = ["BBVA", "Macro", "Naranja", "Santander", "Transferencia"]

            with col_filtro1:
                categorias_filtro = st.multiselect(
                    "Filtrar por categoría",
                    options=todas_categorias,
                    default=[]
                )

            with col_filtro2:
                metodos_filtro = st.multiselect(
                    "Filtrar por método de pago",
                    options=todos_metodos,
                    default=[]
                )

            # Aplicar filtros (si no hay filtros, mostrar todo)
            df_filtrado = df_gastos.copy()

            if len(categorias_filtro) > 0:
                df_filtrado = df_filtrado[df_filtrado['Categoría'].isin(categorias_filtro)]

            if len(metodos_filtro) > 0:
                df_filtrado = df_filtrado[df_filtrado['Método de Pago'].isin(metodos_filtro)]

            # Mostrar tabla con formato argentino en Monto
            df_display_table = df_filtrado.sort_values('Fecha', ascending=False).copy()
            df_display_table['Monto'] = df_display_table['Monto'].apply(lambda x: format_pesos(x))

            st.dataframe(
                df_display_table,
                use_container_width=True,
                hide_index=True
            )

            # Resumen del filtro
            st.info(f"📊 Mostrando {len(df_filtrado)} de {len(df_gastos)} transacciones | Total: {format_pesos(df_filtrado['Monto'].sum())}")

            # Sección para eliminar gastos
            st.markdown("---")
            with st.expander("🗑️ Eliminar Gasto"):
                st.warning("⚠️ Esta acción no se puede deshacer")

                # Crear una lista de gastos para seleccionar
                if len(df_gastos) > 0:
                    # Crear opciones de selección con formato legible
                    df_display = df_gastos.copy()
                    df_display['Fecha_str'] = df_display['Fecha'].dt.strftime('%d/%m/%Y')
                    df_display['Monto_str'] = df_display['Monto'].apply(lambda x: format_pesos(x))
                    df_display['display'] = (
                        df_display['Fecha_str'] + ' - ' +
                        df_display['Categoría'] + ' - ' +
                        df_display['Descripción'] + ' - ' +
                        df_display['Monto_str']
                    )

                    opciones = df_display['display'].tolist()

                    gasto_seleccionado = st.selectbox(
                        "Selecciona el gasto a eliminar:",
                        options=range(len(opciones)),
                        format_func=lambda x: opciones[x]
                    )

                    col_del1, col_del2 = st.columns([1, 3])
                    with col_del1:
                        if st.button("🗑️ Eliminar", type="primary", use_container_width=True):
                            # El índice en Google Sheets es +2 (1 para header, 1 para 0-indexing)
                            row_to_delete = gasto_seleccionado + 2

                            with st.spinner("Eliminando gasto..."):
                                if delete_expense_from_sheets(sheet, row_to_delete):
                                    st.success("✅ Gasto eliminado exitosamente!")
                                    st.rerun()
                                else:
                                    st.error("❌ Error al eliminar el gasto")
                else:
                    st.info("No hay gastos para eliminar")

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
                # Gráfico de distribución por método de pago con colores personalizados
                gastos_metodo = df_gastos.groupby('Método de Pago')['Monto'].sum()

                # Definir colores para cada método de pago
                color_map = {
                    'Santander': '#E30613',  # Rojo
                    'BBVA': '#004481',       # Azul
                    'Naranja': '#FF6900',    # Naranja
                    'Macro': '#003366',      # Azul oscuro
                    'Transferencia': '#00BFFF'  # Celeste
                }

                fig2 = px.pie(
                    values=gastos_metodo.values,
                    names=gastos_metodo.index,
                    title="Distribución por Método de Pago",
                    hole=0.4,
                    color=gastos_metodo.index,
                    color_discrete_map=color_map
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
