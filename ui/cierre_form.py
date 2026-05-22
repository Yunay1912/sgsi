# -*- coding: utf-8 -*-
"""
ui/cierre_form.py

Boleta de Cierre del Servicio - PySide6 UI (estructura corregida)
Versión ajustada según jerarquía visual de la boleta física.

Cambios:
- Empaste colocado después de Totales y Cantidades.
- Eliminadas firmas VB (Dirección Ejecutiva / Servicio Litográfico).
- “Detalle por Operador” sin título visible, tabla conservada.
- Observaciones al final del formulario.
"""

from PySide6 import QtCore, QtGui, QtWidgets
import os
import datetime


class Ui_CierreForm(object):
    def setupUi(self, CierreForm):
        CierreForm.setObjectName("CierreForm")
        CierreForm.setWindowTitle("Boleta de Cierre - Servicio Litográfico")

        font = QtGui.QFont()
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        CierreForm.setFont(font)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(12, 8, 12, 8)
        self.main_layout.setSpacing(8)

        # ---------- HEADER ----------
        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # Logo (vacío para futuro logo)
        self.logo_label = QtWidgets.QLabel()
        self.logo_label.setObjectName("logo_label")
        self.logo_label.setFixedSize(160, 80)
        self.logo_label.setAlignment(QtCore.Qt.AlignCenter)
        logo_path = "assets/logo_asamblea.png"  # Ruta del logo institucional
        pixmap = QtGui.QPixmap(logo_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(self.logo_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
        else:
            self.logo_label.setText("LOGO\nINSTITUCIONAL")
        header_layout.addWidget(self.logo_label, 0)

        # Title center
        title_widget = QtWidgets.QWidget()
        title_layout = QtWidgets.QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)
        self.lbl_title_line1 = QtWidgets.QLabel("BOLETA DE CIERRE DEL SERVICIO")
        f = self.lbl_title_line1.font()
        f.setPointSize(11)
        f.setBold(True)
        self.lbl_title_line1.setFont(f)
        self.lbl_title_line1.setAlignment(QtCore.Qt.AlignCenter)
        title_layout.addWidget(self.lbl_title_line1)

        self.lbl_title_line2 = QtWidgets.QLabel("REPORTE DIARIO - SERVICIO LITOGRÁFICO")
        self.lbl_title_line2.setAlignment(QtCore.Qt.AlignCenter)
        title_layout.addWidget(self.lbl_title_line2)
        header_layout.addWidget(title_widget, 1)

        # Fecha / Edificio / Firma pequeña
        right_header = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_header)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        self.lbl_fecha = QtWidgets.QLabel("Fecha:")
        self.txt_fecha = QtWidgets.QLineEdit()
        self.txt_fecha.setReadOnly(True)
        self.txt_fecha.setFixedWidth(120)
        self.txt_fecha.setText(datetime.date.today().strftime("%Y-%m-%d"))

        self.lbl_edificio = QtWidgets.QLabel("Edificio:")
        self.txt_edificio = QtWidgets.QLineEdit()
        self.txt_edificio.setFixedWidth(180)

        right_layout.addWidget(self.lbl_fecha, 0, QtCore.Qt.AlignRight)
        right_layout.addWidget(self.txt_fecha, 0, QtCore.Qt.AlignRight)
        right_layout.addSpacing(4)
        right_layout.addWidget(self.lbl_edificio, 0, QtCore.Qt.AlignRight)
        right_layout.addWidget(self.txt_edificio, 0, QtCore.Qt.AlignRight)
        right_layout.addSpacing(6)
        header_layout.addWidget(right_header, 0)
        self.main_layout.addWidget(header_widget)

        # Separator
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.main_layout.addWidget(sep)

        # ---------- DATOS GENERALES ----------
        self.grp_datos_generales = QtWidgets.QGroupBox("Datos Generales")
        datos_layout = QtWidgets.QGridLayout(self.grp_datos_generales)
        datos_layout.setContentsMargins(8, 8, 8, 8)
        datos_layout.setHorizontalSpacing(12)
        datos_layout.setVerticalSpacing(8)

        datos_layout.addWidget(QtWidgets.QLabel("Nombre del Operador:"), 0, 0)
        self.txt_nombre_operador = QtWidgets.QLineEdit()
        datos_layout.addWidget(self.txt_nombre_operador, 0, 1)

        datos_layout.addWidget(QtWidgets.QLabel("Número fotocopiadora:"), 1, 0)
        self.spn_num_fotocopiadora = QtWidgets.QSpinBox()
        self.spn_num_fotocopiadora.setRange(0, 5)
        self.spn_num_fotocopiadora.setFixedWidth(80)
        datos_layout.addWidget(self.spn_num_fotocopiadora, 1, 1)

        datos_layout.addWidget(QtWidgets.QLabel("Firma del Operador:"), 3, 0)
        self.btn_firma_operador = QtWidgets.QPushButton("Importar Firma (PDF/IMG)")
        self.btn_firma_operador.setObjectName("btn_firma_operador")
        datos_layout.addWidget(self.btn_firma_operador, 3, 2)
        self.preview_firma_operador = QtWidgets.QLabel()
        self.preview_firma_operador.setObjectName("preview_firma_operador")
        self.preview_firma_operador.setFrameShape(QtWidgets.QFrame.Box)
        self.preview_firma_operador.setFixedSize(180, 50)
        datos_layout.addWidget(self.preview_firma_operador, 3, 3, 1, 2)

        self.main_layout.addWidget(self.grp_datos_generales)

        # ---------- TOTALES / CANTIDADES ----------
        self.grp_totales = QtWidgets.QGroupBox("Totales y Cantidades")
        totals_layout = QtWidgets.QGridLayout()
        totals_layout.setContentsMargins(8, 8, 8, 8)
        totals_layout.setHorizontalSpacing(12)
        totals_layout.setVerticalSpacing(8)

        totals_layout.addWidget(QtWidgets.QLabel("Trabajos solicitados:"), 0, 0)
        self.spn_trabajos_solicitados = QtWidgets.QSpinBox()
        self.spn_trabajos_solicitados.setRange(0, 100000)
        totals_layout.addWidget(self.spn_trabajos_solicitados, 0, 1)

        totals_layout.addWidget(QtWidgets.QLabel("Impresos por llave:"), 0, 2)
        self.spn_impresos_llave = QtWidgets.QSpinBox()
        self.spn_impresos_llave.setRange(0, 100000)
        totals_layout.addWidget(self.spn_impresos_llave, 0, 3)

        totals_layout.addWidget(QtWidgets.QLabel("Impresos por correo:"), 1, 0)
        self.spn_impresos_email = QtWidgets.QSpinBox()
        self.spn_impresos_email.setRange(0, 100000)
        totals_layout.addWidget(self.spn_impresos_email, 1, 1)

        totals_layout.addWidget(QtWidgets.QLabel("Cantidad de documentos:"), 1, 2)
        self.spn_cant_documentos = QtWidgets.QSpinBox()
        self.spn_cant_documentos.setRange(0, 100000)
        totals_layout.addWidget(self.spn_cant_documentos, 1, 3)

        totals_layout.addWidget(QtWidgets.QLabel("Total copias (Color):"), 2, 0)
        self.spn_total_color = QtWidgets.QSpinBox()
        self.spn_total_color.setRange(0, 1000000)
        totals_layout.addWidget(self.spn_total_color, 2, 1)

        totals_layout.addWidget(QtWidgets.QLabel("Total copias (B/N):"), 2, 2)
        self.spn_total_bn = QtWidgets.QSpinBox()
        self.spn_total_bn.setRange(0, 1000000)
        totals_layout.addWidget(self.spn_total_bn, 2, 3)

        # Empaste Section (moved into Totales y Cantidades)
        totals_layout.addWidget(QtWidgets.QLabel("Empaste grapa con cinta:"), 3, 0)
        self.spin_empaste_grapa = QtWidgets.QSpinBox()
        self.spin_empaste_grapa.setMaximum(9999)
        totals_layout.addWidget(self.spin_empaste_grapa, 3, 1)

        totals_layout.addWidget(QtWidgets.QLabel("Empaste con resorte:"), 3, 2)
        self.spin_empaste_resorte = QtWidgets.QSpinBox()
        self.spin_empaste_resorte.setMaximum(9999)
        totals_layout.addWidget(self.spin_empaste_resorte, 3, 3)

        totals_layout.addWidget(QtWidgets.QLabel("Empaste de cuadernillo:"), 4, 0)
        self.spin_empaste_cuadernillo = QtWidgets.QSpinBox()
        self.spin_empaste_cuadernillo.setMaximum(9999)
        totals_layout.addWidget(self.spin_empaste_cuadernillo, 4, 1)

        totals_layout.addWidget(QtWidgets.QLabel("Acabado de portada de cartulina:"), 4, 2)
        self.spin_empaste_portada_cartulina = QtWidgets.QSpinBox()
        self.spin_empaste_portada_cartulina.setMaximum(9999)
        totals_layout.addWidget(self.spin_empaste_portada_cartulina, 4, 3)

        totals_layout.addWidget(QtWidgets.QLabel("Engomado:"), 5, 0)
        self.spin_empaste_engomado = QtWidgets.QSpinBox()
        self.spin_empaste_engomado.setMaximum(9999)
        totals_layout.addWidget(self.spin_empaste_engomado, 5, 1)

        totals_layout.addWidget(QtWidgets.QLabel("Guillotina:"), 5, 2)
        self.spin_empaste_guillotina = QtWidgets.QSpinBox()
        self.spin_empaste_guillotina.setMaximum(9999)
        totals_layout.addWidget(self.spin_empaste_guillotina, 5, 3)

        totals_layout.addWidget(QtWidgets.QLabel("Escaneo (páginas):"), 6, 0)
        self.spin_empaste_paginas_escaneo = QtWidgets.QSpinBox()
        self.spin_empaste_paginas_escaneo.setMaximum(99999)
        totals_layout.addWidget(self.spin_empaste_paginas_escaneo, 6, 1)

        totals_layout.addWidget(QtWidgets.QLabel("Copias de prueba:"), 6, 2)
        self.spin_copias_prueba = QtWidgets.QSpinBox()
        self.spin_copias_prueba.setMaximum(9999)
        totals_layout.addWidget(self.spin_copias_prueba, 6, 3)

        # Add layout to the group box
        self.grp_totales.setLayout(totals_layout)
        self.main_layout.addWidget(self.grp_totales)


        # ---------- DETALLE ----------
        self.tbl_detalle = QtWidgets.QTableWidget()
        self.tbl_detalle.setObjectName("tbl_detalle")
        self.tbl_detalle.setColumnCount(6)
        self.tbl_detalle.setHorizontalHeaderLabels([
            "Contador Inicial",
            "Contador Final",
            "Copias Dañadas",
            "Copias de Prueba",
            "Personas Atendidas",
            "Firma del Operador"
        ])
        self.tbl_detalle.setRowCount(5)
        self.tbl_detalle.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tbl_detalle.verticalHeader().setVisible(False)
        self.tbl_detalle.setMaximumHeight(260)

        self._firmas_operadores = {}
        for row in range(5):
            for col in range(6):
                if col < 5:
                    spin = QtWidgets.QSpinBox()
                    spin.setRange(0, 999999)
                    spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
                    spin.setAlignment(QtCore.Qt.AlignCenter)
                    self.tbl_detalle.setCellWidget(row, col, spin)
                else:
                    firma_widget = QtWidgets.QWidget()
                    firma_layout = QtWidgets.QHBoxLayout(firma_widget)
                    firma_layout.setContentsMargins(2, 2, 2, 2)
                    firma_layout.setSpacing(4)
                    btn = QtWidgets.QPushButton("Importar Firma")
                    btn.setFixedWidth(120)
                    preview = QtWidgets.QLabel()
                    preview.setFrameShape(QtWidgets.QFrame.Box)
                    preview.setFixedSize(160, 60)
                    preview.setAlignment(QtCore.Qt.AlignCenter)
                    preview.setText("Sin firma")
                    firma_layout.addWidget(btn)
                    firma_layout.addWidget(preview)
                    btn.clicked.connect(lambda _, r=row, p=preview: self._on_import_firma_operador(r, p))
                    self.tbl_detalle.setCellWidget(row, col, firma_widget)

        self.main_layout.addWidget(self.tbl_detalle)

        # ---------- OBSERVACIONES ----------
        self.lbl_observaciones = QtWidgets.QLabel("Observaciones / Otros:")
        self.txt_observaciones = QtWidgets.QPlainTextEdit()
        self.txt_observaciones.setFixedHeight(100)
        self.main_layout.addWidget(self.lbl_observaciones)
        self.main_layout.addWidget(self.txt_observaciones)

        # ---------- BOTONES ----------
        footer_btns_widget = QtWidgets.QWidget()
        footer_btns_layout = QtWidgets.QHBoxLayout(footer_btns_widget)
        footer_btns_layout.setContentsMargins(0, 0, 0, 0)
        footer_btns_layout.addStretch(1)

        self.btn_guardar = QtWidgets.QPushButton("Guardar")
        self.btn_cancelar = QtWidgets.QPushButton("Cancelar")
        self.btn_enviar = QtWidgets.QPushButton("Enviar")
        self.btn_enviar.setEnabled(False)

        footer_btns_layout.addWidget(self.btn_guardar)
        footer_btns_layout.addWidget(self.btn_cancelar)
        footer_btns_layout.addWidget(self.btn_enviar)
        self.main_layout.addWidget(footer_btns_widget)
        self.main_layout.addStretch()

        # ---------- Firmas internas ----------
        self._firma_small_path = None

    # ---------------------- Helpers ----------------------
    def _import_file_and_preview(self, parent_widget, preview_label: QtWidgets.QLabel):
        caption = "Seleccionar archivo de firma (PDF/IMG/OTRO)"
        filters = "PDF Files (*.pdf);;Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(parent_widget, caption, "", filters)
        if not file_path:
            return None
        lower = file_path.lower()
        if lower.endswith((".png", ".jpg", ".jpeg", ".bmp")):
            pix = QtGui.QPixmap(file_path)
            if not pix.isNull():
                scaled = pix.scaled(preview_label.width(), preview_label.height(),
                                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                preview_label.setPixmap(scaled)
            else:
                preview_label.setText(os.path.basename(file_path))
        elif lower.endswith(".pdf"):
            preview_label.setText(f"PDF: {os.path.basename(file_path)}")
        else:
            preview_label.setText(os.path.basename(file_path))
        return file_path

    def _on_import_small_firma(self):
        path = self._import_file_and_preview(self.lbl_logo, self.lbl_logo)
        if path:
            self._firma_small_path = path

    def _on_import_firma_operador(self, row, preview_label):
        path = self._import_file_and_preview(self.tbl_detalle, preview_label)
        if path:
            self._firmas_operadores[row] = path


# ------------------------ Ejecutable de prueba ------------------------
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    window.setWindowTitle("Boleta de Cierre - Servicio Litográfico")
    scroll = QtWidgets.QScrollArea()
    scroll.setWidgetResizable(True)
    content = QtWidgets.QWidget()
    ui = Ui_CierreForm()
    ui.setupUi(content)
    content.setLayout(ui.main_layout)
    scroll.setWidget(content)
    window.setCentralWidget(scroll)
    window.resize(800, 600)
    screen = app.primaryScreen().availableGeometry()
    window.move((screen.width() - window.width()) // 2, (screen.height() - window.height()) // 2)
    window.show()
    sys.exit(app.exec())
