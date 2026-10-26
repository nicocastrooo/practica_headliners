# Práctica Headliners - GIA IS

Repositorio oficial del proyecto de desarrollo de software para la asignatura de Ingeniería del Software (GIA - UDC).

> **Estado de la versión:** `v0.1.0` (Pre-release)  
> Aplicación en fase de desarrollo enfocada en la carga, exploración y preprocesamiento de datos para machine learning mediante una interfaz gráfica (GUI).

---

## 🚀 Funcionalidades Incluidas (v0.1.0)

Esta primera versión del proyecto incluye el flujo completo de preparación de datos:
* **Importación y lectura de datasets:** Soporte para cargar archivos de datos de ejemplo desde la carpeta local `data/` directamente en la interfaz gráfica.
* **Selección de columnas:** Capacidad para seleccionar las columnas de interés con las que se va a trabajar en el modelo.
* **Separeración Train/Test:** División interactiva del dataset en conjuntos de entrenamiento y prueba.
* **Detección y preprocesamiento de nulos:** 
  * Detección automática y visualización del número de valores inexistentes (NaN) por columna (desglosado en train y test).
  * Aplicación de 4 estrategias de tratamiento: *Eliminar filas*, *Media*, *Mediana* y *Valor constante*.
  * Validación de errores en tiempo real y bloqueo condicional de la creación de modelos hasta limpiar los nulos.

---

## 📋 Requisitos del Sistema

* **Python** `>=3.12`
* **uv** (Gestor de paquetes moderno para Python) instalado en el sistema.

---

## 🛠️ Guía de Instalación y Despliegue

Para clonar y poner en entorno de desarrollo local, sigue estos pasos:

### 1. Clonar el repositorio
Abre tu terminal y ejecuta:
```bash
git clone [https://github.com/nicocastrooo/practica_headliners.git](https://github.com/nicocastrooo/practica_headliners.git)
cd practica_headliners
2. Sincronizar el entorno e instalar dependencias con uv
Gracias al gestor uv, puedes instalar automáticamente el entorno virtual y todas las dependencias del proyecto ejecutando:

Bash
uv sync
3. Ejecutar la aplicación
Una vez instalado el entorno, arranca la interfaz gráfica de la aplicación con:

Bash
uv run python main.py
(Nota: Asegúrate de comprobar el archivo de configuración si el punto de entrada principal tuviera otra ruta).

📂 Datasets de Ejemplo
La aplicación incluye soporte para pruebas utilizando los datasets almacenados en la carpeta local data/. Puedes utilizarlos para validar el flujo completo de carga, selección, partición y preprocesado.
