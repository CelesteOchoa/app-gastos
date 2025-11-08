import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
import gspread
from google.oauth2 import service_account
from io import BytesIO
import openpyxl

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

def initialize_sheet(sheet):
    try:
        if len(sheet.get_all_values()) == 0:
            headers = ['Fecha', 'Categoría', 'Descripción', 'Monto', 'Método de Pago']
            sheet.append_row(headers)
    except Exception as e:
        st.error(f"Error al inicializar hoja: {str(e)}")

def main():
    st.markdown('<h1 class="main-header">💰 Registro de Gastos</h1>', unsafe_allow_html=True)
    sheet = get_google_sheet()
    if sheet is None:
        st.error("⚠️ No se pudo conectar con Google Sheets. Verifica la configuración de Secrets.")
        return
    initialize_sheet(sheet)
    df_gastos = load_data_from_sheets()
    # Sidebar para agregar un nuevo gasto ...
    # Resto del código de funcionalidad...

if __name__ == "__main__":
    main()
