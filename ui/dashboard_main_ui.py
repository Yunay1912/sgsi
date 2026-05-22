import traceback  
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QStackedWidget, QTableWidget, QTableWidgetItem, QComboBox,
    QHeaderView, QAbstractItemView, QSpacerItem, QSizePolicy, QApplication,
    QLineEdit, QScrollArea, QMessageBox, QFileDialog, QCalendarWidget,
    QListWidget, QListWidgetItem, QGridLayout, QTextEdit, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, QSize, QDate, QPropertyAnimation, QEasingCurve, Slot
from PySide6.QtGui import QFont, QPixmap, QCursor, QTextCharFormat, QColor
import sys
import os
import importlib
import json
# Helper: AccordionItem (kept for compatibility)

class AccordionItem(QFrame):
    def __init__(self, title: str, content_widget: QWidget, parent=None, initial_expanded: bool = False):
        super().__init__(parent)
        self.setObjectName("accordion_item")
        self.title = title
        self.content_widget = content_widget
        self.expanded = False
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 6)
        self.header = QFrame(self)
        self.header.setCursor(QCursor(Qt.PointingHandCursor))
        self.header_layout = QHBoxLayout(self.header)
        self.arrow = QLabel("▼")
        self.arrow.setFixedWidth(18)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("accordion_title")
        self.count_label = QLabel("")
        self.count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.header_layout.addWidget(self.arrow)
        self.header_layout.addWidget(self.title_label)
        self.header_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.header_layout.addWidget(self.count_label)
        self.main_layout.addWidget(self.header)
        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_area.setFrameShape(QFrame.NoFrame)
        self.content_area.setWidget(content_widget)
        self.content_area.setMaximumHeight(0)
        self.main_layout.addWidget(self.content_area)
        self.animation = QPropertyAnimation(self.content_area, b"maximumHeight")
        self.animation.setDuration(220)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.header.mouseReleaseEvent = self.toggle
        if initial_expanded:
            self.toggle()

    @Slot()
    def toggle(self, event=None):
        content_height = self.content_widget.sizeHint().height()
        if content_height < 80:
            content_height = 240
        if self.expanded:
            self.animation.setStartValue(self.content_area.maximumHeight())
            self.animation.setEndValue(0)
            self.animation.start()
            self.arrow.setText("▼")
            self.expanded = False
        else:
            self.animation.setStartValue(self.content_area.maximumHeight())
            self.animation.setEndValue(content_height)
            self.animation.start()
            self.arrow.setText("▲")
            self.expanded = True

    def set_count_text(self, text: str):
        self.count_label.setText(text)


# Dialog para justificación de cambios/rechazo
class JustificacionDialog(QDialog):
    def __init__(self, parent=None, titulo="Justificación", mensaje="Ingrese la justificación:"):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setMinimumSize(400, 200)
        layout = QVBoxLayout(self)
        
        lbl = QLabel(mensaje)
        lbl.setWordWrap(True)
        layout.addWidget(lbl)
        
        self.text_justificacion = QTextEdit()
        self.text_justificacion.setPlaceholderText("Escriba aquí la justificación...")
        layout.addWidget(self.text_justificacion)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_justificacion(self):
        return self.text_justificacion.toPlainText()

