# Optimización de Rendimiento en Tablas Masivas

## Técnica Elegida
Para el manejo visual de datasets de gran volumen (como el dataset de ejemplo de +20.000 filas), se ha implementado un sistema de **Paginación Guiada por Modelo** en la capa gráfica (`TablaDatos`).

El sistema divide el DataFrame original en bloques fijos de visualización (100 filas por página), y expone a través de un `QAbstractTableModel` únicamente el "slice" de memoria correspondiente a la página actual.

## Motivos de la Elección
1. **Consumo estable de Memoria y CPU:** Aunque la arquitectura *Model/View* de Qt (mediante `QAbstractTableModel`) aplica por defecto un comportamiento similar al *Virtual Scroll* (solo renderiza celdas visibles), exigirle a la GUI que mantenga un cálculo de coordenadas y barras de *scroll* sobre 20.000 filas provoca micropausas, cuellos de botella en la actualización del layout y saltos erráticos al deslizar.
2. **Claridad del Flujo (UX):** La paginación explícita (con controles de navegación *"Anterior"* y *"Siguiente"*) evita la sensación de "pérdida infinita" en el scroll y permite al usuario saber en qué bloque del dataset se encuentra exactamente.
3. **Escalabilidad O(1):** Con la paginación, el coste gráfico y computacional de renderizar el dataset es siempre constante (`O(1)`), ya tenga 2.000, 20.000 o 2 millones de registros.

## Comportamiento antes y después

**Antes del cambio (Enfoque crudo o dependiente de la API nativa de scroll):**
* **Comportamiento:** Al cargar el archivo masivo, la barra de desplazamiento generaba un lag perceptible al moverse verticalmente rápido. El motor de PySide6 se sobrecargaba actualizando miles de identificadores visuales en el margen de la tabla en un solo repintado de ventana.

**Después del cambio (Paginación con bloque fijo):**
* **Comportamiento:** La carga inicial en pantalla de la tabla y los controles es instantánea. 
* El usuario visualiza 100 filas cada vez. Al hacer clic en "Siguiente", el modelo notifica a la vista (`beginResetModel()`) y refresca inmediatamente los datos visibles.
* La ventana en ningún momento se congela, garantizando la fluidez, resiliencia visual y experiencia de usuario ininterrumpida que exige la HU #37.