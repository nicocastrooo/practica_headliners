from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import pandas as pd

class GraficoRegresion(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Crear la figura de Matplotlib y el canvas para PySide6
        self.figura = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvas(self.figura)
        self.layout.addWidget(self.canvas)
        
        # Añadir un eje a la figura
        self.ax = self.figura.add_subplot(111)
        self.ax.set_title("Ajuste del Modelo")

    def dibujar_grafico(self, df_train: pd.DataFrame, df_test: pd.DataFrame, features: list, target: str, modelo):
        """
        Dibuja el gráfico dependiendo de si es regresión simple o múltiple.
        Limpia el gráfico anterior automáticamente al ser llamado de nuevo.
        """
        self.ax.clear()

        # Separar X e Y
        X_train = df_train[features]
        y_train = df_train[target]
        X_test = df_test[features]
        y_test = df_test[target]

        if len(features) == 1:
            # REGRESIÓN SIMPLE: Variable vs Variable
            feature_name = features[0]
            
            # Puntos reales
            self.ax.scatter(X_train[feature_name], y_train, color='blue', marker='o', label='Entrenamiento', alpha=0.6)
            self.ax.scatter(X_test[feature_name], y_test, color='orange', marker='s', label='Test', alpha=0.8)
            
            # Recta de ajuste del modelo
            x_min = min(X_train[feature_name].min(), X_test[feature_name].min())
            x_max = max(X_train[feature_name].max(), X_test[feature_name].max())
            x_line = np.linspace(x_min, x_max, 100)
            
            # Crear un DataFrame con el mismo nombre de columna para el predict
            df_line = pd.DataFrame({feature_name: x_line})
            y_line = modelo.predict(df_line)
            
            self.ax.plot(x_line, y_line, color='red', linewidth=2, label='Recta de ajuste')
            
            # Etiquetas
            self.ax.set_xlabel(feature_name)
            self.ax.set_ylabel(target)
            self.ax.set_title(f"Regresión Simple: {target} vs {feature_name}")

        else:
            # REGRESIÓN MÚLTIPLE: Valores Reales vs Predichos
            y_pred_train = modelo.predict(X_train)
            y_pred_test = modelo.predict(X_test)
            
            # Nubes de puntos
            self.ax.scatter(y_train, y_pred_train, color='blue', marker='o', label='Entrenamiento', alpha=0.6)
            self.ax.scatter(y_test, y_pred_test, color='orange', marker='s', label='Test', alpha=0.8)
            
            # Recta ideal (Valor Real == Valor Predicho)
            min_val = min(y_train.min(), y_test.min(), y_pred_train.min(), y_pred_test.min())
            max_val = max(y_train.max(), y_test.max(), y_pred_train.max(), y_pred_test.max())
            
            self.ax.plot([min_val, max_val], [min_val, max_val], color='red', linestyle='--', linewidth=2, label='Coincidencia ideal')
            
            # Etiquetas
            self.ax.set_xlabel("Valor real")
            self.ax.set_ylabel("Valor predicho")
            self.ax.set_title(f"Regresión Múltiple: Predicciones de {target}")

        self.ax.legend()
        self.ax.grid(True, linestyle=':', alpha=0.7)
        self.canvas.draw()