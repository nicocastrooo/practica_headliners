def __init__(self):
    super().__init__()
    
    # Añade aquí las variables de estado para la HU #24:
    self.has_unsaved_changes = False
    self.ruta_modelo_actual = None
    self.modelo_actual = None