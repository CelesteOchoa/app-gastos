# 💰 Sistema de Registro de Gastos Mensuales

## 📋 Descripción

Este es un programa moderno y fácil de usar para registrar y analizar tus gastos mensuales. Está basado en tu formato de Excel existente y te permite:

- ✅ Registrar gastos de forma rápida y sencilla
- 📊 Ver historial completo de gastos con filtros
- 📈 Analizar gastos con gráficos interactivos
- 💾 Exportar datos a Excel
- 📱 Interfaz web moderna y responsive

## 🚀 Cómo Ejecutar el Programa

### Paso 1: Abrir la terminal

En tu computadora, abre la terminal o línea de comandos:
- **Windows**: Presiona `Win + R`, escribe `cmd` y presiona Enter
- **Mac**: Presiona `Cmd + Espacio`, escribe `terminal` y presiona Enter
- **Linux**: Presiona `Ctrl + Alt + T`

### Paso 2: Navegar a la carpeta del programa

```bash
cd ruta/donde/guardaste/el/programa
```

### Paso 3: Ejecutar el programa

```bash
streamlit run app_gastos.py
```

### Paso 4: ¡Listo!

El programa se abrirá automáticamente en tu navegador en la dirección: `http://localhost:8501`

---

## 📖 Guía de Uso

### 1. 📝 Registrar un Gasto

1. Selecciona **"📝 Registrar Gasto"** en el menú lateral
2. Elige el tipo de gasto:
   - **💳 Gasto con Tarjeta**: Para compras con tarjeta de crédito
   - **💵 Gasto Fijo**: Para gastos recurrentes (alquiler, servicios, etc.)
   - **🛒 Gasto Variable**: Para gastos ocasionales
3. Completa los datos:
   - Fecha del gasto
   - Concepto (qué compraste)
   - Importe en pesos
   - Método de pago
   - Categoría (si aplica)
   - Notas adicionales (opcional)
4. Presiona **"💾 Guardar Gasto"**

### 2. 📊 Ver Gastos

1. Selecciona **"📊 Ver Gastos"** en el menú lateral
2. Usa los filtros para encontrar gastos específicos:
   - Por mes
   - Por categoría
   - Por tipo de gasto
3. Revisa las métricas en la parte superior:
   - Total gastado
   - Cantidad de gastos
   - Promedio
   - Gasto máximo
4. Mira el detalle completo en la tabla
5. Si quieres exportar, presiona **"📥 Exportar a Excel"**

### 3. 📈 Análisis

1. Selecciona **"📈 Análisis"** en el menú lateral
2. Explora los diferentes gráficos:
   - **Por Categoría**: Gráfico de torta que muestra la distribución de gastos
   - **Por Mes**: Evolución de tus gastos a lo largo del tiempo
   - **Por Método de Pago**: Cuánto gastas con cada tarjeta o método

### 4. ⚙️ Configuración

1. Selecciona **"⚙️ Configuración"** en el menú lateral
2. Aquí puedes:
   - Ver estadísticas generales
   - Reiniciar los datos (¡cuidado! esto borra todo)

---

## 💡 Características Principales

### ✨ Interfaz Moderna
- Diseño limpio y fácil de usar
- Colores organizados por secciones
- Responsive (funciona en cualquier dispositivo)

### 📊 Análisis Inteligente
- Gráficos interactivos (puedes hacer zoom, filtrar, etc.)
- Métricas automáticas
- Comparación mensual

### 💾 Gestión de Datos
- Los datos se guardan automáticamente
- Exportación a Excel con formato
- Respaldo en archivo JSON

### 🔒 Seguridad
- Todos los datos se guardan localmente en tu computadora
- No se envía información a internet
- Control total de tu información

---

## 📂 Archivos del Sistema

El programa crea los siguientes archivos:

- **app_gastos.py**: El programa principal (no modificar)
- **gastos_data.json**: Base de datos con tus gastos
- **gastos_FECHA.xlsx**: Archivos de exportación que generes

---

## 🎯 Tipos de Gastos

### 💳 Gasto con Tarjeta
Usa esta opción cuando pagues con tarjeta de crédito. Puedes especificar:
- Qué tarjeta usaste (BBVA, Naranja, Macro, etc.)
- Cantidad de cuotas
- El programa calculará automáticamente el impacto mensual

### 💵 Gasto Fijo
Para gastos que se repiten mensualmente:
- Alquiler
- Expensas
- Servicios (luz, gas, agua, internet)
- Terapia, gimnasio, etc.

### 🛒 Gasto Variable
Para compras ocasionales:
- Supermercado
- Restaurantes
- Ropa
- Entretenimiento
- Transporte

---

## ❓ Preguntas Frecuentes

### ¿Cómo importo mis datos del Excel existente?

Por ahora el programa empieza desde cero. Si quieres migrar datos antiguos, tendrías que ingresarlos manualmente o puedo crear una función de importación.

### ¿Puedo usar el programa en mi teléfono?

Sí, mientras el programa esté ejecutándose en tu computadora, puedes acceder desde tu teléfono usando la dirección IP de tu red local.

### ¿Qué pasa si cierro el navegador?

Los datos quedan guardados. Solo cierra el navegador y cuando vuelvas a abrir el programa, todo estará allí.

### ¿Cómo detengo el programa?

Ve a la terminal donde está corriendo y presiona `Ctrl + C`

---

## 🆘 Solución de Problemas

### El programa no inicia
- Asegúrate de tener Python instalado
- Verifica que todas las librerías estén instaladas
- Prueba ejecutar: `pip install streamlit pandas openpyxl plotly`

### No puedo ver los gráficos
- Actualiza tu navegador
- Prueba con otro navegador (Chrome, Firefox, Edge)

### Los datos no se guardan
- Verifica que tienes permisos de escritura en la carpeta
- El archivo `gastos_data.json` debe poder crearse/modificarse

---

## 📞 Soporte

Si tienes alguna pregunta o necesitas ayuda adicional, no dudes en consultar.

---

## 🎨 Personalización

Puedes personalizar:
- Las categorías de gastos
- Los métodos de pago
- Las tarjetas disponibles
- Los colores de la interfaz

Solo tienes que editar las listas al inicio del archivo `app_gastos.py`

---

**¡Disfruta registrando tus gastos de forma fácil y organizada!** 💰✨
