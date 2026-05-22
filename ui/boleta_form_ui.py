# ui/boleta_form_ui.py
from PySide6 import QtCore, QtGui, QtWidgets
import os
import datetime

class Ui_BoletaForm(object):
    def setupUi(self, BoletaForm):
        BoletaForm.setObjectName("BoletaForm")
        BoletaForm.setWindowTitle("Boleta de Solicitud del Servicio")

        # Fuente base
        font = QtGui.QFont()
        font.setFamily("Sans Serif")
        font.setPointSize(10)
        BoletaForm.setFont(font)

        # Layout principal vertical
        self.main_layout = QtWidgets.QVBoxLayout(BoletaForm)
        self.main_layout.setObjectName("main_layout")
        self.main_layout.setContentsMargins(12, 8, 12, 8)
        self.main_layout.setSpacing(8)

        # Encabezado: logo a la izquierda, titulo en el centro, fecha y firma rápida a la derecha
        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # Logo (vacío para futuro logo)
        self.logo_label = QtWidgets.QLabel()
        self.logo_label.setObjectName("logo_label")
        self.logo_label.setFixedSize(150, 70)
        self.logo_label.setAlignment(QtCore.Qt.AlignCenter)
        logo_path = "assets/logo_asamblea.png"  # Ruta del logo institucional
        pixmap = QtGui.QPixmap(logo_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(self.logo_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
        header_layout.addWidget(self.logo_label, 0)

        # Título central (multi-línea para imitar boleta)
        title_widget = QtWidgets.QWidget()
        title_layout = QtWidgets.QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)
        self.title_label_line1 = QtWidgets.QLabel("BOLETA DE SOLICITUD DEL SERVICIO \"USUARIO\"")
        self.title_label_line1.setObjectName("title_label_line1")
        font_title = QtGui.QFont()
        font_title.setPointSize(11)
        font_title.setBold(True)
        self.title_label_line1.setFont(font_title)
        self.title_label_line1.setAlignment(QtCore.Qt.AlignCenter)
        title_layout.addWidget(self.title_label_line1)

        self.title_label_line2 = QtWidgets.QLabel("SERVICIO LITOGRÁFICO - ÁREA DE MANTENIMIENTO")
        self.title_label_line2.setObjectName("title_label_line2")
        self.title_label_line2.setAlignment(QtCore.Qt.AlignCenter)
        title_layout.addWidget(self.title_label_line2)

        header_layout.addWidget(title_widget, 1)

        # Fecha y firma pequeña a la derecha
        right_header = QtWidgets.QWidget()
        right_header_layout = QtWidgets.QVBoxLayout(right_header)
        right_header_layout.setContentsMargins(0, 0, 0, 0)
        right_header_layout.setSpacing(6)
        # Fecha (autocompletada)
        self.label_fecha = QtWidgets.QLabel("Fecha:")
        self.input_fecha = QtWidgets.QLineEdit()
        self.input_fecha.setObjectName("input_fecha")
        self.input_fecha.setReadOnly(True)
        self.input_fecha.setFixedWidth(120)
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.input_fecha.setText(today)
        # Firma pequeña (preview de firma o botón)
        self.small_firma_btn = QtWidgets.QPushButton("Firma")
        self.small_firma_btn.setObjectName("small_firma_btn")
        self.small_firma_btn.setFixedWidth(120)
        # organizar
        right_header_layout.addWidget(self.label_fecha, 0, QtCore.Qt.AlignRight)
        right_header_layout.addWidget(self.input_fecha, 0, QtCore.Qt.AlignRight)
        right_header_layout.addWidget(self.small_firma_btn, 0, QtCore.Qt.AlignRight)
        header_layout.addWidget(right_header, 0)

        self.main_layout.addWidget(header_widget)

        # ---------------- Datos del solicitante ----------------
        self.group_datos_solicitante = QtWidgets.QGroupBox("PARA USO EXCLUSIVO DEL USUARIO")
        self.group_datos_solicitante.setObjectName("group_datos_solicitante")
        datos_layout = QtWidgets.QFormLayout(self.group_datos_solicitante)
        datos_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        datos_layout.setFormAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.input_area = QtWidgets.QLineEdit()
        self.input_area.setObjectName("input_area")
        datos_layout.addRow("Área / Departamento:", self.input_area)

        self.input_nombre_usuario = QtWidgets.QLineEdit()
        self.input_nombre_usuario.setObjectName("input_nombre_usuario")
        datos_layout.addRow("Nombre completo del Usuario Autorizado:", self.input_nombre_usuario)

        self.input_nombre_documento = QtWidgets.QLineEdit()
        self.input_nombre_documento.setObjectName("input_nombre_documento")
        datos_layout.addRow("Nombre del Documento:", self.input_nombre_documento)

        self.main_layout.addWidget(self.group_datos_solicitante)

        # ---------------- Seleccionar el servicio (uso exclusivo del usuario) ----------------
        self.group_seleccionar_servicio = QtWidgets.QGroupBox("")
        self.group_seleccionar_servicio.setObjectName("group_seleccionar_servicio")
        servicio_layout = QtWidgets.QGridLayout(self.group_seleccionar_servicio)
        servicio_layout.setContentsMargins(8, 8, 8, 8)
        servicio_layout.setHorizontalSpacing(12)
        servicio_layout.setVerticalSpacing(8)

        # Row 0: instruction label full width 
        label_marca_x = QtWidgets.QLabel("Marque con X el servicio a utilizar:")
        servicio_layout.addWidget(label_marca_x, 0, 0, 1, 4)

        # === Fila 1: Servicios principales ===
        self.chk_fotocopiado = QtWidgets.QCheckBox("Fotocopiado")
        self.chk_impresion_llave = QtWidgets.QCheckBox("Impresión por medio de llave maya")
        self.chk_impresion_email = QtWidgets.QCheckBox("Impresión correo electrónico")

        servicio_layout.addWidget(self.chk_fotocopiado, 1, 0)
        servicio_layout.addWidget(self.chk_impresion_llave, 1, 1, 1, 2)
        servicio_layout.addWidget(self.chk_impresion_email, 1, 3, 1, 1)

        # === Nueva fila: título "Servicios:" ===
        label_servicios = QtWidgets.QLabel("Servicios:")
        servicio_layout.addWidget(label_servicios, 2, 0, 1, 4)

        # === Fila 3 y 4: Servicios de empaste (en horizontal, 4 columnas) ===
        self.chk_empaste_grapa = QtWidgets.QCheckBox("Empaste grapa con cinta")
        self.chk_empaste_resorte = QtWidgets.QCheckBox("Empaste con resorte")
        self.chk_empaste_cuadernillo = QtWidgets.QCheckBox("Empaste de cuadernillo")
        self.chk_empaste_portada = QtWidgets.QCheckBox("Acabado de portada de cartulina")
        self.chk_empaste_engomado = QtWidgets.QCheckBox("Engomado")
        self.chk_empaste_guillotina = QtWidgets.QCheckBox("Guillotina")

        servicio_layout.addWidget(self.chk_empaste_grapa, 3, 0)
        servicio_layout.addWidget(self.chk_empaste_resorte, 3, 1)
        servicio_layout.addWidget(self.chk_empaste_cuadernillo, 3, 2)
        servicio_layout.addWidget(self.chk_empaste_portada, 3, 3)
        servicio_layout.addWidget(self.chk_empaste_engomado, 4, 0)
        servicio_layout.addWidget(self.chk_empaste_guillotina, 4, 1)

        # === Escaneo (checkbox + campo de correo) ===
        self.chk_escaneo_email = QtWidgets.QCheckBox("Escaneo (correo electrónico):")
        self.chk_escaneo_email.setObjectName("chk_escaneo_email")

        self.txt_email_escaneo = QtWidgets.QLineEdit()
        self.txt_email_escaneo.setPlaceholderText("usuario@correo.com")

        # Colocar checkbox y campo en la misma fila
        servicio_layout.addWidget(self.chk_escaneo_email, 4, 2)
        servicio_layout.addWidget(self.txt_email_escaneo, 4, 3)

        # === Cantidad de copias ===
        label_copias = QtWidgets.QLabel("Cantidad de copias:")
        servicio_layout.addWidget(label_copias, 5, 0, 1, 4)

        self.grid_copias = QtWidgets.QGridLayout()
        self.grid_copias.setHorizontalSpacing(10)
        self.grid_copias.setVerticalSpacing(6)

        self.spin_copias_color = QtWidgets.QSpinBox()
        self.spin_copias_color.setMaximum(99999)
        self.spin_copias_bn = QtWidgets.QSpinBox()
        self.spin_copias_bn.setMaximum(99999)
        self.spin_total_copias = QtWidgets.QSpinBox()
        self.spin_total_copias.setMaximum(999999)
        self.spin_cantidad_documentos = QtWidgets.QSpinBox()
        self.spin_cantidad_documentos.setMaximum(99999)

        self.grid_copias.addWidget(QtWidgets.QLabel("Copias a color:"), 0, 0)
        self.grid_copias.addWidget(self.spin_copias_color, 0, 1)
        self.grid_copias.addWidget(QtWidgets.QLabel("Copias B/N:"), 0, 2)
        self.grid_copias.addWidget(self.spin_copias_bn, 0, 3)
        self.grid_copias.addWidget(QtWidgets.QLabel("Total de copias:"), 1, 0)
        self.grid_copias.addWidget(self.spin_total_copias, 1, 1)
        self.grid_copias.addWidget(QtWidgets.QLabel("Cantidad de documentos:"), 1, 2)
        self.grid_copias.addWidget(self.spin_cantidad_documentos, 1, 3)

        servicio_layout.addLayout(self.grid_copias, 6, 0, 1, 4)

        # === Observaciones ===
        servicio_layout.addWidget(QtWidgets.QLabel("Observaciones:"), 7, 0)
        self.text_observaciones_servicio = QtWidgets.QPlainTextEdit()
        self.text_observaciones_servicio.setObjectName("text_observaciones_servicio")
        self.text_observaciones_servicio.setFixedHeight(100)
        servicio_layout.addWidget(self.text_observaciones_servicio, 8, 0, 1, 4)

        self.main_layout.addWidget(self.group_seleccionar_servicio)

        # ---------------- Servicio de Empaste ----------------
        self.group_empaste = QtWidgets.QGroupBox("USO EXCLUSIVO DEL OPERADOR")
        self.group_empaste.setObjectName("group_empaste")
        empaste_layout = QtWidgets.QGridLayout(self.group_empaste)
        empaste_layout.setContentsMargins(8, 8, 8, 8)
        empaste_layout.setHorizontalSpacing(12)
        empaste_layout.setVerticalSpacing(8)

        empaste_layout.addWidget(QtWidgets.QLabel("Con grapa con cinta:"), 0, 0)
        self.spin_empaste_grapa = QtWidgets.QSpinBox()
        self.spin_empaste_grapa.setMaximum(9999)
        empaste_layout.addWidget(self.spin_empaste_grapa, 0, 1)

        empaste_layout.addWidget(QtWidgets.QLabel("Con resorte:"), 0, 2)
        self.spin_empaste_resorte = QtWidgets.QSpinBox()
        self.spin_empaste_resorte.setMaximum(9999)
        empaste_layout.addWidget(self.spin_empaste_resorte, 0, 3)

        empaste_layout.addWidget(QtWidgets.QLabel("Con cuadernillo:"), 1, 0)
        self.spin_empaste_cuadernillo = QtWidgets.QSpinBox()
        self.spin_empaste_cuadernillo.setMaximum(9999)
        empaste_layout.addWidget(self.spin_empaste_cuadernillo, 1, 1)

        empaste_layout.addWidget(QtWidgets.QLabel("Con Acabado de portada de cartulina:"), 1, 2)
        self.spin_empaste_portada_cartulina = QtWidgets.QSpinBox()
        self.spin_empaste_portada_cartulina.setMaximum(9999)
        empaste_layout.addWidget(self.spin_empaste_portada_cartulina, 1, 3)

        empaste_layout.addWidget(QtWidgets.QLabel("Con Engomado:"), 2, 0)
        self.spin_empaste_engomado = QtWidgets.QSpinBox()
        self.spin_empaste_engomado.setMaximum(9999)
        empaste_layout.addWidget(self.spin_empaste_engomado, 2, 1)

        empaste_layout.addWidget(QtWidgets.QLabel("Con Guillotina:"), 2, 2)
        self.spin_empaste_guillotina = QtWidgets.QSpinBox()
        self.spin_empaste_guillotina.setMaximum(9999)
        empaste_layout.addWidget(self.spin_empaste_guillotina, 2, 3)

        empaste_layout.addWidget(QtWidgets.QLabel("Escaneo (páginas):"), 3, 0)
        self.spin_empaste_paginas_escaneo = QtWidgets.QSpinBox()
        self.spin_empaste_paginas_escaneo.setMaximum(99999)
        empaste_layout.addWidget(self.spin_empaste_paginas_escaneo, 3, 1)

        empaste_layout.addWidget(QtWidgets.QLabel("Copias de prueba:"), 3, 2)
        self.spin_copias_prueba = QtWidgets.QSpinBox()
        self.spin_copias_prueba.setMaximum(9999)
        empaste_layout.addWidget(self.spin_copias_prueba, 3, 3)

        # 🔧 Ajustar las columnas para adaptarse al ancho de la ventana
        for i in range(4):
            servicio_layout.setColumnStretch(i, 1)
            empaste_layout.setColumnStretch(i, 1)

        self.main_layout.addWidget(self.group_empaste)

        # ---------------- Nombre del Operador / Firma del Operador / Email escaneo ----------------
        self.group_operador = QtWidgets.QGroupBox("")
        self.group_operador.setObjectName("group_operador")
        operador_layout = QtWidgets.QGridLayout(self.group_operador)
        operador_layout.setContentsMargins(8, 8, 8, 8)
        operador_layout.setHorizontalSpacing(12)
        operador_layout.setVerticalSpacing(8)

        operador_layout.addWidget(QtWidgets.QLabel("Nombre del Operador:"), 0, 0)
        self.input_nombre_operador = QtWidgets.QLineEdit()
        self.input_nombre_operador.setObjectName("input_nombre_operador")
        operador_layout.addWidget(self.input_nombre_operador, 0, 1)

        operador_layout.addWidget(QtWidgets.QLabel("Número de Fotocopiadora:"), 0, 2)
        self.input_numero_fotocopiadora = QtWidgets.QLineEdit()
        self.input_numero_fotocopiadora.setObjectName("input_numero_fotocopiadora")
        operador_layout.addWidget(self.input_numero_fotocopiadora, 0, 3)

        operador_layout.addWidget(QtWidgets.QLabel("Personas atendidas:"), 1, 0)
        self.spin_personas_atendidas = QtWidgets.QSpinBox()
        self.spin_personas_atendidas.setObjectName("spin_personas_atendidas")
        self.spin_personas_atendidas.setMaximum(999)
        operador_layout.addWidget(self.spin_personas_atendidas, 1, 1)

        # Firma del operador (pequeña area)
        operador_layout.addWidget(QtWidgets.QLabel("Firma del Operador:"), 3, 0)
        self.btn_firma_operador = QtWidgets.QPushButton("Importar Firma (PDF/IMG)")
        self.btn_firma_operador.setObjectName("btn_firma_operador")
        operador_layout.addWidget(self.btn_firma_operador, 3, 2)
        self.preview_firma_operador = QtWidgets.QLabel()
        self.preview_firma_operador.setObjectName("preview_firma_operador")
        self.preview_firma_operador.setFrameShape(QtWidgets.QFrame.Box)
        self.preview_firma_operador.setFixedSize(180, 50)
        operador_layout.addWidget(self.preview_firma_operador, 3, 3, 1, 2)

        self.main_layout.addWidget(self.group_operador)

        # ---------------- Uso exclusivo: autorizaciones (tres firmas) ----------------
        self.group_uso_exclusivo = QtWidgets.QGroupBox("USO EXCLUSIVO: EN CASO DE REQUERIRSE AUTORIZACIÓN ADICIONAL")
        self.group_uso_exclusivo.setObjectName("group_uso_exclusivo")
        uso_layout = QtWidgets.QGridLayout(self.group_uso_exclusivo)
        uso_layout.setContentsMargins(8, 8, 8, 8)
        uso_layout.setHorizontalSpacing(12)
        uso_layout.setVerticalSpacing(8)

        # Tres firmas (VB Dirección Ejecutiva, VB Servicio Litográfico, VB Dirección de Servicios Generales)
        self.btn_firma_vb_ejecutiva = QtWidgets.QPushButton("Firma VB Gerencia General")
        self.btn_firma_vb_ejecutiva.setObjectName("btn_firma_vb_ejecutiva")
        self.preview_vb_ejecutiva = QtWidgets.QLabel()
        self.preview_vb_ejecutiva.setObjectName("preview_vb_ejecutiva")
        self.preview_vb_ejecutiva.setFrameShape(QtWidgets.QFrame.Box)
        self.preview_vb_ejecutiva.setFixedSize(200, 60)

        self.btn_firma_vb_litografico = QtWidgets.QPushButton("Firma VB Jefatura Litográfico")
        self.btn_firma_vb_litografico.setObjectName("btn_firma_vb_litografico")
        self.preview_vb_litografico = QtWidgets.QLabel()
        self.preview_vb_litografico.setObjectName("preview_vb_litografico")
        self.preview_vb_litografico.setFrameShape(QtWidgets.QFrame.Box)
        self.preview_vb_litografico.setFixedSize(200, 60)

        self.btn_firma_vb_servicios = QtWidgets.QPushButton("Firma VB Gerencia Servicios Generales")
        self.btn_firma_vb_servicios.setObjectName("btn_firma_vb_servicios")
        self.preview_vb_servicios = QtWidgets.QLabel()
        self.preview_vb_servicios.setObjectName("preview_vb_servicios")
        self.preview_vb_servicios.setFrameShape(QtWidgets.QFrame.Box)
        self.preview_vb_servicios.setFixedSize(240, 60)

        uso_layout.addWidget(self.btn_firma_vb_ejecutiva, 0, 0)
        uso_layout.addWidget(self.preview_vb_ejecutiva, 1, 0)
        uso_layout.addWidget(self.btn_firma_vb_litografico, 0, 1)
        uso_layout.addWidget(self.preview_vb_litografico, 1, 1)
        uso_layout.addWidget(self.btn_firma_vb_servicios, 0, 2)
        uso_layout.addWidget(self.preview_vb_servicios, 1, 2)

        self.main_layout.addWidget(self.group_uso_exclusivo)

        # ---------------- Botones inferiores principales ----------------
        footer_widget = QtWidgets.QWidget()
        footer_layout = QtWidgets.QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.addStretch()

        self.btn_guardar = QtWidgets.QPushButton("Guardar")
        self.btn_guardar.setObjectName("btn_guardar")
        self.btn_cancelar = QtWidgets.QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("btn_cancelar")
        self.btn_enviar = QtWidgets.QPushButton("Enviar")
        self.btn_enviar.setObjectName("btn_enviar")

        footer_layout.addWidget(self.btn_guardar)
        footer_layout.addWidget(self.btn_cancelar)
        footer_layout.addWidget(self.btn_enviar)

        self.main_layout.addWidget(footer_widget)

        # Stretch final (para mantener proporciones)
        self.main_layout.addStretch()

        # ---------- Variables para almacenar rutas de firma ----------
        self._firma_small_path = None
        self._firma_operador_path = None
        self._firma_vb_ejecutiva_path = None
        self._firma_vb_litografico_path = None
        self._firma_vb_servicios_path = None

        # Guardar referencia al widget padre para mostrar mensajes
        self._parent_widget = BoletaForm

        # ---------- Conexiones ----------
        self.small_firma_btn.clicked.connect(self._on_import_small_firma)
        self.btn_firma_operador.clicked.connect(self._on_import_firma_operador)
        self.btn_firma_vb_ejecutiva.clicked.connect(self._on_import_firma_vb_ejecutiva)
        self.btn_firma_vb_litografico.clicked.connect(self._on_import_firma_vb_litografico)
        self.btn_firma_vb_servicios.clicked.connect(self._on_import_firma_vb_servicios)
        

    # ---------------------- VALIDACIONES ----------------------
    def _validar_campos_obligatorios(self) -> tuple[bool, str]:
        """Valida los campos obligatorios y retorna (es_valido, mensaje_error)"""
        errores = []
        
        if not self.input_area.text().strip():
            errores.append("• Área / Departamento")
        
        if not self.input_nombre_usuario.text().strip():
            errores.append("• Nombre completo del Usuario Autorizado")
        
        if not self.input_nombre_documento.text().strip():
            errores.append("• Nombre del Documento")
        
        if errores:
            mensaje = "Complete los siguientes campos obligatorios:\n\n" + "\n".join(errores)
            return False, mensaje
        
        return True, ""

    def _validar_servicios(self) -> tuple[bool, str]:
        """Valida que al menos un servicio esté seleccionado"""
        servicios_seleccionados = any([
            self.chk_fotocopiado.isChecked(),
            self.chk_impresion_llave.isChecked(),
            self.chk_impresion_email.isChecked(),
            self.chk_empaste_grapa.isChecked(),
            self.chk_empaste_resorte.isChecked(),
            self.chk_empaste_cuadernillo.isChecked(),
            self.chk_empaste_portada.isChecked(),
            self.chk_empaste_engomado.isChecked(),
            self.chk_empaste_guillotina.isChecked(),
            self.chk_escaneo_email.isChecked()
        ])
        
        if not servicios_seleccionados:
            return False, "Debe seleccionar al menos un servicio"
        
        return True, ""

    def _mostrar_advertencia(self, mensaje: str):
        """Muestra un popup de advertencia"""
        msg = QtWidgets.QMessageBox(self._parent_widget)
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setWindowTitle("Advertencia")
        msg.setText(mensaje)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()

    def _validar_antes_guardar(self):
        """Validación antes de guardar"""
        valido_campos, msg_campos = self._validar_campos_obligatorios()
        if not valido_campos:
            self._mostrar_advertencia(msg_campos)
            return False
        
        valido_servicios, msg_servicios = self._validar_servicios()
        if not valido_servicios:
            self._mostrar_advertencia(msg_servicios)
            return False
        
        return True

    def _validar_antes_enviar(self):
        """Validación antes de enviar"""
        return self._validar_antes_guardar()

    # ---------------------- Helpers for import/preview ----------------------
    def _import_file_and_preview(self, parent_widget, preview_label: QtWidgets.QLabel):
        """
        Open file dialog, accept images and pdfs (and others).
        If an image is selected, display preview in preview_label.
        If a PDF or other file is selected, show filename text in preview_label.
        Returns selected absolute path or None.
        """
        caption = "Seleccionar archivo de firma (PDF/IMG/OTRO)"
        filters = "PDF Files (*.pdf);;Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(parent_widget, caption, "", filters)
        if not file_path:
            return None

        # If image -> load pixmap
        lower = file_path.lower()
        if lower.endswith((".png", ".jpg", ".jpeg", ".bmp")):
            pix = QtGui.QPixmap(file_path)
            if not pix.isNull():
                # scale to preview_label keeping aspect ratio
                scaled = pix.scaled(preview_label.width(), preview_label.height(), QtCore.Qt.KeepAspectRatio,
                                     QtCore.Qt.SmoothTransformation)
                preview_label.setPixmap(scaled)
                preview_label.setToolTip(file_path)
            else:
                preview_label.setText(os.path.basename(file_path))
                preview_label.setToolTip(file_path)
        elif lower.endswith(".pdf"):
            # For PDF we don't render (no heavy deps); just show icon/text and keep path
            preview_label.setPixmap(QtGui.QPixmap())  # clear pixmap
            preview_label.setText(f"PDF: {os.path.basename(file_path)}")
            preview_label.setToolTip(file_path)
        else:
            # Other types: show filename
            preview_label.setPixmap(QtGui.QPixmap())
            preview_label.setText(os.path.basename(file_path))
            preview_label.setToolTip(file_path)

        return file_path

    # ---------- Signature button handlers ----------
    def _on_import_small_firma(self):
        path = self._import_file_and_preview(self._parent_widget, self.logo_label)
        if path:
            self._firma_small_path = path

    def _on_import_firma_operador(self):
        path = self._import_file_and_preview(self.group_operador, self.preview_firma_operador)
        if path:
            self._firma_operador_path = path

    def _on_import_firma_vb_ejecutiva(self):
        path = self._import_file_and_preview(self.group_uso_exclusivo, self.preview_vb_ejecutiva)
        if path:
            self._firma_vb_ejecutiva_path = path

    def _on_import_firma_vb_litografico(self):
        path = self._import_file_and_preview(self.group_uso_exclusivo, self.preview_vb_litografico)
        if path:
            self._firma_vb_litografico_path = path

    def _on_import_firma_vb_servicios(self):
        path = self._import_file_and_preview(self.group_uso_exclusivo, self.preview_vb_servicios)
        if path:
            self._firma_vb_servicios_path = path

    # ---------- Public helper methods for controllers ----------
    def set_section_enabled(self, section_object_name: str, enabled: bool):
        """
        Permite al controller habilitar/deshabilitar secciones por objectName.
        Ejemplo: ui.set_section_enabled('group_uso_exclusivo', False)
        """
        widget = getattr(self, section_object_name, None)
        if isinstance(widget, QtWidgets.QWidget):
            widget.setEnabled(enabled)

    def get_all_data(self) -> dict:
        """
        Retorna un diccionario con los valores actuales de los campos (útil para el controller).
        Nota: las rutas de firma se retornan tal cual; el controller será responsable de incrustarlas en PDF.
        """
        data = {
            "fecha": self.input_fecha.text(),
            "area": self.input_area.text(),
            "nombre_usuario": self.input_nombre_usuario.text(),
            "nombre_documento": self.input_nombre_documento.text(),
            "servicios": {
                "fotocopiado": self.chk_fotocopiado.isChecked(),
                "impresion_llave": self.chk_impresion_llave.isChecked(),
                "impresion_email": self.chk_impresion_email.isChecked(),
                "empaste_grapa": self.chk_empaste_grapa.isChecked(),
                "empaste_resorte": self.chk_empaste_resorte.isChecked(),
                "empaste_cuadernillo": self.chk_empaste_cuadernillo.isChecked(),
                "empaste_portada": self.chk_empaste_portada.isChecked(),
                "empaste_engomado": self.chk_empaste_engomado.isChecked(),
                "empaste_guillotina": self.chk_empaste_guillotina.isChecked(),
                "escaneo_email": self.chk_escaneo_email.isChecked()
            },
            "copias": {
                "color": self.spin_copias_color.value(),
                "bn": self.spin_copias_bn.value(),
                "total": self.spin_total_copias.value(),
                "documentos": self.spin_cantidad_documentos.value()
            },
            "empaste": {
                "grapa": self.spin_empaste_grapa.value(),
                "resorte": self.spin_empaste_resorte.value(),
                "cuadernillo": self.spin_empaste_cuadernillo.value(),
                "portada_cartulina": self.spin_empaste_portada_cartulina.value(),
                "engomado": self.spin_empaste_engomado.value(),
                "guillotina": self.spin_empaste_guillotina.value(),
                "paginas_escaneo": self.spin_empaste_paginas_escaneo.value(),
                "copias_prueba": self.spin_copias_prueba.value()
            },
            "observaciones_servicio": self.text_observaciones_servicio.toPlainText(),
            "operador": {
                "nombre": self.input_nombre_operador.text(),
                "numero_fotocopiadora": self.input_numero_fotocopiadora.text(),
                "personas_atendidas": self.spin_personas_atendidas.value(),
                "email_escaneo": self.txt_email_escaneo.text()
            },
            "firmas": {
                "small": self._firma_small_path,
                "operador": self._firma_operador_path,
                "vb_ejecutiva": self._firma_vb_ejecutiva_path,
                "vb_litografico": self._firma_vb_litografico_path,
                "vb_servicios": self._firma_vb_servicios_path
            }
        }
        return data


# ========== Event Filter para validar antes de permitir interacción ==========
class BoletaValidationFilter(QtCore.QObject):
    def __init__(self, ui_instance, parent_widget):
        super().__init__(parent_widget)  # ✅ Un solo argumento
        self.ui = ui_instance
        self.parent_widget = parent_widget
        self._ya_mostrado = False
    
    def eventFilter(self, obj, event):
        # ✅ NO bloquear botones
        if isinstance(obj, QtWidgets.QPushButton):
            return super().eventFilter(obj, event)
        
        if event.type() in (QtCore.QEvent.MouseButtonPress, QtCore.QEvent.FocusIn):
            valido, mensaje = self.ui._validar_campos_obligatorios()
            if not valido and not self._ya_mostrado:
                self._ya_mostrado = True
                self.ui._mostrar_advertencia(mensaje)
                QtCore.QTimer.singleShot(500, lambda: setattr(self, '_ya_mostrado', False))
                
                if isinstance(obj, QtWidgets.QCheckBox) and obj.isChecked():
                    QtCore.QTimer.singleShot(100, lambda: obj.setChecked(False))
                    return True
        
        return super().eventFilter(obj, event)
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    # Ventana principal sin marco y tamaño fijo inicial
    window = QtWidgets.QMainWindow()
    window.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    window.setWindowTitle("Boleta de Solicitud del Servicio")

    # Scroll principal
    scroll_area = QtWidgets.QScrollArea()
    scroll_area.setWidgetResizable(True)
    # 🔧 Desactivar scroll horizontal, solo vertical
    scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    # Contenedor interno
    content_widget = QtWidgets.QWidget()
    ui = Ui_BoletaForm()
    ui.setupUi(content_widget)

    # 🔧 Forzar adaptación del contenido al ancho de la ventana
    content_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
    content_widget.setMinimumWidth(790)  # un poquito menos que la ventana fija

    # Aplicar layout adaptativo
    for layout_name in [
        "main_layout", "group_seleccionar_servicio", "group_empaste",
        "group_datos_solicitante", "group_operador", "group_uso_exclusivo"
    ]:
        widget = getattr(ui, layout_name, None)
        if widget and isinstance(widget, QtWidgets.QWidget):
            widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

    scroll_area.setWidget(content_widget)
    window.setCentralWidget(scroll_area)

    # Tamaño fijo y centrado
    window.resize(800, 600)
    window.setFixedSize(800, 600)
    screen = app.primaryScreen().availableGeometry()
    window.move(
        (screen.width() - window.width()) // 2,
        (screen.height() - window.height()) // 2
    )

    window.show()
    sys.exit(app.exec())