# UI principal
class Ui_DashboardMain:
    def setupUi(self, DashboardMain: QMainWindow):
        DashboardMain.setObjectName("DashboardMain")
        DashboardMain.setWindowTitle("Asamblea Legislativa - Panel")
        DashboardMain.resize(1400, 880)
        DashboardMain.setMinimumSize(QSize(1200, 750))
        DashboardMain.setFont(QFont("Segoe UI", 10))

        # theme state
        self._theme = "Claro"  # "Claro" / "Oscuro"

        # calendar archive in-memory (date_str -> list of dicts)
        # controller should persist this to DB when ready
        self._calendar_archive = {}  # e.g. {"2025-10-28": [{"boleta": "...", "ext": "...", "pag": 3}, ...]}

        # boletas data per day (in-memory grouping)
        self._boletas_data = {d: [] for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]}

        # CENTRAL
        self.central_widget = QWidget(DashboardMain)
        DashboardMain.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # SIDEBAR
        self.sidebar = QFrame(self.central_widget)
        self.sidebar.setObjectName("sidebar_frame")
        self.sidebar.setMinimumWidth(260)
        self.sidebar.setMaximumWidth(340)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(18, 18, 18, 18)
        self.sidebar_layout.setSpacing(12)

        # Logo
        self.logo_label = QLabel(self.sidebar)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        path_logo = "assets/logo_asamblea.png"
        if os.path.exists(path_logo):
            self.logo_label.setPixmap(QPixmap(path_logo))
        else:
            self.logo_label.setText("Asamblea")
        self.logo_label.setScaledContents(True)
        self.logo_label.setMaximumHeight(140)
        self.logo_label.setMaximumWidth(220)
        self.logo_label.setStyleSheet("QLabel { background-color: transparent; padding: 10px; border: none; }")
        self.sidebar_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # decorative separator
        self.line_separator = QFrame(self.sidebar)
        self.line_separator.setFrameShape(QFrame.Shape.HLine)
        self.line_separator.setStyleSheet("QFrame { background-color: rgba(198,12,48,0.28); max-height:1px; margin:8px 8px; border:none; }")
        self.sidebar_layout.addWidget(self.line_separator)
        self.sidebar_layout.addSpacing(8)

        # BOTONES DE NAVEGACIÓN PRINCIPAL
        self.btn_gestion = QPushButton("Gestión de Solicitudes"); self.btn_gestion.setObjectName("btn_gestion"); self.btn_gestion.setMinimumHeight(44)
        self.btn_boletas = QPushButton("Boletas"); self.btn_boletas.setObjectName("btn_boletas"); self.btn_boletas.setMinimumHeight(44)
        self.btn_cierre = QPushButton("Cierre"); self.btn_cierre.setObjectName("btn_cierre"); self.btn_cierre.setMinimumHeight(44)
        self.btn_auditoria = QPushButton("Auditoría"); self.btn_auditoria.setObjectName("btn_auditoria"); self.btn_auditoria.setMinimumHeight(44)
        self.btn_reportes = QPushButton("Reportes"); self.btn_reportes.setObjectName("btn_reportes"); self.btn_reportes.setMinimumHeight(44)
        self.btn_config = QPushButton("Configuración"); self.btn_config.setObjectName("btn_config"); self.btn_config.setMinimumHeight(44)
        self.btn_calendario = QPushButton("Calendario Anual"); self.btn_calendario.setObjectName("btn_calendario"); self.btn_calendario.setMinimumHeight(44)

        # ---- PRIMERA OPCIÓN INACTIVA  ----
        self.btn_contador = QPushButton("Contador -En espera")
        self.btn_contador.setMinimumHeight(44)
        self.btn_contador.setObjectName("btn_snippet")
        self.btn_contador.setEnabled(False)
        # ---- SEGUNDA OPCIÓN INACTIVA (DESHABILITADA) ----
        self.btn_op_futura2 = QPushButton("-Inactivo")
        self.btn_op_futura2.setMinimumHeight(44)
        self.btn_op_futura2.setEnabled(False)

        # ---- TERCERA OPCIÓN INACTIVA  ----
        self.btn_reportes.setEnabled(False) 

        # ---- Añadir botones al layout lateral ----
        for b in [
            self.btn_gestion,
            self.btn_boletas,
            self.btn_cierre,
            self.btn_calendario,
            self.btn_auditoria,
            self.btn_config,
            self.btn_reportes,
            self.btn_contador,
            self.btn_op_futura2
        ]:
            self.sidebar_layout.addWidget(b)

        # ---- Separador y versión ----
        self.sidebar_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.lbl_sidebar_version = QLabel("Versión 1.0.0")
        self.lbl_sidebar_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sidebar_layout.addWidget(self.lbl_sidebar_version)
        self.main_layout.addWidget(self.sidebar)

        # CONEXIONES DE BOTONES DE NAVEGACIÓN
        self.btn_gestion.clicked.connect(lambda: self.stacked_main.setCurrentWidget(self.page_gestion))
        self.btn_boletas.clicked.connect(lambda: self.stacked_main.setCurrentWidget(self.page_boletas))
        self.btn_cierre.clicked.connect(lambda: self.stacked_main.setCurrentWidget(self.page_cierre))
        self.btn_auditoria.clicked.connect(lambda: self.stacked_main.setCurrentWidget(self.page_auditoria))
        self.btn_reportes.clicked.connect(lambda: self.stacked_main.setCurrentWidget(self.page_reportes))
        self.btn_config.clicked.connect(lambda: self.stacked_main.setCurrentWidget(self.page_config))
        self.btn_calendario.clicked.connect(lambda: self.stacked_main.setCurrentWidget(self.page_calendar))

        # El botón de snippet abre una interfaz secundaria o archivo aparte
        self.btn_contador.clicked.connect(self.mostrar_snippet)

        # ÁREA PRINCIPAL
        self.area = QFrame(self.central_widget)
        self.area_layout = QVBoxLayout(self.area)
        self.area_layout.setContentsMargins(12, 12, 12, 12)
        self.area_layout.setSpacing(8)

        # TOPBAR
        self.topbar = QFrame(self.area); self.topbar.setMinimumHeight(64)
        self.topbar_layout = QHBoxLayout(self.topbar); self.topbar_layout.setContentsMargins(8,8,8,8)
        self.lbl_bienvenida = QLabel("Bienvenido, [NombreUsuario]"); self.lbl_bienvenida.setObjectName("lbl_bienvenida")
        self.topbar_layout.addWidget(self.lbl_bienvenida)
        self.topbar_layout.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum))
        self.btn_notificaciones = QPushButton("🔔"); self.btn_notificaciones.setFixedSize(36,36); self.topbar_layout.addWidget(self.btn_notificaciones)
        self.lbl_notifCount = QLabel(""); self.lbl_notifCount.setMinimumSize(18,18); self.lbl_notifCount.setAlignment(Qt.AlignmentFlag.AlignCenter); self.lbl_notifCount.setStyleSheet("background:#E74C3C; color:white; border-radius:9px; padding:0px 4px;"); self.lbl_notifCount.setVisible(False); self.topbar_layout.addWidget(self.lbl_notifCount)
        self.btn_tema = QPushButton("🌙 Oscuro"); self.btn_tema.setObjectName("btn_tema"); self.btn_tema.setFixedSize(65,36); self.btn_tema.setToolTip("Alternar tema (Claro / Oscuro)"); self.topbar_layout.addWidget(self.btn_tema)
        self.area_layout.addWidget(self.topbar)

        # STACKED PAGES
        self.stacked_main = QStackedWidget(self.area); self.stacked_main.setObjectName("stacked_main")

        # PAGE: GESTIÓN
        self.page_gestion = QWidget(); self.page_gestion_layout = QVBoxLayout(self.page_gestion); self.page_gestion_layout.setContentsMargins(6,6,6,6); self.page_gestion_layout.setSpacing(8)
        btns_top = QHBoxLayout()
        self.btn_nuevaSolicitud = QPushButton("Nueva Solicitud"); self.btn_nuevaSolicitud.setObjectName("btn_nuevaSolicitud"); self.btn_nuevaSolicitud.setMinimumHeight(36)
        self.btn_editarSolicitud = QPushButton("Editar"); self.btn_editarSolicitud.setObjectName("btn_editarSolicitud"); self.btn_editarSolicitud.setMinimumHeight(36)
        self.btn_actualizar = QPushButton("Actualizar Tabla"); self.btn_actualizar.setObjectName("btn_actualizar"); self.btn_actualizar.setMinimumHeight(36)
        btns_top.addWidget(self.btn_nuevaSolicitud); btns_top.addWidget(self.btn_editarSolicitud); btns_top.addWidget(self.btn_actualizar); btns_top.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum))
        self.page_gestion_layout.addLayout(btns_top)

        # table: Número Boleta, Extensión, Nombre, Páginas, Estado/Enviar, Acciones
        self.table_solicitudes = QTableWidget(); self.table_solicitudes.setObjectName("table_solicitudes")
        self.table_solicitudes.setColumnCount(6)
        self.table_solicitudes.setHorizontalHeaderLabels(["Número Boleta", "Extensión", "Nombre", "Páginas", "Estado", "Acciones"])
        self.table_solicitudes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_solicitudes.verticalHeader().setVisible(False)
        self.table_solicitudes.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        header = self.table_solicitudes.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table_solicitudes.setColumnWidth(5, 150)
        self.page_gestion_layout.addWidget(self.table_solicitudes)
        stats_layout = QHBoxLayout()
        self.lbl_totalUsuarios = QLabel("Usuarios atendidos hoy: 0"); self.lbl_totalBoletas = QLabel("Total de boletas: 0")
        stats_layout.addWidget(self.lbl_totalUsuarios); stats_layout.addWidget(self.lbl_totalBoletas); stats_layout.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum))
        self.page_gestion_layout.addLayout(stats_layout)
        self.stacked_main.addWidget(self.page_gestion)

        # PAGE: BOLETAS (Desplegable día + contenedor)
        self.page_boletas = QWidget(); l_boletas = QVBoxLayout(self.page_boletas); l_boletas.setContentsMargins(6,6,6,6); l_boletas.setSpacing(8)
        top_boletas_controls = QHBoxLayout()
        lbl_boletas_title = QLabel("Boletas recibidas (cierres)"); lbl_boletas_title.setStyleSheet("font-weight:700;")
        top_boletas_controls.addWidget(lbl_boletas_title)
        top_boletas_controls.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum))
        dias = ["Lunes","Martes","Miércoles","Jueves","Viernes"]
        self.combo_boletas_dia = QComboBox(); self.combo_boletas_dia.addItems(dias); self.combo_boletas_dia.setFixedWidth(160)
        # default to today or friday
        di = QDate.currentDate().dayOfWeek() - 1
        if 0 <= di <= 4:
            self.combo_boletas_dia.setCurrentIndex(di)
        else:
            self.combo_boletas_dia.setCurrentIndex(4)
        top_boletas_controls.addWidget(QLabel("Día:")); top_boletas_controls.addWidget(self.combo_boletas_dia)
        l_boletas.addLayout(top_boletas_controls)

        # container for cards (scroll)
        self.boletas_day_container = QWidget(); self.boletas_day_layout = QVBoxLayout(self.boletas_day_container); self.boletas_day_layout.setContentsMargins(6,6,6,6); self.boletas_day_layout.setSpacing(8)
        self.boletas_day_layout.addItem(QSpacerItem(10,10,QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding))
        self.boletas_scroll = QScrollArea(); self.boletas_scroll.setWidgetResizable(True); self.boletas_scroll.setWidget(self.boletas_day_container); l_boletas.addWidget(self.boletas_scroll)

        # export button (visible only for encargado/admin)
        bot_export_layout = QHBoxLayout()
        self.btn_exportar_boletas = QPushButton("Exportar a Excel (Seleccionar días)"); self.btn_exportar_boletas.setObjectName("btn_exportar_boletas"); self.btn_exportar_boletas.setFixedWidth(220); self.btn_exportar_boletas.setFixedHeight(36)
        bot_export_layout.addWidget(self.btn_exportar_boletas); bot_export_layout.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum))
        l_boletas.addLayout(bot_export_layout)
        self.stacked_main.addWidget(self.page_boletas)

        # PAGE: CIERRE (operador)
        self.page_cierre = QWidget(); l_cierre = QVBoxLayout(self.page_cierre); l_cierre.setContentsMargins(6,6,6,6); l_cierre.setSpacing(8)
        
        # Controles superiores
        controls_cierre = QHBoxLayout()
        self.btn_enviar_cierre_actual = QPushButton("Enviar cierre actual"); self.btn_enviar_cierre_actual.setFixedSize(200,36)
        self.btn_listo_dia = QPushButton("Listo día"); self.btn_listo_dia.setFixedSize(120,36); self.btn_listo_dia.setObjectName("btn_listo_dia")
        self.btn_enviar_cierre_semanal = QPushButton("Enviar cierre semanal (solo viernes)"); self.btn_enviar_cierre_semanal.setFixedSize(260,36); self.btn_enviar_cierre_semanal.setEnabled(False)
        controls_cierre.addWidget(self.btn_enviar_cierre_actual); controls_cierre.addWidget(self.btn_listo_dia); controls_cierre.addWidget(self.btn_enviar_cierre_semanal); controls_cierre.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum))
        self.combo_cierre_dia = QComboBox(); self.combo_cierre_dia.addItems(dias); self.combo_cierre_dia.setFixedWidth(160)
        di = QDate.currentDate().dayOfWeek() - 1
        if 0 <= di <= 4:
            self.combo_cierre_dia.setCurrentIndex(di)
        else:
            self.combo_cierre_dia.setCurrentIndex(4)
        controls_cierre.addWidget(QLabel("Ver día:")); controls_cierre.addWidget(self.combo_cierre_dia)
        l_cierre.addLayout(controls_cierre)
        
        instruct = QLabel("Marca boletas como 'Listo' para que se archiven en el Calendario Anual. Enviar cierre actual/semana manda a Boletas (controlador valida).")
        instruct.setWordWrap(True)
        l_cierre.addWidget(instruct)
        
        # NUEVO: Panel de boleta de cierre (manejado por cierre_controller)
        cierre_panel_layout = QHBoxLayout()
        
        # Área izquierda: boletas del día (puede reutilizar lógica similar a boletas)
        left_cierre = QVBoxLayout()
        lbl_boletas_cierre = QLabel("Boletas del día actual:")
        lbl_boletas_cierre.setStyleSheet("font-weight:700; font-size:12px;")
        left_cierre.addWidget(lbl_boletas_cierre)
        
        self.cierre_day_container = QWidget()
        self.cierre_day_layout = QVBoxLayout(self.cierre_day_container)
        self.cierre_day_layout.setContentsMargins(6,6,6,6)
        self.cierre_day_layout.setSpacing(8)
        self.cierre_day_layout.addItem(QSpacerItem(10,10,QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding))
        self.cierre_scroll = QScrollArea()
        self.cierre_scroll.setWidgetResizable(True)
        self.cierre_scroll.setWidget(self.cierre_day_container)
        left_cierre.addWidget(self.cierre_scroll)
        
        # Área derecha: texto de boleta de cierre
        right_cierre = QVBoxLayout()
        lbl_texto_cierre = QLabel("Boleta de cierre (gestionado por controlador):")
        lbl_texto_cierre.setStyleSheet("font-weight:700; font-size:12px;")
        right_cierre.addWidget(lbl_texto_cierre)
        
        # Frame destacado para la boleta de cierre
        self.frame_boleta_cierre = QFrame()
        self.frame_boleta_cierre.setObjectName("frame_boleta_cierre")
        self.frame_boleta_cierre.setStyleSheet("QFrame#frame_boleta_cierre { background: rgba(255,230,180,0.3); border: 2px solid rgba(198,12,48,0.5); border-radius: 8px; padding: 10px; }")
        layout_boleta_cierre = QVBoxLayout(self.frame_boleta_cierre)
        
        self.text_boleta_cierre = QTextEdit()
        self.text_boleta_cierre.setPlaceholderText("El controlador de cierre mostrará aquí el contenido de la boleta de cierre del día...")
        self.text_boleta_cierre.setReadOnly(True)
        self.text_boleta_cierre.setMinimumHeight(200)
        layout_boleta_cierre.addWidget(self.text_boleta_cierre)
        
        right_cierre.addWidget(self.frame_boleta_cierre)
        
        # Agregar áreas al layout de cierre
        cierre_panel_layout.addLayout(left_cierre, 2)
        cierre_panel_layout.addLayout(right_cierre, 1)
        l_cierre.addLayout(cierre_panel_layout)
        
        self.stacked_main.addWidget(self.page_cierre)

        # PAGE: AUDITORÍA
        self.page_auditoria = QWidget(); l_aud = QVBoxLayout(self.page_auditoria); l_aud.setContentsMargins(6,6,6,6); l_aud.setSpacing(8)
        search_layout = QHBoxLayout()
        self.input_aud_buscar = QLineEdit(); self.input_aud_buscar.setPlaceholderText("Buscar por extensión..."); self.input_aud_buscar.setFixedWidth(220)
        self.btn_aud_buscar = QPushButton("Buscar"); self.btn_aud_limpiar = QPushButton("Limpiar")
        search_layout.addWidget(QLabel("Buscar:")); search_layout.addWidget(self.input_aud_buscar); search_layout.addWidget(self.btn_aud_buscar); search_layout.addWidget(self.btn_aud_limpiar); search_layout.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum))
        l_aud.addLayout(search_layout)
        self.table_auditoria = QTableWidget(); self.table_auditoria.setColumnCount(4); self.table_auditoria.setHorizontalHeaderLabels(["Fecha","Extensión","Acción","Detalle"]); self.table_auditoria.setEditTriggers(QAbstractItemView.NoEditTriggers); self.table_auditoria.verticalHeader().setVisible(False); self.table_auditoria.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        header_aud = self.table_auditoria.horizontalHeader(); header_aud.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch); l_aud.addWidget(self.table_auditoria)
        self.btn_exportarAuditoria = QPushButton("Exportar a Excel"); self.btn_exportarAuditoria.setFixedSize(160,36); l_aud.addWidget(self.btn_exportarAuditoria, alignment=Qt.AlignmentFlag.AlignLeft)
        self.stacked_main.addWidget(self.page_auditoria)

        # PAGE: REPORTES (placeholder; snippet can replace)
        self.page_reportes = QWidget(); l_rep = QVBoxLayout(self.page_reportes); l_rep.addWidget(QLabel("Reportes (en desarrollo)")); self.stacked_main.addWidget(self.page_reportes)

        # PAGE: CONFIGURACIÓN
        self.page_config = QWidget(); l_cfg = QVBoxLayout(self.page_config); l_cfg.setContentsMargins(6,6,6,6); l_cfg.setSpacing(8); l_cfg.addWidget(QLabel("Configuración de usuario"))
        cfg_frame = QFrame(); cfg_frame.setObjectName("cfg_frame"); cfg_layout = QGridLayout(cfg_frame); cfg_layout.setContentsMargins(12,12,12,12); cfg_layout.setHorizontalSpacing(16); cfg_layout.setVerticalSpacing(10)
        lbl_usuario_title = QLabel("Usuario:"); self.lbl_usuario = QLabel("-")
        lbl_extension_title = QLabel("Extensión:"); self.lbl_extension = QLabel("-")
        lbl_role_title = QLabel("Rol:"); self.lbl_rol = QLabel("-")
        cfg_layout.addWidget(lbl_usuario_title,0,0); cfg_layout.addWidget(self.lbl_usuario,0,1)
        cfg_layout.addWidget(lbl_extension_title,1,0); cfg_layout.addWidget(self.lbl_extension,1,1)
        cfg_layout.addWidget(lbl_role_title,2,0); cfg_layout.addWidget(self.lbl_rol,2,1)
        lbl_idioma = QLabel("Idioma:"); self.combo_idioma = QComboBox(); self.combo_idioma.addItems(["Español","Inglés"]); cfg_layout.addWidget(lbl_idioma,3,0); cfg_layout.addWidget(self.combo_idioma,3,1)
        lbl_notifs = QLabel("Notificaciones:"); self.combo_notifs = QComboBox(); self.combo_notifs.addItems(["Activadas","Desactivadas"]); cfg_layout.addWidget(lbl_notifs,4,0); cfg_layout.addWidget(self.combo_notifs,4,1)
        self.btn_cerrarSesion = QPushButton("Cerrar Sesión"); self.btn_cerrarSesion.setFixedWidth(140); cfg_layout.addWidget(self.btn_cerrarSesion,5,1)
        l_cfg.addWidget(cfg_frame); l_cfg.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)); self.stacked_main.addWidget(self.page_config)

        # PAGE: CALENDARIO ANUAL (with list of archived boletas for selected date)
        self.page_calendar = QWidget(); l_cal = QHBoxLayout(self.page_calendar)
        left = QVBoxLayout(); left.addWidget(QLabel("Calendario Anual"))
        self.calendar_widget = QCalendarWidget(); self.calendar_widget.setGridVisible(True)
        left.addWidget(self.calendar_widget)
        
        right = QVBoxLayout()
        lbl_archivadas = QLabel("Boletas archivadas (fecha seleccionada)")
        lbl_archivadas.setStyleSheet("font-weight:700;")
        right.addWidget(lbl_archivadas)
        
        self.list_calendar_entries = QListWidget()
        right.addWidget(self.list_calendar_entries)
        
        # NUEVO: Botón para abrir boleta archivada en modo lectura
        self.btn_abrir_boleta_archivo = QPushButton("Abrir boleta seleccionada (Lectura)")
        self.btn_abrir_boleta_archivo.setFixedHeight(36)
        self.btn_abrir_boleta_archivo.setObjectName("btn_abrir_boleta_archivo")
        right.addWidget(self.btn_abrir_boleta_archivo)
        
        l_cal.addLayout(left); l_cal.addLayout(right)
        self.stacked_main.addWidget(self.page_calendar)

        # placeholder pages (kept)
        self.page_contador = QWidget(); self.page_contador.setVisible(False); self.stacked_main.addWidget(self.page_contador)
        self.page_op_futura2 = QWidget(); self.page_op_futura2.setVisible(False); self.stacked_main.addWidget(self.page_op_futura2)

        self.area_layout.addWidget(self.stacked_main)

        # FOOTER
        self.footer = QFrame(self.area); self.footer.setMinimumHeight(40); self.footer_layout = QHBoxLayout(self.footer); self.footer_layout.setContentsMargins(6,6,6,6)
        self.lbl_fecha = QLabel(f"Fecha: {QDate.currentDate().toString('dd/MM/yyyy')}"); self.lbl_estadoConexion = QLabel("Conectado"); self.lbl_version = QLabel("Versión 1.0.0")
        self.footer_layout.addWidget(self.lbl_fecha); self.footer_layout.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)); self.footer_layout.addWidget(self.lbl_estadoConexion); self.footer_layout.addWidget(self.lbl_version)
        self.area_layout.addWidget(self.footer)
        self.main_layout.addWidget(self.area)

        # Stylesheets (claro / oscuro) - QComboBox popups included + Calendar styles
        self._styles_claro = """
        QMainWindow { background-color: #E8EDF2; color: #374151; }
        QWidget { color: #374151; font-family: 'Segoe UI', 'Roboto', sans-serif; }
        QFrame#sidebar_frame { background-color: #D8E1E8; }
        QLabel { color: #374151; }
        QPushButton {
            background-color: #C8D5DF;
            color: #1F2933;
            border: none;
            border-radius: 8px;
            padding: 8px;
            text-align: left;
        }
        QPushButton:hover { background-color: #A8B8C4; }
        QPushButton:disabled { background-color: #D9E2E9; color: #8A939D; }
        QPushButton#btn_tema { background-color: #BDD0DD; min-width: 120px; text-align: center; }
        QPushButton#btn_listo_dia { background-color: #7FCD7F; color: #0d3d0d; font-weight: 700; }
        QPushButton#btn_listo_dia:hover { background-color: #6BB86B; }
        QHeaderView::section { background-color: #B5C5D1; color: #2C3E50; padding:6px; border: none; }
        QTableWidget { background-color: #F5F8FA; color: #374151; gridline-color: #C1CDD7; border: none; }
        QTableWidget::item:selected { background: #B0C6D6; color: #0b1a1f; }
        QLineEdit { background: #F8FAFB; color: #222; border: 1px solid #C1CDD7; border-radius:6px; padding:6px; }
        QComboBox { background: #F8FAFB; color: #222; border: 1px solid #C1CDD7; border-radius:6px; padding:4px; }
        QComboBox QAbstractItemView {
            background-color: #F8FAFB;
            color: #222;
            selection-background-color: #B7CBD9;
            selection-color: #000000;
            border: 1px solid #9AAAB8;
        }
        QTextEdit { background: #F8FAFB; color: #222; border: 1px solid #C1CDD7; border-radius:6px; padding:6px; }
        QScrollArea { background: transparent; border: none; }
        QFrame#cfg_frame { background: rgba(216, 225, 232, 0.85); border-radius: 8px; }
        QFrame#card_boleta { background: rgba(245,248,250,0.95); border-radius: 8px; padding: 10px; border: 1px solid rgba(0,0,0,0.08); }
        QCalendarWidget QWidget { background-color: #F8FAFB; color: #374151; }
        QCalendarWidget QAbstractItemView { background-color: #F8FAFB; color: #374151; selection-background-color: #B0C6D6; selection-color: #0b1a1f; }
        QCalendarWidget QToolButton { background-color: #C8D5DF; color: #1F2933; border-radius: 4px; }
        QCalendarWidget QToolButton:hover { background-color: #A8B8C4; }
        QCalendarWidget QMenu { background-color: #F8FAFB; color: #374151; }
        QCalendarWidget QSpinBox { background-color: #F8FAFB; color: #374151; border: 1px solid #C1CDD7; }
        QListWidget { background-color: #F8FAFB; color: #374151; border: 1px solid #C1CDD7; border-radius: 6px; }
        QListWidget::item:selected { background: #B0C6D6; color: #0b1a1f; }
        """

        self._styles_oscuro = """
        QMainWindow { background-color: #232528; color: #E6E6E6; }
        QWidget { color: #E6E6E6; font-family: 'Segoe UI', 'Roboto', sans-serif; }
        QFrame#sidebar_frame { background-color: #1F2933; }
        QLabel { color: #E6E6E6; }
        QPushButton {
            background-color: #3A3F44;
            color: #E6E6E6;
            border: none;
            border-radius: 8px;
            padding: 8px;
            text-align: left;
        }
        QPushButton:hover { background-color: #505559; }
        QPushButton:disabled { background-color: #2E2E2E; color:#9AA0A6; }
        QPushButton#btn_tema { background-color: #44494D; min-width: 120px; text-align: center; }
        QPushButton#btn_listo_dia { background-color: #2d5f2d; color: #90EE90; font-weight: 700; }
        QPushButton#btn_listo_dia:hover { background-color: #3d6f3d; }
        QHeaderView::section { background-color: #2B3540; color: #E6E6E6; padding:6px; border: none; }
        QTableWidget { background-color: #1C1F22; color: #E6E6E6; gridline-color: #333638; border: none; }
        QTableWidget::item:selected { background: #3A505A; color: #E6E6E6; }
        QLineEdit { background: #2B2F33; color: #E6E6E6; border: 1px solid #3A3F44; border-radius:6px; padding:6px; }
        QComboBox { background: #2B2F33; color: #E6E6E6; border: 1px solid #3A3F44; border-radius:6px; padding:4px; }
        QComboBox QAbstractItemView {
            background-color: #2B2F33;
            color: #E6E6E6;
            selection-background-color: #3A505A;
            selection-color: #E6E6E6;
            border: 1px solid #3A3F44;
        }
        QTextEdit { background: #2B2F33; color: #E6E6E6; border: 1px solid #3A3F44; border-radius:6px; padding:6px; }
        QFrame#cfg_frame { background: rgba(40, 44, 49, 0.85); border-radius: 8px; }
        QFrame#card_boleta { background: rgba(60,60,60,0.75); border-radius: 8px; padding: 10px; border: 1px solid rgba(255,255,255,0.03); }
        QCalendarWidget QWidget { background-color: #2B2F33; color: #E6E6E6; }
        QCalendarWidget QAbstractItemView { background-color: #2B2F33; color: #E6E6E6; selection-background-color: #3A505A; selection-color: #E6E6E6; }
        QCalendarWidget QToolButton { background-color: #3A3F44; color: #E6E6E6; border-radius: 4px; }
        QCalendarWidget QToolButton:hover { background-color: #505559; }
        QCalendarWidget QMenu { background-color: #2B2F33; color: #E6E6E6; }
        QCalendarWidget QSpinBox { background-color: #2B2F33; color: #E6E6E6; border: 1px solid #3A3F44; }
        QListWidget { background-color: #2B2F33; color: #E6E6E6; border: 1px solid #3A3F44; border-radius: 6px; }
        QListWidget::item:selected { background: #3A505A; color: #E6E6E6; }
        """

        # apply initial theme
        QMainWindow.setStyleSheet(DashboardMain, self._styles_oscuro)

        # UI SIGNALS / BEHAVIOR
        self.btn_gestion.clicked.connect(lambda: self.stacked_main.setCurrentWidget(self.page_gestion))
        self.btn_boletas.clicked.connect(lambda: self.stacked_main.setCurrentWidget(self.page_boletas))
        self.btn_cierre.clicked.connect(lambda: self.stacked_main.setCurrentWidget(self.page_cierre))
        self.btn_auditoria.clicked.connect(lambda: self.stacked_main.setCurrentWidget(self.page_auditoria))
        self.btn_reportes.clicked.connect(lambda: self.stacked_main.setCurrentWidget(self.page_reportes))
        self.btn_config.clicked.connect(lambda: self.stacked_main.setCurrentWidget(self.page_config))

        # SNIPPET launcher (first inactive option)
        self.btn_contador.clicked.connect(self.mostrar_snippet)

        self.btn_tema.clicked.connect(lambda: self.toggle_theme(DashboardMain))
        self.combo_boletas_dia.currentIndexChanged.connect(self._on_boletas_dia_changed)
        self.combo_cierre_dia.currentIndexChanged.connect(self._on_combo_cierre_changed)
        self.btn_enviar_cierre_actual.clicked.connect(self._ui_send_cierre_actual)
        self.btn_listo_dia.clicked.connect(self._ui_listo_dia)
        self.btn_enviar_cierre_semanal.clicked.connect(self._ui_send_cierre_semanal)
        self.btn_exportar_boletas.clicked.connect(self._ui_exportar_boletas)
        self.btn_exportarAuditoria.clicked.connect(self._ui_exportar_auditoria)
        self.btn_nuevaSolicitud.clicked.connect(self._ui_nueva_solicitud)
        self.btn_editarSolicitud.clicked.connect(self._ui_editar_solicitud)
        self.btn_cerrarSesion.clicked.connect(self._ui_cerrar_sesion)
        self.btn_aud_buscar.clicked.connect(lambda: self._ui_buscar_auditoria(self.input_aud_buscar.text()))
        self.btn_aud_limpiar.clicked.connect(self._ui_limpiar_auditoria)
        
        # NUEVO: Conexión del botón de notificaciones al controlador
        self.btn_notificaciones.clicked.connect(self._ui_abrir_notificaciones)
        
        # NUEVO: Conexión del botón para abrir boletas archivadas
        self.btn_abrir_boleta_archivo.clicked.connect(self._ui_abrir_boleta_archivada)

        # calendar selection shows archive items
        self.calendar_widget.clicked.connect(self._on_calendar_date_selected)

    # Theme toggle (applies full stylesheet including combobox popup)
    def toggle_theme(self, DashboardMain: QMainWindow):
        if self._theme == "Oscuro":
            QMainWindow.setStyleSheet(DashboardMain, self._styles_claro)
            self._theme = "Claro"
            try:
                self.btn_tema.setText("🌞 Claro")
            except Exception:
                pass
        else:
            QMainWindow.setStyleSheet(DashboardMain, self._styles_oscuro)
            self._theme = "Oscuro"
            try:
                self.btn_tema.setText("🌙 Oscuro")
            except Exception:
                pass

    def mostrar_snippet(self):
        try:
            # buscar módulo snippet_ui (archivo snippet_ui.py en el mismo directorio)
            if os.path.exists("contador_ui.py"):
                spec = importlib.import_module("snippet_ui")
                if hasattr(spec, "SnippetWidget"):
                    Snip = getattr(spec, "SnippetWidget")
                    widget = Snip()
                    # Si devuelve un widget, lo insertamos como página
                    if isinstance(widget, QWidget):
                        # remover página previa si ya existe
                        if hasattr(self, "page_snippet") and self.page_snippet in [self.stacked_main.widget(i) for i in range(self.stacked_main.count())]:
                            # replace
                            idx = self.stacked_main.indexOf(self.page_snippet)
                            if idx != -1:
                                self.stacked_main.removeWidget(self.page_snippet)
                        self.page_snippet = widget
                        self.stacked_main.addWidget(self.page_snippet)
                        self.stacked_main.setCurrentWidget(self.page_snippet)
                        return
            # si no hay archivo o clase, mostrar placeholder
            placeholder = QWidget()
            layout = QVBoxLayout(placeholder); layout.setContentsMargins(24,24,24,24); layout.setSpacing(12)
            lbl = QLabel("🔧En desarrollo")
            lbl.setStyleSheet("font-size:18px; font-weight:700;")
            desc = QLabel("No se encontró 'contador_ui.py' con 'SnippetWidget'. Coloca el archivo en la misma carpeta para que se cargue automáticamente.\n\nMientras tanto, esto es un placeholder.")
            desc.setWordWrap(True)
            self.page_snippet = placeholder
            self.stacked_main.addWidget(self.page_snippet)
            self.stacked_main.setCurrentWidget(self.page_snippet)
        except Exception as e:
            QMessageBox.critical(None, "Error snippet", f"Error al cargar snippet: {e}")

    # configurar visibilidad por rol (ajustada a tus reglas)
    def configurar_visibilidad_por_rol(self, rol: str):
        r = (rol or "").lower().strip()
        # hide all initial
        for btn in [self.btn_gestion, self.btn_boletas, self.btn_cierre, self.btn_auditoria, self.btn_reportes, self.btn_config]:
            btn.setVisible(False)
        # hide special by default
        self.btn_enviar_cierre_actual.setVisible(False)
        self.btn_listo_dia.setVisible(False)
        self.btn_enviar_cierre_semanal.setVisible(False)
        self.btn_exportar_boletas.setVisible(False)
        self.btn_exportarAuditoria.setVisible(False)
        self.btn_nuevaSolicitud.setVisible(False)
        self.btn_editarSolicitud.setVisible(False)
        # restore all columns and header text
        if hasattr(self, "table_solicitudes"):
            for i in range(self.table_solicitudes.columnCount()):
                self.table_solicitudes.setColumnHidden(i, False)
            headers = ["Número Boleta", "Extensión", "Nombre", "Páginas", "Estado", "Acciones"]
            for i, h in enumerate(headers):
                item = self.table_solicitudes.horizontalHeaderItem(i)
                if item:
                    item.setText(h)
        # USER
        if r == "usuario":
            self.btn_gestion.setVisible(True)
            self.btn_config.setVisible(True)
            self.btn_nuevaSolicitud.setVisible(True)
            self.btn_calendario.setVisible(False)
            self.lbl_totalUsuarios.setVisible(False)
            self.lbl_totalBoletas.setVisible(False)
            self.btn_contador.setVisible(False)
            self.stacked_main.setCurrentWidget(self.page_gestion)
            # hide pages/state/actions by header name
            if hasattr(self, "table_solicitudes"):
                hide = ("páginas","paginas","estado","acciones")
                for i in range(self.table_solicitudes.columnCount()):
                    hi = self.table_solicitudes.horizontalHeaderItem(i)
                    if hi and hi.text().strip().lower() in hide:
                        self.table_solicitudes.setColumnHidden(i, True)
                # rename Actions -> Enviar if exists (for clarity)
                for i in range(self.table_solicitudes.columnCount()):
                    hi = self.table_solicitudes.horizontalHeaderItem(i)
                    if hi and hi.text().strip().lower() == "acciones":
                        hi.setText("Enviar")
                        break
        # OPERADOR
        elif r == "operador":
            self.btn_gestion.setVisible(True)
            self.btn_cierre.setVisible(True)
            self.btn_config.setVisible(True)
            self.btn_enviar_cierre_actual.setVisible(True)
            self.btn_listo_dia.setVisible(True)
            self.btn_calendario.setVisible(True)
            self.btn_calendario.setVisible(False)
            hoy = QDate.currentDate()
            self.btn_enviar_cierre_semanal.setVisible(hoy.dayOfWeek() == 5)
            self.btn_exportar_boletas.setVisible(False)
            # operador sees all columns
            if hasattr(self, "table_solicitudes"):
                for i in range(self.table_solicitudes.columnCount()):
                    self.table_solicitudes.setColumnHidden(i, False)
            self.stacked_main.setCurrentWidget(self.page_gestion)
        # ENCARGADO
        elif r == "encargado":
            self.btn_gestion.setVisible(True)
            self.btn_boletas.setVisible(True)
            self.btn_config.setVisible(True)
            self.btn_nuevaSolicitud.setVisible(True)
            self.lbl_totalUsuarios.setVisible(False)
            self.lbl_totalBoletas.setVisible(False)
            self.btn_contador.setVisible(False)
            # encargado can export boletas
            self.btn_exportar_boletas.setVisible(False)
            self.stacked_main.setCurrentWidget(self.page_boletas)
            # hide pages/state/actions columns in management
            if hasattr(self, "table_solicitudes"):
                hide = ("páginas","paginas","estado","acciones")
                for i in range(self.table_solicitudes.columnCount()):
                    hi = self.table_solicitudes.horizontalHeaderItem(i)
                    if hi and hi.text().strip().lower() in hide:
                        self.table_solicitudes.setColumnHidden(i, True)
                for i in range(self.table_solicitudes.columnCount()):
                    hi = self.table_solicitudes.horizontalHeaderItem(i)
                    if hi and hi.text().strip().lower() == "acciones":
                        hi.setText("Enviar")
                        break
        # ADMIN
        elif r in ("admin"):
            for btn in [self.btn_gestion, self.btn_boletas, self.btn_cierre, self.btn_auditoria, self.btn_reportes, self.btn_config]:
                btn.setVisible(True)
            self.btn_nuevaSolicitud.setVisible(True)
            self.btn_editarSolicitud.setVisible(True)
            self.btn_enviar_cierre_actual.setVisible(True)
            self.btn_listo_dia.setVisible(True)
            self.btn_exportar_boletas.setVisible(True)
            self.btn_exportarAuditoria.setVisible(True)
            self.btn_contador.setVisible(True)
            if hasattr(self, "table_solicitudes"):
                for i in range(self.table_solicitudes.columnCount()):
                    self.table_solicitudes.setColumnHidden(i, False)
            self.stacked_main.setCurrentWidget(self.page_boletas)
        else:
            self.btn_gestion.setVisible(True)
            self.stacked_main.setCurrentWidget(self.page_gestion)

    # Gestión: agregar fila (behavior per viewer role)
    def agregar_fila_solicitud(self, numero_boleta: str, extension: str, nombre: str, paginas: str,
                            rol_view: str = "operador", estado: str = "Pendiente", extra_id: str = None):
        r = self.table_solicitudes.rowCount()
        self.table_solicitudes.insertRow(r)
        self.table_solicitudes.setItem(r, 0, QTableWidgetItem(str(numero_boleta)))
        self.table_solicitudes.setItem(r, 1, QTableWidgetItem(str(extension)))
        self.table_solicitudes.setItem(r, 2, QTableWidgetItem(str(nombre)))
        self.table_solicitudes.setItem(r, 3, QTableWidgetItem(str(paginas)))

        if rol_view in ("usuario","encargado"):
            btn_send = QPushButton("Enviar")
            btn_send.clicked.connect(lambda: self._ui_send_from_user(r, numero_boleta, extension, nombre, paginas))
            self.table_solicitudes.setCellWidget(r, 4, btn_send)
        else:
            combo = QComboBox()
            combo.addItems(["Pendiente","En proceso","Listo"])
            combo.setCurrentText(estado)
            combo.currentTextChanged.connect(
                lambda nuevo_estado: self._on_estado_changed_handler(numero_boleta, extension, nuevo_estado)
            )
            self.table_solicitudes.setCellWidget(r, 4, combo)
            
            # ✅ Botones Ver y Rechazar
            btn_ver = QPushButton("Ver")
            btn_ver.setFixedHeight(30)
            btn_ver.setFixedWidth(50)
            btn_ver.clicked.connect(lambda: self._on_ver_handler(numero_boleta, extra_id))
            
            btn_rechazar = QPushButton("Rechazar")
            btn_rechazar.setFixedHeight(30)
            btn_rechazar.setFixedWidth(80)
            btn_rechazar.setStyleSheet("background-color:#E74C3C;color:white;")
            btn_rechazar.clicked.connect(lambda: self._on_rechazar_handler(numero_boleta, extension, nombre))
            
            action_frame = QWidget()
            action_layout = QHBoxLayout(action_frame)
            action_layout.setContentsMargins(0,0,0,0)
            action_layout.addWidget(btn_ver)
            action_layout.addWidget(btn_rechazar)
            self.table_solicitudes.setCellWidget(r, 5, action_frame)
        
        return r
    
    def _on_ver_handler(self, numero_boleta: str, boleta_id: int):
        try:
            if hasattr(self, '_controller_ref') and self._controller_ref:
                self._controller_ref.ver_boleta(numero_boleta, boleta_id)
        except Exception as e:
            print(f"[ERROR] _on_ver_handler: {e}")

    def _on_estado_changed_handler(self, numero_boleta: str, extension: str, nuevo_estado: str):
        try:
            if hasattr(self, '_controller_ref') and self._controller_ref:
                self._controller_ref.cambiar_estado_boleta(numero_boleta, extension, nuevo_estado)
        except Exception as e:
            print(f"[ERROR] _on_estado_changed_handler: {e}")

    def _on_rechazar_handler(self, numero_boleta: str, extension: str, nombre: str):
        try:
            if hasattr(self, '_controller_ref') and self._controller_ref:
                self._controller_ref.rechazar_boleta(numero_boleta, extension, nombre)
        except Exception as e:
            print(f"[ERROR] _on_rechazar_handler: {e}")

    # NUEVO: Abrir panel de notificaciones
    def _ui_abrir_notificaciones(self):
        """Abre panel de notificaciones"""
        try:
            if hasattr(self, '_controller_ref') and self._controller_ref:
                self._controller_ref.abrir_panel_notificaciones()
            # Reset contador
            if hasattr(self, "lbl_notifCount"):
                self.lbl_notifCount.setVisible(False)
        except Exception as e:
            print(f"[ERROR] _ui_abrir_notificaciones: {e}")

    # NUEVO: Editar boleta del día actual (operador) - SOLO EN CIERRE
    def _ui_editar_boleta_operador(self, numero_boleta: str, extension: str, nombre: str):
        """
        Permite al operador editar una boleta del día actual.
        Al guardar, solicita justificación de cambios.
        """
        try:
            # Verificar que sea del día actual
            hoy = QDate.currentDate().dayOfWeek()
            dias_map = {1:"Lunes",2:"Martes",3:"Miércoles",4:"Jueves",5:"Viernes"}
            dia_actual = dias_map.get(hoy, "Viernes")
            
            print(f"[INFO] Editando boleta {numero_boleta} del día {dia_actual}")
            
            # TODO: Abrir formulario de edición de boleta (controlado por solicitud_controller)
            # Al guardar, mostrar diálogo de justificación
            
            # Simular guardado y solicitar justificación
            confirm = QMessageBox.question(None, "Editar boleta", 
                f"¿Abrir boleta {numero_boleta} para edición?\n\n"
                f"Operador: {nombre} (Ext: {extension})",
                QMessageBox.Yes | QMessageBox.No)
            
            if confirm == QMessageBox.Yes:
                # TODO: solicitud_controller.abrir_boleta_edicion(numero_boleta)
                # Cuando guarde, mostrar diálogo de justificación
                dialog = JustificacionDialog(None, 
                    "Justificar cambios", 
                    "Explique los cambios realizados en la boleta:")
                
                if dialog.exec() == QDialog.Accepted:
                    justificacion = dialog.get_justificacion()
                    if justificacion.strip():
                        print(f"[INFO] Cambios justificados: {justificacion}")
                        # TODO: solicitud_controller.guardar_boleta_con_justificacion(numero_boleta, justificacion)
                        QMessageBox.information(None, "Guardado", 
                            "Boleta editada y cambios registrados.\n\n"
                            "TODO: Conectar con solicitud_controller")
                    else:
                        QMessageBox.warning(None, "Justificación requerida", 
                            "Debe proporcionar una justificación para los cambios.")
        except Exception as e:
            print(f"[ERROR] _ui_editar_boleta_operador: {e}")

    # NUEVO: Rechazar boleta (operador)
    def _ui_rechazar_boleta(self, numero_boleta: str, extension: str, nombre: str):
        """
        Permite al operador rechazar una boleta.
        Solicita comentario de rechazo y envía alerta en tiempo real al usuario.
        """
        try:
            dialog = JustificacionDialog(None, 
                "Rechazar boleta", 
                f"¿Por qué se rechaza la boleta {numero_boleta}?\n\n"
                "El usuario recibirá una alerta en tiempo real con este comentario.")
            
            if dialog.exec() == QDialog.Accepted:
                comentario = dialog.get_justificacion()
                if comentario.strip():
                    print(f"[INFO] Boleta {numero_boleta} rechazada. Comentario: {comentario}")
                    
                    # TODO: solicitud_controller.rechazar_boleta(numero_boleta, extension, comentario)
                    # Esto enviará una alerta en tiempo real al usuario
                    
                    # Remover de tabla (simular)
                    for r in range(self.table_solicitudes.rowCount()):
                        it = self.table_solicitudes.item(r, 0)
                        if it and it.text() == str(numero_boleta):
                            self.table_solicitudes.removeRow(r)
                            break
                    
                    QMessageBox.information(None, "Boleta rechazada", 
                        "La boleta ha sido rechazada y se ha enviado una alerta al usuario.\n\n"
                        "TODO: Conectar con solicitud_controller.rechazar_boleta()")
                else:
                    QMessageBox.warning(None, "Comentario requerido", 
                        "Debe proporcionar un comentario explicando el rechazo.")
        except Exception as e:
            print(f"[ERROR] _ui_rechazar_boleta: {e}")

    # NUEVO: Botón "Listo día" para cerrar la boleta de cierre
    def _ui_listo_dia(self):
        """
        Marca el día como listo y cierra la boleta de cierre.
        Manejado por cierre_controller.py
        """
        try:
            confirm = QMessageBox.question(None, "Listo día", 
                "¿Marcar el día como listo y cerrar la boleta de cierre?\n\n"
                "Esta acción finalizará el procesamiento del día actual.",
                QMessageBox.Yes | QMessageBox.No)
            
            if confirm == QMessageBox.Yes:
                print("[INFO] Marcando día como listo...")
                # TODO: cierre_controller.marcar_dia_listo()
                QMessageBox.information(None, "Día cerrado", 
                    "El día ha sido marcado como listo.\n\n"
                    "TODO: Conectar con cierre_controller.marcar_dia_listo()")
        except Exception as e:
            print(f"[ERROR] _ui_listo_dia: {e}")

    # NUEVO: Abrir boleta archivada en modo lectura
    def _ui_abrir_boleta_archivada(self):
        """Abre boleta archivada"""
        try:
            if not hasattr(self, "list_calendar_entries"):
                return
            
            current = self.list_calendar_entries.currentItem()
            if not current:
                QMessageBox.warning(None, "Sin selección", 
                    "Seleccione una boleta de la lista.")
                return
            
            texto = current.text()
            # Extraer número de boleta (formato: "Boleta B-1234 — ...")
            import re
            match = re.search(r'B-\d+', texto)
            if not match:
                QMessageBox.warning(None, "Error", "No se pudo extraer número de boleta")
                return
            
            numero_boleta = match.group()
            
            # Obtener ID
            if hasattr(self, '_controller_ref') and self._controller_ref:
                try:
                    self._controller_ref.conexion.rollback()
                except:
                    pass
                
                cur = self._controller_ref.conexion.cursor()
                cur.execute("SELECT id FROM boletas WHERE numero_boleta = %s", (numero_boleta,))
                row = cur.fetchone()
                cur.close()
                
                if row:
                    self._controller_ref.ver_boleta(numero_boleta, row[0])
            
        except Exception as e:
            print(f"[ERROR] _ui_abrir_boleta_archivada: {e}")
            traceback.print_exc()

    # NUEVO: Método para actualizar texto de boleta de cierre
    def actualizar_texto_boleta_cierre(self, texto: str):
        """
        Actualiza el contenido de la boleta de cierre.
        Llamado por cierre_controller.py
        """
        try:
            if hasattr(self, "text_boleta_cierre"):
                self.text_boleta_cierre.setPlainText(texto)
                print("[INFO] Texto de boleta de cierre actualizado")
        except Exception as e:
            print(f"[ERROR] actualizar_texto_boleta_cierre: {e}")

    # UI demo: when user sends a request -> move to boletas day container (simulation)
    def _ui_send_from_user(self, row: int, numero_boleta: str, extension: str, nombre: str, paginas: str):
        confirm = QMessageBox.question(None, "Enviar solicitud", f"Enviar boleta {numero_boleta} (Ext {extension}) al operador?", QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return
        dow = QDate.currentDate().dayOfWeek()
        dias_map = {1:"Lunes",2:"Martes",3:"Miércoles",4:"Jueves",5:"Viernes"}
        dia_str = dias_map.get(dow,"Viernes")
        resumen = f"De: {nombre} (Ext: {extension}) • {paginas} páginas"
        # add to in-memory boletas data (store metadata)
        meta = {"boleta": numero_boleta, "ext": extension, "nombre": nombre, "paginas": paginas, "estado": "Pendiente", "dia": dia_str}
        self._boletas_data[dia_str].insert(0, meta)
        # If current visible day equals dia_str, refresh UI
        if self.combo_boletas_dia.currentText() == dia_str:
            self._refresh_boletas_day_ui(dia_str)
        # remove row from table (search by boleta number)
        try:
            for r in range(self.table_solicitudes.rowCount()):
                it = self.table_solicitudes.item(r,0)
                if it and it.text() == str(numero_boleta):
                    self.table_solicitudes.removeRow(r)
                    break
        except Exception:
            pass
        QMessageBox.information(None, "Enviado", "Solicitud enviada al operador (UI-demo).")
        # TODO: controller.enviar_solicitud(...)

    # Build a card widget from metadata
    def _build_card_from_meta(self, meta: dict, es_cierre: bool = False):
        titulo = f"Boleta {meta.get('boleta')}"
        resumen = f"De: {meta.get('nombre')} (Ext: {meta.get('ext')}) • {meta.get('paginas')} páginas"
        card = QFrame()
        card.setObjectName("card_boleta")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10,10,10,10)
        layout.setSpacing(8)
        
        lbl_title = QLabel(titulo)
        lbl_title.setStyleSheet("font-weight:700;")
        lbl_meta = QLabel(f"Ext: {meta.get('ext')} • {meta.get('paginas')} páginas • {meta.get('estado')}")
        lbl_meta.setStyleSheet("font-size:12px; color: rgba(0,0,0,0.6);")
        lbl_res = QLabel(resumen)
        lbl_res.setWordWrap(True)
        lbl_res.setStyleSheet("font-size:12px;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_meta)
        layout.addWidget(lbl_res)
        
        btns = QHBoxLayout()
        btn_ver = QPushButton("Ver")
        btn_ver.setFixedHeight(30)
        btn_ver.setFixedWidth(60)
        btn_ver.clicked.connect(lambda _, m=meta: self._ui_ver_boleta_cierre(m.get('boleta')))
        
        if es_cierre:
            btn_editar = QPushButton("Editar")
            btn_editar.setFixedHeight(30)
            btn_editar.setFixedWidth(80)
            btn_editar.clicked.connect(lambda _, m=meta: self._ui_editar_con_justificacion(m.get('boleta')))
            btns.addWidget(btn_ver)
            btns.addWidget(btn_editar)
        else:
            btn_listo = QPushButton("Listo")
            btn_listo.setFixedHeight(30)
            btn_listo.setFixedWidth(80)
            btn_listo.clicked.connect(lambda _, m=meta, c=card: self._ui_mark_listo_and_archive(m, c))
            btns.addWidget(btn_ver)
            btns.addWidget(btn_listo)
        
        btns.addItem(QSpacerItem(10,10,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum))
        layout.addLayout(btns)
        card.setProperty("meta", meta)
        return card

    def _ui_ver_boleta_cierre(self, numero_boleta: str):
        """Ver boleta desde cierre"""
        try:
            if hasattr(self, '_controller_ref') and self._controller_ref:
                # Buscar ID de boleta
                cur = self._controller_ref.conexion.cursor()
                cur.execute("SELECT id FROM boletas WHERE numero_boleta = %s", (numero_boleta,))
                row = cur.fetchone()
                cur.close()
                
                if row:
                    self._controller_ref.ver_boleta(numero_boleta, row[0])
        except Exception as e:
            print(f"[ERROR] _ui_ver_boleta_cierre: {e}")

    def _ui_editar_con_justificacion(self, numero_boleta: str):
        """Editar con justificación posterior"""
        try:
            if not hasattr(self, '_controller_ref') or not self._controller_ref:
                return
            
            # Buscar ID
            cur = self._controller_ref.conexion.cursor()
            cur.execute("SELECT id FROM boletas WHERE numero_boleta = %s", (numero_boleta,))
            row = cur.fetchone()
            cur.close()
            
            if not row:
                QMessageBox.warning(None, "Error", "Boleta no encontrada")
                return
            
            boleta_id = row[0]
            
            # Abrir para edición
            from ui.boleta_form_ui import Ui_BoletaForm
            from controllers.boleta_controller import BoletaController
            
            window = QMainWindow()
            window.setWindowTitle(f"Editar Boleta {numero_boleta}")
            
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            
            content_widget = QWidget()
            ui_form = Ui_BoletaForm()
            ui_form.setupUi(content_widget)
            
            scroll_area.setWidget(content_widget)
            window.setCentralWidget(scroll_area)
            window.resize(800, 600)
            
            boleta_ctrl = BoletaController(
                ui=ui_form,
                conexion=self._controller_ref.conexion,
                usuario=self._controller_ref.usuario,
                auditoria_ctrl=self._controller_ref.auditoria_ctrl,
                solicitudes_ctrl=self._controller_ref.solicitudes_ctrl,
                modo="edit",
                parent_window=window,
                boleta_id=boleta_id
            )
            
            # ✅ Override: guardar primero, justificación después
            original_guardar = boleta_ctrl.guardar_cambios_operador
            
            def guardar_con_justificacion():
                # 1. Guardar cambios
                try:
                    data = ui_form.get_all_data()
                    
                    try:
                        self._controller_ref.conexion.rollback()
                    except:
                        pass
                    
                    cur = self._controller_ref.conexion.cursor()
                    # Línea del UPDATE (ya debe estar):
                    cur.execute("""
                        UPDATE boletas 
                        SET observaciones = COALESCE(observaciones, '') || E'\n\n════════════════════════════════\n      🔧 JUSTIFICACIÓN DE EDICIÓN\n════════════════════════════════\n' || %s || E'\n════════════════════════════════'
                        WHERE id = %s
                    """, (justificacion, boleta_id))
                    (
                        json.dumps(data.get("empaste", {})),
                        data.get("observaciones_servicio", ""),
                        data.get("operador", {}).get("nombre", ""),
                        boleta_id
                    )
                    self._controller_ref.conexion.commit()
                    cur.close()
                    
                except Exception as e:
                    print(f"[ERROR] guardar_con_justificacion: {e}")
                    try:
                        self._controller_ref.conexion.rollback()
                    except:
                        pass
                    QMessageBox.critical(None, "Error", f"No se pudo guardar:\n{e}")
                    return
                
                # 2. Pedir justificación
                dialog = JustificacionDialog(None, "Justificar cambios",
                    "Explique los cambios realizados:")
                
                if dialog.exec() == QDialog.Accepted:
                    justificacion = dialog.get_justificacion()
                    if justificacion.strip():
                        # 3. Guardar justificación con formato
                        try:
                            cur = self._controller_ref.conexion.cursor()
                            cur.execute("""
                                UPDATE boletas 
                                SET observaciones = COALESCE(observaciones, '') || E'\n\n════════════════════════════════\n      🔧 JUSTIFICACIÓN DE EDICIÓN\n════════════════════════════════\n' || %s || E'\n════════════════════════════════'
                                WHERE id = %s
                            """, (justificacion, boleta_id))
                            self._controller_ref.conexion.commit()
                            cur.close()
                            
                            QMessageBox.information(None, "✓ Guardado", 
                                "Cambios y justificación guardados correctamente.")
                            window.close()
                            
                            # Actualizar vista de cierre
                            dia = self._controller_ref.ui.combo_cierre_dia.currentText()
                            if dia:
                                self._controller_ref._actualizar_vista_cierre(dia)
                            
                        except Exception as e:
                            print(f"[ERROR] guardar justificación: {e}")
                            QMessageBox.critical(None, "Error", f"No se pudo guardar justificación:\n{e}")
                    else:
                        QMessageBox.warning(None, "Justificación requerida",
                            "Debe proporcionar una justificación para los cambios.")
                else:
                    # Canceló la justificación, deshacer cambios
                    try:
                        self._controller_ref.conexion.rollback()
                    except:
                        pass
                    QMessageBox.information(None, "Cancelado", "Cambios descartados.")
                    window.close()
            
            boleta_ctrl.guardar_cambios_operador = guardar_con_justificacion
            window._boleta_controller = boleta_ctrl
            window.show()
            
        except Exception as e:
            print(f"[ERROR] _ui_editar_con_justificacion: {e}")
            traceback.print_exc()

    # Refresh day UI (clear & rebuild from _boletas_data[dia])
    def _refresh_boletas_day_ui(self, dia: str):
        # clear UI container
        for i in reversed(range(self.boletas_day_layout.count())):
            item = self.boletas_day_layout.itemAt(i)
            if item and item.widget():
                w = item.widget()
                self.boletas_day_layout.removeWidget(w)
                w.setParent(None)
        # add cards from data
        items = self._boletas_data.get(dia, [])
        for meta in items:
            card = self._build_card_from_meta(meta, es_cierre=False)
            # insert before spacer (at end of list area)
            self.boletas_day_layout.insertWidget(self.boletas_day_layout.count()-1, card)
        # if none, container remains with spacer

    # NUEVO: Refresh cierre day UI (muestra boletas del día actual con botón editar)
    def _refresh_cierre_day_ui(self, dia: str):
        """
        Actualiza la vista de cierre con las boletas del día actual.
        Incluye botón de editar para cada boleta.
        """
        try:
            if not hasattr(self, "cierre_day_layout"):
                return
            
            # Limpiar contenedor
            for i in reversed(range(self.cierre_day_layout.count())):
                item = self.cierre_day_layout.itemAt(i)
                if item and item.widget():
                    w = item.widget()
                    self.cierre_day_layout.removeWidget(w)
                    w.setParent(None)
            
            # Agregar cards del día
            items = self._boletas_data.get(dia, [])
            for meta in items:
                card = self._build_card_from_meta(meta, es_cierre=True)
                self.cierre_day_layout.insertWidget(self.cierre_day_layout.count()-1, card)
            
            print(f"[INFO] Vista de cierre actualizada para {dia}: {len(items)} boletas")
        except Exception as e:
            print(f"[ERROR] _refresh_cierre_day_ui: {e}")

    # When day combobox changes (robust: soporta llamadas manuales donde sender() es None)
    def _on_boletas_dia_changed(self, idx: int = None):
        """
        Actualiza la vista de Boletas cuando cambia el combo de días.
        Este método es robusto: cuando lo llamás manualmente (ej: en __init__) sender() es None,
        así que usa self.combo_boletas_dia directamente.
        """
        try:
            combo = self.sender() or getattr(self, "combo_boletas_dia", None)
            if combo is None:
                # No hay combo (UI no inicializada). No hacer nada.
                print("[WARN] _on_boletas_dia_changed: combo_boletas_dia no encontrado.")
                return
            dia = combo.currentText()
            if not dia:
                print("[WARN] _on_boletas_dia_changed: día vacío")
                return
            print(f"[INFO] Día seleccionado en Boletas: {dia}")
            # Actualizar la UI con los datos guardados en _boletas_data
            # Si no existe la estructura, crea una por seguridad
            if not hasattr(self, "_boletas_data"):
                self._boletas_data = {d: [] for d in ["Lunes","Martes","Miércoles","Jueves","Viernes"]}
            # Limpiar la vista actual y reconstruir a partir de _boletas_data[dia]
            self._refresh_boletas_day_ui(dia)
        except Exception as e:
            print(f"[ERROR] _on_boletas_dia_changed: {e}")

    # Evento: cambio de dia en combo de cierre (robusto)
    def _on_combo_cierre_changed(self, idx: int = None):
        """
        Handler para el combo de cierre. Es robusto ante llamadas manuales (sender() puede ser None).
        Actualiza la vista de cierre con las boletas del día seleccionado.
        """
        try:
            combo = self.sender() or getattr(self, "combo_cierre_dia", None)
            if combo is None:
                print("[WARN] _on_combo_cierre_changed: combo_cierre_dia no encontrado.")
                return
            dia = combo.currentText()
            if dia:
                print(f"[INFO] Día seleccionado en Cierre: {dia}")
                # Actualizar vista de cierre
                self._refresh_cierre_day_ui(dia)
                # TODO: Llamar a controller para obtener texto de boleta de cierre
                # cierre_controller.obtener_boleta_cierre_dia(dia)
        except Exception as e:
            print(f"[ERROR] _on_combo_cierre_changed: {e}")

    # Mark as 'Listo' -> archive to calendar and remove from boletas_data/UI
    # (robust and safe)
    def _ui_mark_listo_and_archive(self, meta: dict, card_widget: QWidget):
        try:
            confirm = QMessageBox.question(None, "Marcar listo", f"¿Marcar {meta.get('boleta')} como listo y archivar en Calendario Anual?", QMessageBox.Yes | QMessageBox.No)
            if confirm != QMessageBox.Yes:
                return
            today = QDate.currentDate().toString("yyyy-MM-dd")
            entry = {"boleta": meta.get("boleta"), "ext": meta.get("ext"), "nombre": meta.get("nombre"), "paginas": meta.get("paginas")}
            if not hasattr(self, "_calendar_archive"):
                self._calendar_archive = {}
            if today not in self._calendar_archive:
                self._calendar_archive[today] = []
            self._calendar_archive[today].append(entry)
            # Remove from _boletas_data
            dia = meta.get("dia")
            if hasattr(self, "_boletas_data") and dia in self._boletas_data:
                self._boletas_data[dia] = [m for m in self._boletas_data[dia] if m.get("boleta") != meta.get("boleta")]
            # Remove card widget safely
            try:
                if card_widget is not None:
                    self.boletas_day_layout.removeWidget(card_widget)
                    card_widget.setParent(None)
            except Exception:
                pass
            QMessageBox.information(None, "Archivado", "Boleta marcada como lista y archivada en Calendario Anual (UI-demo).")
            # Si el calendario muestra la fecha de hoy, refrescar la lista
            if hasattr(self, "calendar_widget"):
                cal_selected = self.calendar_widget.selectedDate().toString("yyyy-MM-dd")
                if cal_selected == today:
                    self._populate_calendar_list_for_date(today)
            # TODO: Persistir con controller.marcar_listo_y_archivar(meta)
        except Exception as e:
            print(f"[ERROR] _ui_mark_listo_and_archive: {e}")

    # Calendar: when date selected, populate right list with archived boletas
    def _on_calendar_date_selected(self, qdate):
        try:
            date_str = qdate.toString("yyyy-MM-dd")
            self._populate_calendar_list_for_date(date_str)
            # show calendar page so user sees archived items
            if hasattr(self, "stacked_main") and hasattr(self, "page_calendar"):
                self.stacked_main.setCurrentWidget(self.page_calendar)
        except Exception as e:
            print(f"[ERROR] _on_calendar_date_selected: {e}")

    def _populate_calendar_list_for_date(self, date_str: str):
        try:
            if not hasattr(self, "list_calendar_entries"):
                print("[WARN] _populate_calendar_list_for_date: list_calendar_entries no inicializado.")
                return
            self.list_calendar_entries.clear()
            items = getattr(self, "_calendar_archive", {}).get(date_str, [])
            for it in items:
                text = f"Boleta {it.get('boleta')} — Ext {it.get('ext')} — {it.get('nombre')} — {it.get('paginas')} pág."
                QListItem = QListWidgetItem(text)
                self.list_calendar_entries.addItem(QListItem)
        except Exception as e:
            print(f"[ERROR] _populate_calendar_list_for_date: {e}")

    # Cierre send UI placeholders
    def _ui_send_cierre_actual(self):
        try:
            confirm = QMessageBox.question(None, "Enviar cierre actual", "¿Confirmas enviar el cierre del día actual a encargado/admin?", QMessageBox.Yes | QMessageBox.No)
            if confirm != QMessageBox.Yes:
                return
            QMessageBox.information(None, "Envío", "Solicitud de envío del cierre actual registrada (TODO: controlador).")
            # TODO: controller.enviar_cierre_actual()
        except Exception as e:
            print(f"[ERROR] _ui_send_cierre_actual: {e}")

    def _ui_send_cierre_semanal(self):
        try:
            confirm = QMessageBox.question(None, "Enviar cierre semanal", "¿Confirmas enviar el cierre semanal? (Habilitado solo los viernes)", QMessageBox.Yes | QMessageBox.No)
            if confirm != QMessageBox.Yes:
                return
            QMessageBox.information(None, "Envío", "Solicitud de envío del cierre semanal registrada (TODO: controlador).")
            # TODO: controller.enviar_cierre_semanal()
        except Exception as e:
            print(f"[ERROR] _ui_send_cierre_semanal: {e}")

    # Export functions (open save dialog; controller should implement actual work)
    def _ui_exportar_boletas(self):
        try:
            path, _ = QFileDialog.getSaveFileName(None, "Exportar boletas a Excel", "", "Excel Files (*.xlsx);;CSV Files (*.csv)")
            if not path:
                return
            QMessageBox.information(None, "Exportar", f"Petición de exportación guardada en: {path}\n(TODO: controller.exportar_boletas_excel(path, dias_seleccionados))")
        except Exception as e:
            print(f"[ERROR] _ui_exportar_boletas: {e}")

    def _ui_exportar_auditoria(self):
        try:
            path, _ = QFileDialog.getSaveFileName(None, "Exportar auditoría a Excel", "", "Excel Files (*.xlsx);;CSV Files (*.csv)")
            if not path:
                return
            QMessageBox.information(None, "Exportar", f"Petición de exportación auditoría guardada en: {path}\n(TODO: controller.exportar_auditoria_excel(path))")
        except Exception as e:
            print(f"[ERROR] _ui_exportar_auditoria: {e}")

    # Search placeholders
    def _ui_buscar_boletas(self, q: str):
        try:
            QMessageBox.information(None, "Buscar", f"Buscar boletas: {q} (TODO: controller.buscar_boletas)")
        except Exception as e:
            print(f"[ERROR] _ui_buscar_boletas: {e}")

    def _ui_buscar_auditoria(self, q: str):
        try:
            QMessageBox.information(None, "Buscar Auditoría", f"Buscar auditoría: {q} (TODO: controller.buscar_auditoria)")
        except Exception as e:
            print(f"[ERROR] _ui_buscar_auditoria: {e}")

    def _ui_limpiar_auditoria(self):
        try:
            for i in reversed(range(self.table_auditoria.rowCount())):
                self.table_auditoria.removeRow(i)
            QMessageBox.information(None, "Limpiar", "Filtro de auditoría limpiado (UI).")
        except Exception as e:
            print(f"[ERROR] _ui_limpiar_auditoria: {e}")

    # New / Edit placeholders
    def _ui_nueva_solicitud(self):
        QMessageBox.information(None, "Nueva Solicitud", "Abrir formulario nueva solicitud (TODO: conectar formulario/controller).")

    def _ui_editar_solicitud(self):
        QMessageBox.information(None, "Editar", "Abrir editor de boleta (TODO: conectar controlador).")

    # Close session
    def _ui_cerrar_sesion(self):
        try:
            confirm = QMessageBox.question(None, "Cerrar sesión", "¿Desea cerrar sesión?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                # TODO: controller.logout()
                QApplication.quit()
        except Exception as e:
            print(f"[ERROR] _ui_cerrar_sesion: {e}")

    # Audit helper
    def agregar_auditoria(self, fecha: str, extension: str, accion: str, detalle: str):
        try:
            r = self.table_auditoria.rowCount()
            self.table_auditoria.insertRow(r)
            self.table_auditoria.setItem(r,0,QTableWidgetItem(str(fecha)))
            self.table_auditoria.setItem(r,1,QTableWidgetItem(str(extension)))
            self.table_auditoria.setItem(r,2,QTableWidgetItem(str(accion)))
            self.table_auditoria.setItem(r,3,QTableWidgetItem(str(detalle)))
            return r
        except Exception as e:
            print(f"[ERROR] agregar_auditoria: {e}")
            return -1

    # Update user info and apply role visibility
    def actualizar_info_usuario(self, nombre: str, extension: str, rol: str = None):
        try:
            self.lbl_bienvenida.setText(f"Bienvenido, {nombre}")
            if hasattr(self, "lbl_usuario"):
                self.lbl_usuario.setText(nombre)
            if hasattr(self, "lbl_extension"):
                self.lbl_extension.setText(extension)
            if rol and hasattr(self, "lbl_rol"):
                self.lbl_rol.setText(rol)
            # apply role visibility (robust)
            self.configurar_visibilidad_por_rol(rol)
        except Exception as e:
            print(f"[ERROR] actualizar_info_usuario: {e}")

# ======================================================
# Clase principal del Dashboard
# ======================================================
class DashboardWindow(QMainWindow, Ui_DashboardMain):
    def __init__(self, usuario_data: dict):
        super().__init__()
        self.setupUi(self)

        # Extraer datos del dict
        self.usuario = usuario_data.get("usuario", usuario_data.get("extension", ""))
        self.rol = usuario_data.get("rol", "usuario")
        self.nombre_completo = usuario_data.get("nombre_completo", "Usuario")
        
        # IMPORTANTE: Controller se asigna DESPUÉS
        self.controller = None

        # Personalizar etiquetas
        try:
            self.lbl_bienvenida.setText(f"Bienvenido, {self.nombre_completo}")
            self.lbl_usuario.setText(self.usuario)
            self.lbl_rol.setText(self.rol.capitalize())
        except Exception as e:
            print(f"[WARN] No se pudieron actualizar etiquetas de usuario: {e}")

        # Configurar interfaz según el rol
        try:
            self.configurar_visibilidad_por_rol(self.rol)
        except Exception as e:
            print(f"[WARN] No se pudo configurar visibilidad por rol: {e}")

        print(f"[INFO] DashboardWindow iniciado para usuario={self.usuario}, rol={self.rol}")

    def set_controller(self, controller):
        """
        MÉTODO CRÍTICO: Conecta el controller con la UI
        Llamado por login_controller.py después de crear el DashboardController
        """
        self.controller = controller
        print("[OK] Controller conectado a la UI")
        
        # Reconectar señales con el controller (desconectar placeholders primero)
        try:
            # GESTIÓN
            try:
                self.btn_actualizar.clicked.disconnect()
            except:
                pass
            self.btn_actualizar.clicked.connect(self.controller.cargar_solicitudes)
            
            try:
                self.btn_nuevaSolicitud.clicked.disconnect()
            except:
                pass
            self.btn_nuevaSolicitud.clicked.connect(self.controller.nueva_solicitud)
            
            try:
                self.btn_editarSolicitud.clicked.disconnect()
            except:
                pass
            self.btn_editarSolicitud.clicked.connect(self.controller.editar_solicitud)
            
            # BOLETAS      
            try:
                self.combo_boletas_dia.currentTextChanged.disconnect()
            except:
                pass
            self.combo_boletas_dia.currentTextChanged.connect(
                self.controller.cargar_boletas_por_dia
            )
            
            try:
                self.btn_exportar_boletas.clicked.disconnect()
            except:
                pass
            self.btn_exportar_boletas.clicked.connect(self.controller.exportar_boletas_csv)
            
            # CIERRE
            try:
                self.btn_enviar_cierre_actual.clicked.disconnect()
            except:
                pass
            self.btn_enviar_cierre_actual.clicked.connect(self.controller.enviar_cierre_actual)
            
            try:
                self.btn_listo_dia.clicked.disconnect()
            except:
                pass
            self.btn_listo_dia.clicked.connect(self.controller.marcar_dia_listo)
            
            try:
                self.btn_enviar_cierre_semanal.clicked.disconnect()
            except:
                pass
            self.btn_enviar_cierre_semanal.clicked.connect(self.controller.enviar_cierre_semanal)
            
            try:
                self.combo_cierre_dia.currentTextChanged.disconnect()
            except:
                pass
            self.combo_cierre_dia.currentTextChanged.connect(self.controller._on_cierre_dia_changed)
            
            # AUDITORÍA
            try:
                self.btn_aud_buscar.clicked.disconnect()
            except:
                pass
            self.btn_aud_buscar.clicked.connect(
                lambda: self.controller.buscar_auditoria(self.input_aud_buscar.text())
            )
            
            try:
                self.btn_aud_limpiar.clicked.disconnect()
            except:
                pass
            self.btn_aud_limpiar.clicked.connect(self.controller.cargar_auditoria)
            
            try:
                self.btn_exportarAuditoria.clicked.disconnect()
            except:
                pass
            self.btn_exportarAuditoria.clicked.connect(self.controller.exportar_auditoria_csv)
            
            print("[OK] Señales reconectadas al controller")
            
        except Exception as e:
            print(f"[ERROR] set_controller: {e}")
    def _refresh_cierre_day_ui_from_db(self, dia: str, conexion):
        """Carga boletas desde BD para cierre"""
        try:
            if not hasattr(self, "cierre_day_layout"):
                return
            
            # ✅ ROLLBACK
            try:
                conexion.rollback()
            except:
                pass
            
            # Limpiar contenedor
            for i in reversed(range(self.cierre_day_layout.count())):
                item = self.cierre_day_layout.itemAt(i)
                if item and item.widget():
                    w = item.widget()
                    self.cierre_day_layout.removeWidget(w)
                    w.setParent(None)
            
            cur = conexion.cursor()
            cur.execute("""
                SELECT numero_boleta, extension, nombre_usuario, paginas, fecha_procesado
                FROM boletas
                WHERE dia = %s AND estado = 'Listo' AND cerrado = FALSE
                ORDER BY fecha_procesado ASC
            """, (dia,))
            
            for row in cur.fetchall():
                meta = {
                    "boleta": row[0],
                    "ext": row[1],
                    "nombre": row[2],
                    "paginas": row[3],
                    "estado": "Listo",
                    "dia": dia
                }
                card = self._build_card_from_meta(meta, es_cierre=True)
                self.cierre_day_layout.insertWidget(self.cierre_day_layout.count()-1, card)
            
            cur.close()
        except Exception as e:
            print(f"[ERROR] _refresh_cierre_day_ui_from_db: {e}")
            
# DEMO / main
if __name__ == "__main__":
    print("=== DEMO: seleccionar rol de inicio ===")
    print("Opciones válidas: usuario | operador | encargado | admin")
    try:
        rol_demo = input("Ingrese rol para demo (Enter = operador): ").strip().lower()
    except Exception:
        rol_demo = ""
    if not rol_demo:
        rol_demo = "operador"
    rol_demo_map = {"user":"usuario","operator":"operador","encargado":"encargado","admin":"admin","operador":"operador","usuario":"usuario"}
    rol_demo = rol_demo_map.get(rol_demo, rol_demo)

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    # Clase DashboardWindow para DEMO (hereda de la UI base)
    class DashboardWindowDemo(QMainWindow, Ui_DashboardMain):
        def __init__(self, role):
            # Crear usuario_data en formato dict (compatibilidad con controller)
            usuario_data = {
                "usuario": "demo",
                "extension": "101",
                "rol": role,
                "nombre_completo": "Demo Usuario",
                "nombre": "Demo Usuario"
            }
            
            # Llamar al constructor padre
            super().__init__()
            self.setupUi(self)
            
            # Guardar datos de usuario
            self.usuario = usuario_data.get("usuario")
            self.rol = usuario_data.get("rol")
            self.nombre_completo = usuario_data.get("nombre_completo")
            
            # Controller placeholder (para compatibilidad)
            self.controller = None
            
            # Populate demo data & apply role
            self.actualizar_info_usuario("Demo Usuario", "101", role)

            # Populate management table according to role view
            if role in ("usuario","encargado"):
                for i in range(1,7):
                    num = f"B-{2000+i}"; ext = f"20{i}"; nombre = f"Cliente {i}"; paginas = str(1+(i%3))
                    self.agregar_fila_solicitud(num, ext, nombre, paginas, rol_view=role)
            else:
                for i in range(1,9):
                    num = f"B-{1000+i}"; ext = f"10{i}"; nombre = f"Usuario {i}"; paginas = str(2+(i%4))
                    estado = "Pendiente" if i%3!=0 else "Listo"
                    self.agregar_fila_solicitud(num, ext, nombre, paginas, rol_view=role, estado=estado)

            # auditoría demo
            for i in range(4):
                fecha = QDate.currentDate().addDays(-i).toString("yyyy-MM-dd")
                self.agregar_auditoria(fecha, f"10{i}", "Login", "Ingreso al sistema (demo)")

            # boletas demo: add some to different days via internal _boletas_data and refresh UI
            demo_meta = [
                {"boleta":"B-5001","ext":"201","nombre":"Operador A","paginas":"3","estado":"Pendiente","dia":"Lunes"},
                {"boleta":"B-5002","ext":"202","nombre":"Operador B","paginas":"2","estado":"Pendiente","dia":"Martes"},
                {"boleta":"B-5003","ext":"203","nombre":"Operador C","paginas":"1","estado":"Pendiente","dia":"Miércoles"},
                {"boleta":"B-5004","ext":"204","nombre":"Operador D","paginas":"4","estado":"Pendiente","dia":"Viernes"},
            ]
            # asegurar estructura
            if not hasattr(self, "_boletas_data"):
                self._boletas_data = {d: [] for d in ["Lunes","Martes","Miércoles","Jueves","Viernes"]}
            for m in demo_meta:
                self._boletas_data[m["dia"]].insert(0, m)

            # show current combo day (llamada segura: el método maneja sender() None)
            try:
                self._on_boletas_dia_changed(self.combo_boletas_dia.currentIndex())
            except Exception as e:
                print(f"[WARN] error al inicializar vista Boletas: {e}")

            # Inicializar vista de cierre si es operador/admin
            if role in ("operador", "admin"):
                try:
                    dia_actual_idx = QDate.currentDate().dayOfWeek() - 1
                    if 0 <= dia_actual_idx <= 4:
                        dias = ["Lunes","Martes","Miércoles","Jueves","Viernes"]
                        dia_actual = dias[dia_actual_idx]
                        self._refresh_cierre_day_ui(dia_actual)
                        
                        # Simular texto de boleta de cierre
                        texto_demo = f"=== BOLETA DE CIERRE - {dia_actual.upper()} ===\n\n"
                        texto_demo += f"Fecha: {QDate.currentDate().toString('dd/MM/yyyy')}\n"
                        texto_demo += f"Operador: Demo Usuario (Ext: 101)\n\n"
                        texto_demo += "RESUMEN DEL DÍA:\n"
                        texto_demo += f"- Boletas procesadas: {len(self._boletas_data.get(dia_actual, []))}\n"
                        texto_demo += "- Estado: En proceso\n\n"
                        texto_demo += "(Este texto es gestionado por cierre_controller.py)"
                        self.actualizar_texto_boleta_cierre(texto_demo)
                except Exception as e:
                    print(f"[WARN] error al inicializar vista de cierre: {e}")

            # special role visibility tweaks
            if role == "operador":
                self.btn_enviar_cierre_actual.setVisible(True)
                self.btn_listo_dia.setVisible(True)
                if QDate.currentDate().dayOfWeek() == 5:
                    self.btn_enviar_cierre_semanal.setEnabled(True); self.btn_enviar_cierre_semanal.setVisible(True)
                else:
                    self.btn_enviar_cierre_semanal.setEnabled(False); self.btn_enviar_cierre_semanal.setVisible(True)
            if role == "encargado":
                self.btn_exportar_boletas.setVisible(True)
            if role in ("admin"):
                self.btn_exportar_boletas.setVisible(True); self.btn_exportarAuditoria.setVisible(True)
                self.btn_enviar_cierre_actual.setVisible(True)
                self.btn_listo_dia.setVisible(True)
            
            # Simular algunas notificaciones para demo
            if role == "usuario":
                # Usuario tiene 2 notificaciones pendientes
                self.lbl_notifCount.setText("2")
                self.lbl_notifCount.setVisible(True)
            
            # Demo: agregar algunas boletas archivadas al calendario
            hoy = QDate.currentDate().toString("yyyy-MM-dd")
            ayer = QDate.currentDate().addDays(-1).toString("yyyy-MM-dd")
            self._calendar_archive[hoy] = [
                {"boleta": "B-9001", "ext": "301", "nombre": "Usuario Archivo 1", "paginas": "5"},
                {"boleta": "B-9002", "ext": "302", "nombre": "Usuario Archivo 2", "paginas": "3"},
            ]
            self._calendar_archive[ayer] = [
                {"boleta": "B-8001", "ext": "201", "nombre": "Usuario Archivo 3", "paginas": "2"},
            ]

    # Instanciar la ventana DEMO
    w = DashboardWindowDemo(rol_demo)
    w.show()
    sys.exit(app.exec())