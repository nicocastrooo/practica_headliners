from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import pandas as pd


class GraficoRegresion(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Crear la figura de Matplotlib y el canvas para PySide6
        self.figura = Figure(figsize=(7, 4.5), dpi=100)
        self.canvas = FigureCanvas(self.figura)
        self.canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.layout.addWidget(self.canvas)

        # Garantizar altura mínima para que nunca se vea aplastado
        self.setMinimumHeight(350)

        # Añadir un eje a la figura
        self.ax = self.figura.add_subplot(111)
        self.limpiar_grafico()

    def limpiar_grafico(self):
        """Limpia el lienzo del gráfico y restaura su estado inicial."""
        self.ax.clear()
        self.ax.set_title("Ajuste del Modelo (Sin entrenar)")
        self.ax.grid(True, linestyle=":", alpha=0.5)
        self.figura.tight_layout()
        self.canvas.draw()

    def dibujar_grafico(
        self,
        df_train: pd.DataFrame,
        df_test: pd.DataFrame,
        features: list,
        target: str,
        modelo,
    ):
        """
        Dibuja el gráfico diferenciando entrada/salida y entrenamiento/test
        tanto en regresión simple como en regresión múltiple.
        """
        self.ax.clear()

        # Compatibilidad con ModeloLineal (modelo.estimador) o estimador directo
        estimador = modelo.estimador if hasattr(modelo, "estimador") else modelo

        # Separar variables de Entrada (X) y de Salida (y)
        X_train = df_train[features]
        y_train = df_train[target]
        X_test = df_test[features]
        y_test = df_test[target]

        if len(features) == 1:
            # REGRESIÓN SIMPLE: Entrada (X) vs Salida (Y)
            feature_name = features[0]

            # Nubes de puntos diferenciando Entrenamiento y Test por color y forma
            self.ax.scatter(
                X_train[feature_name],
                y_train,
                color="royalblue",
                marker="o",
                label="Entrenamiento (real)",
                alpha=0.6,
            )
            self.ax.scatter(
                X_test[feature_name],
                y_test,
                color="darkorange",
                marker="s",
                label="Test (real)",
                alpha=0.8,
            )

            # Recta de ajuste del modelo a lo largo de todo el rango de entrada
            x_min = min(X_train[feature_name].min(), X_test[feature_name].min())
            x_max = max(X_train[feature_name].max(), X_test[feature_name].max())
            x_line = np.linspace(x_min, x_max, 100)

            df_line = pd.DataFrame({feature_name: x_line})
            y_line = estimador.predict(df_line)

            self.ax.plot(
                x_line,
                y_line,
                color="crimson",
                linewidth=2,
                label="Recta de ajuste (predicción)",
            )

            # Etiquetas diferenciando Entrada y Salida
            self.ax.set_xlabel(f"Entrada: {feature_name}")
            self.ax.set_ylabel(f"Salida: {target}")
            self.ax.set_title(
                f"Regresión Simple — Salida ({target}) vs Entrada ({feature_name})"
            )

        else:
            # REGRESIÓN MÚLTIPLE: Salida Real vs Salida Predicha a partir de las Entradas
            y_pred_train = estimador.predict(X_train)
            y_pred_test = estimador.predict(X_test)

            # Nubes de puntos diferenciando Entrenamiento y Test por color y forma
            self.ax.scatter(
                y_train,
                y_pred_train,
                color="royalblue",
                marker="o",
                label="Entrenamiento (real vs predicho)",
                alpha=0.6,
            )
            self.ax.scatter(
                y_test,
                y_pred_test,
                color="darkorange",
                marker="s",
                label="Test (real vs predicho)",
                alpha=0.8,
            )

            # Recta ideal (Valor Real == Valor Predicho)
            min_val = min(
                y_train.min(), y_test.min(), y_pred_train.min(), y_pred_test.min()
            )
            max_val = max(
                y_train.max(), y_test.max(), y_pred_train.max(), y_pred_test.max()
            )

            self.ax.plot(
                [min_val, max_val],
                [min_val, max_val],
                color="crimson",
                linestyle="--",
                linewidth=2,
                label="Ajuste ideal (Real = Predicho)",
            )

            # Etiquetas diferenciando Salida Real, Salida Predicha y Entradas utilizadas
            entradas_txt = ", ".join(features)
            self.ax.set_xlabel(f"Valor real — Salida: {target}")
            self.ax.set_ylabel(f"Valor predicho — Salida: {target}")
            self.ax.set_title(
                f"Regresión Múltiple — Salida: {target} | Entradas: {entradas_txt}"
            )

        self.ax.legend(loc="best")
        self.ax.grid(True, linestyle=":", alpha=0.7)
        self.figura.tight_layout()
        self.canvas.draw()