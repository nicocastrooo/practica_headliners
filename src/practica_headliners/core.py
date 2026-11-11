import os
import joblib
from sklearn.linear_model import LinearRegression

class ModelCore:
    def __init__(self):
        self.model_data = None
        self.has_unsaved_changes = False

    def create_model(self, X, y, description=""):
        """Crea y entrena un modelo, marcando cambios sin guardar."""
        model = LinearRegression()
        model.fit(X, y)
        
        self.model_data = {
            "model": model,
            "formula": self._generate_formula(model, X),
            "columns_in": list(X.columns) if hasattr(X, "columns") else [f"x_{i}" for i in range(X.shape[1])],
            "column_out": "y",
            "metrics": {"r2": model.score(X, y), "mse": 0.0},
            "description": description
        }
        self.has_unsaved_changes = True

    def update_description(self, new_description: str):
        """Actualiza la descripción y marca el estado como modificado (sin guardar)."""
        if self.model_data is None:
            raise ValueError("No hay ningún modelo cargado o creado para modificar.")
        self.model_data["description"] = new_description
        self.has_unsaved_changes = True

    def save_model(self, file_path: str):
        """Guarda el modelo en disco y resetea el estado de cambios sin guardar."""
        if self.model_data is None:
            raise ValueError("No hay ningún modelo para guardar.")
        
        joblib.dump(self.model_data, file_path)
        self.has_unsaved_changes = False

    def load_model(self, file_path: str):
        """
        Carga un modelo desde la ruta absoluta, validando existencia, 
        integridad del archivo y metadatos obligatorios.
        """
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"El archivo no existe en la ruta: {abs_path}")

        try:
            data = joblib.load(abs_path)
        except Exception as e:
            raise ValueError(f"El archivo está dañado o no tiene un formato válido: {e}")

        # Validación estricta de metadatos requeridos por la HU #24
        required_keys = ["model", "formula", "columns_in", "column_out", "metrics", "description"]
        if not isinstance(data, dict) or not all(key in data for key in required_keys):
            raise ValueError("El archivo no tiene el formato esperado o le faltan metadatos esenciales.")

        self.model_data = data
        self.has_unsaved_changes = False
        return self.model_data

    def _generate_formula(self, model, X):
        coefs = model.coef_
        intercept = model.intercept_
        cols = list(X.columns) if hasattr(X, "columns") else [f"x_{i}" for i in range(len(coefs))]
        terms = [f"{coef:.2f} * {col}" for coef, col in zip(coefs, cols)]
        return f"y = {intercept:.2f} + " + " + ".join(terms)