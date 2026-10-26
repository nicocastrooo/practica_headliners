from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QButtonGroup, QGroupBox, QLabel, QLineEdit,
                               QMessageBox, QPushButton, QRadioButton,
                               QVBoxLayout)

from practica_headliners.preprocesado import (
    ErrorPreprocesado, detectar_valores_inexistentes,
    tratar_valores_inexistentes)

ESTRATEGIAS = [
    ("Eliminar filas con valores inexistentes", "eliminar_filas"),
    ("Rellenar con la media", "media"),
    ("Rellenar con la mediana", "mediana"),
    ("Rellenar con un valor constante", "valor_constante"),
]
TEXTO_INICIAL = "Separa los datos para detectar valores inexistentes."


class PanelPreprocesado(QGroupBox):
    """Detección y tratamiento de valores inexistentes."""

    aplicado = Signal(object, object)  # (entrenamiento, test) tratados

    def __init__(self, parent=None):
        super().__init__("Preprocesado", parent)
        self._train = None
        self._test = None
        self._columnas = []

        capa = QVBoxLayout(self)
        self.lbl_deteccion = QLabel(TEXTO_INICIAL)
        capa.addWidget(self.lbl_deteccion)

        self.radios = {}
        grupo = QButtonGroup(self)
        for texto, clave in ESTRATEGIAS:
            radio = QRadioButton(texto)
            grupo.addButton(radio)
            capa.addWidget(radio)
            self.radios[clave] = radio
        self.radios["eliminar_filas"].setChecked(True)

        self.txt_constante = QLineEdit()
        self.txt_constante.setPlaceholderText("Valor constante")
        self.txt_constante.setEnabled(False)
        self.radios["valor_constante"].toggled.connect(
            self.txt_constante.setEnabled)
        capa.addWidget(self.txt_constante)

        self.btn_aplicar = QPushButton("Aplicar preprocesado")
        self.btn_aplicar.clicked.connect(self._aplicar)
        capa.addWidget(self.btn_aplicar)

        self.invalidar()

    # --- API para la ventana ---
    def establecer_conjuntos(self, entrenamiento, test, columnas):
        """Recibe los conjuntos recién separados y muestra la detección."""
        self._train, self._test = entrenamiento, test
        self._columnas = list(columnas)
        self.setEnabled(True)
        self._mostrar_deteccion()

    def invalidar(self):
        """Descarta el estado: obliga a separar y preprocesar de nuevo."""
        self._train = self._test = None
        self._columnas = []
        self.lbl_deteccion.setText(TEXTO_INICIAL)
        self.setEnabled(False)

    def hay_pendientes(self):
        """True si no hay conjuntos o quedan NaN en las columnas."""
        if self._train is None:
            return True
        return self._contar() > 0

    # --- internos ---
    def _conteo(self):
        return detectar_valores_inexistentes(
            self._train, self._test, self._columnas)

    def _contar(self):
        conteo = self._conteo()
        return (sum(conteo["entrenamiento"].values())
                + sum(conteo["test"].values()))

    def _mostrar_deteccion(self):
        if self._contar() == 0:
            self.lbl_deteccion.setText(
                "No hay valores inexistentes. Puedes continuar sin "
                "preprocesar.")
            return
        conteo = self._conteo()
        lineas = [
            f"{c}: entrenamiento {conteo['entrenamiento'][c]}, "
            f"test {conteo['test'][c]}"
            for c in self._columnas
        ]
        self.lbl_deteccion.setText(
            "Valores inexistentes por columna:\n" + "\n".join(lineas))

    def _estrategia(self):
        return next(k for k, r in self.radios.items() if r.isChecked())

    def _aplicar(self):
        estrategia = self._estrategia()
        constante = None
        if estrategia == "valor_constante":
            texto = self.txt_constante.text().strip().replace(",", ".")
            constante = texto or None
        try:
            train, test, resumen = tratar_valores_inexistentes(
                self._train, self._test, self._columnas,
                estrategia, constante)
        except ErrorPreprocesado as error:
            QMessageBox.warning(self, "No se aplicó el preprocesado",
                                str(error))
            return  # el estado no cambia: se puede reintentar

        self._train, self._test = train, test
        self._mostrar_deteccion()

        accion = ("Filas eliminadas" if estrategia == "eliminar_filas"
                  else "Valores rellenados")
        mensaje = (f"{accion}:\n"
                   f"  Entrenamiento: {resumen['entrenamiento']}\n"
                   f"  Test: {resumen['test']}")
        if self._contar() > 0:
            mensaje += ("\n\nAún quedan valores inexistentes (por ejemplo, "
                        "una columna sin datos en entrenamiento).")
        QMessageBox.information(self, "Preprocesado aplicado", mensaje)
        self.aplicado.emit(train, test)
