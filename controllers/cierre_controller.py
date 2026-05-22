# controllers/cierre_controller.py
# -*- coding: utf-8 -*-
"""
Controller para cierre diario - FLUJO COMPLETO:
1. Recibe boletas en estado "Listo"
2. Contador de usuarios únicos
3. Ordenamiento dinámico
4. Genera boleta de cierre
5. Envía a encargado (solo día actual)
"""

from __future__ import annotations
import os
import datetime
from typing import Optional, List, Dict, Any

from PySide6.QtWidgets import QMainWindow, QWidget, QMessageBox
from PySide6.QtCore import Qt, QDate

try:
    from cierre_form import Ui_CierreForm
except Exception:
    try:
        import sys
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ui_dir = os.path.join(base_dir, "ui")
        if ui_dir not in sys.path:
            sys.path.insert(0, ui_dir)
        from cierre_form import Ui_CierreForm
    except Exception as e:
        Ui_CierreForm = None
        print(f"[WARN] No se pudo importar Ui_CierreForm: {e}")


class CierreController:
    def __init__(self, conexion: Optional[Any] = None,
                 notification_controller: Optional[Any] = None,
                 auditoria_controller: Optional[Any] = None,
                 solicitud_controller: Optional[Any] = None):
        self.conexion = conexion
        self.notif = notification_controller
        self.aud = auditoria_controller
        self.solicitud_controller = solicitud_controller
        
        self._win: Optional[QMainWindow] = None
        self._ui: Optional[Ui_CierreForm] = None
        self._dashboard = None
        self._dia_actual: Optional[str] = None
    
    def obtener_resumen_dia(self, dashboard, dia: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene boletas del día desde BD"""
        resumen: Dict[str, Any] = {}
        try:
            # ✅ ROLLBACK
            try:
                self.conexion.rollback()
            except:
                pass
            
            if dia is None:
                dow = QDate.currentDate().dayOfWeek()
                dias_map = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes"}
                dia = dias_map.get(dow, "Viernes")
            
            resumen["dia"] = dia
            
            cur = self.conexion.cursor()
            
            # ✅ CORREGIDO: Buscar boletas estado='Listo' Y cerrado=FALSE
            print(f"[INFO] Buscando boletas para cierre: dia={dia}, estado='Listo', cerrado=FALSE")
            
            cur.execute("""
            SELECT numero_boleta, extension, nombre_usuario, paginas, fecha_procesado
            FROM boletas
            WHERE dia = %s 
            AND estado = 'Listo'
            AND cerrado = FALSE
            ORDER BY fecha_procesado ASC
            """, (dia,))
            
            boletas_list = []
            extensiones_unicas = set()
            total_paginas = 0
            
            for row in cur.fetchall():
                boletas_list.append({
                    "boleta": row[0],
                    "ext": row[1],
                    "nombre": row[2],
                    "paginas": row[3],
                    "fecha_procesado": row[4]
                })
                if row[1]:
                    extensiones_unicas.add(row[1])
                total_paginas += int(row[3] or 0)
            
            cur.close()
            
            resumen["boletas_list"] = boletas_list
            resumen["total_boletas"] = len(boletas_list)
            resumen["usuarios_unicos"] = len(extensiones_unicas)
            resumen["total_paginas"] = total_paginas
            resumen["total_documentos"] = len(boletas_list)
            resumen["operador_nombre"] = getattr(dashboard, "nombre_completo", "")
            resumen["numero_fotocopiadora"] = getattr(dashboard, "usuario", "")
            resumen["observaciones"] = ""
            
            print(f"[✓] Resumen día {dia}: {len(boletas_list)} boletas LISTAS (cerrado=FALSE), {len(extensiones_unicas)} usuarios únicos")
            return resumen
            
        except Exception as e:
            print(f"[ERROR] obtener_resumen_dia: {e}")
            import traceback
            traceback.print_exc()
            return resumen
    
    def generate_cierre_text(self, resumen: Dict[str, Any]) -> str:
        """Genera texto legible para dashboard"""
        dia = resumen.get("dia", "N/A")
        fecha = QDate.currentDate().toString("dd/MM/yyyy")
        operador = resumen.get("operador_nombre", "Desconocido")
        total_boletas = resumen.get("total_boletas", 0)
        usuarios_unicos = resumen.get("usuarios_unicos", 0)
        total_paginas = resumen.get("total_paginas", 0)
        
        lines = []
        lines.append(f"╔═══════════════════════════════════════════╗")
        lines.append(f"║   BOLETA DE CIERRE - {dia.upper():^20} ║")
        lines.append(f"╚═══════════════════════════════════════════╝")
        lines.append("")
        lines.append(f"📅 Fecha: {fecha}")
        lines.append(f"👤 Operador: {operador}")
        lines.append("")
        lines.append("📊 RESUMEN DEL DÍA:")
        lines.append(f"   • Boletas procesadas: {total_boletas}")
        lines.append(f"   • Usuarios únicos atendidos: {usuarios_unicos}")
        lines.append(f"   • Total páginas: {total_paginas}")
        lines.append("")
        
        # Listar boletas ordenadas
        if resumen.get("boletas_list"):
            lines.append("📋 DETALLE DE BOLETAS (orden de llegada):")
            for i, b in enumerate(resumen.get("boletas_list", []), 1):
                lines.append(f"   {i}. {b.get('boleta')} - {b.get('nombre')} (Ext: {b.get('ext')}) - {b.get('paginas')} pág.")
        
        lines.append("")
        lines.append("─" * 47)
        lines.append("Estado: Listo para cierre")
        lines.append("(Presione 'Enviar cierre actual' para finalizar)")
        
        return "\n".join(lines)
    
    def abrir_cierre_form(self, dashboard, dia: Optional[str] = None):
        """Abre formulario de cierre con datos del día"""
        if Ui_CierreForm is None:
            QMessageBox.critical(None, "Error", "Ui_CierreForm no disponible")
            return
        
        try:
            self._dashboard = dashboard
            
            if dia is None:
                dow = QDate.currentDate().dayOfWeek()
                dias_map = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes"}
                dia = dias_map.get(dow, "Viernes")
            
            self._dia_actual = dia
            
            window = QMainWindow()
            window.setWindowTitle(f"Boleta de Cierre - {dia}")
            content = QWidget()
            ui = Ui_CierreForm()
            ui.setupUi(content)
            content.setLayout(ui.main_layout)
            window.setCentralWidget(content)
            window.resize(900, 700)
            window.setFixedSize(1000, 700)  
            window.setWindowModality(Qt.WindowModality.ApplicationModal)
            
            self._win = window
            self._ui = ui
            
            # Conectar botones
            ui.btn_guardar.clicked.connect(lambda: self.guardar_cierre())
            ui.btn_cancelar.clicked.connect(lambda: self._close_window())
            ui.btn_enviar.clicked.connect(lambda: self.enviar_cierre(destinatario_tipo="encargado"))
            
            # Habilitar según rol
            rol = getattr(dashboard, "rol", "") or ""
            if rol.lower() in ("operador", "admin", "encargado"):
                ui.btn_enviar.setEnabled(True)
            else:
                ui.btn_enviar.setEnabled(False)
            
            # Llenar con resumen
            resumen = self.obtener_resumen_dia(dashboard, dia)
            self._populate_ui_from_resumen(resumen)
            
            # Actualizar texto en dashboard
            texto = self.generate_cierre_text(resumen)
            if hasattr(dashboard, "actualizar_texto_boleta_cierre"):
                dashboard.actualizar_texto_boleta_cierre(texto)
            
            window.show()
            
            # Habilitar botón enviar solo para día actual
            dow = QDate.currentDate().dayOfWeek()
            dias_map = {1:"Lunes",2:"Martes",3:"Miércoles",4:"Jueves",5:"Viernes"}
            dia_sistema = dias_map.get(dow, "Viernes")
            
            if dia == dia_sistema:
                ui.btn_enviar.setEnabled(True)
            else:
                ui.btn_enviar.setEnabled(False)
                ui.btn_enviar.setToolTip("Solo se puede enviar el cierre del día actual")
                
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo abrir cierre:\n{e}")
    
    def _populate_ui_from_resumen(self, resumen: Dict[str, Any]):
        """Llena UI del formulario"""
        if not self._ui:
            return
        
        ui = self._ui
        try:
            ui.txt_nombre_operador.setText(resumen.get("operador_nombre", ""))
            ui.spn_num_fotocopiadora.setValue(int(resumen.get("numero_fotocopiadora") or 0))
            ui.spn_trabajos_solicitados.setValue(resumen.get("total_boletas", 0))
            ui.spn_total_color.setValue(0)
            ui.spn_total_bn.setValue(resumen.get("total_paginas", 0))
            ui.spn_cant_documentos.setValue(resumen.get("total_documentos", 0))
            ui.txt_observaciones.setPlainText(resumen.get("observaciones", ""))
        except Exception as e:
            print(f"[WARN] _populate_ui_from_resumen: {e}")
    
    def guardar_cierre(self) -> bool:
        """Guarda boleta de cierre en BD"""
        if not self._ui:
            QMessageBox.warning(None, "Guardar", "Formulario no inicializado")
            return False
        
        ui = self._ui
        data = {
            "fecha": ui.txt_fecha.text() if hasattr(ui, "txt_fecha") else QDate.currentDate().toString("yyyy-MM-dd"),
            "operador": ui.txt_nombre_operador.text() if hasattr(ui, "txt_nombre_operador") else "",
            "trabajos_solicitados": ui.spn_trabajos_solicitados.value() if hasattr(ui, "spn_trabajos_solicitados") else 0,
            "observaciones": ui.txt_observaciones.toPlainText() if hasattr(ui, "txt_observaciones") else ""
        }
        
        saved_ok = False
        if self.conexion:
            try:
                import json
                cur = self.conexion.cursor()
                cur.execute("""
                    INSERT INTO cierres (fecha, operador, trabajos_solicitados, observaciones, meta)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    data["fecha"],
                    data["operador"],
                    data["trabajos_solicitados"],
                    data["observaciones"],
                    json.dumps(data)
                ))
                cierre_id = cur.fetchone()[0]
                self.conexion.commit()
                cur.close()
                saved_ok = True
                print(f"[✓] Cierre guardado con ID {cierre_id}")
            except Exception as e:
                print(f"[ERROR] guardar_cierre: {e}")
                try:
                    self.conexion.rollback()
                except:
                    pass
                saved_ok = False
        
        if saved_ok:
            QMessageBox.information(None, "Guardado", "Boleta de cierre guardada")
        else:
            QMessageBox.warning(None, "Error", "No se pudo guardar")
        
        return saved_ok
    
    def enviar_cierre(self, destinatario_tipo: str = "encargado"):
        if not self._ui:
            return
        
        # Validar día actual
        dow = QDate.currentDate().dayOfWeek()
        dias_map = {1:"Lunes",2:"Martes",3:"Miércoles",4:"Jueves",5:"Viernes"}
        dia_sistema = dias_map.get(dow, "Viernes")
        
        if self._dia_actual != dia_sistema:
            QMessageBox.warning(None, "Día incorrecto",
                f"Solo cierre del día actual ({dia_sistema})")
            return
        
        if not self.guardar_cierre():
            return
        
        # Marcar como cerradas
        try:
            cur = self.conexion.cursor()
            cur.execute("""
                UPDATE boletas
                SET cerrado = TRUE
                WHERE dia = %s AND estado = 'Listo'
            """, (self._dia_actual,))
            self.conexion.commit()
            cur.close()
            print(f"[✓] Boletas del día {self._dia_actual} marcadas como cerradas")
        except Exception as e:
            print(f"[ERROR] enviar_cierre: {e}")
        
        # Notificar
        if self.notif:
            try:
                mensaje = f"Cierre diario {self._dia_actual} enviado"
                self.notif.notificar(destinatario_tipo, mensaje, {"dia": self._dia_actual})
            except:
                pass
        
        # Auditoría
        if self.aud:
            self.aud.registrar(
                getattr(self._dashboard, "usuario", "-"),
                "enviar_cierre",
                f"Cierre {self._dia_actual} enviado"
            )
        
        QMessageBox.information(None, "Enviado", f"Cierre enviado a {destinatario_tipo}")
        self._close_window()

        # Guardar en tabla calendar_archive
        try:
            cur = self.conexion.cursor()
            cur.execute("""
                INSERT INTO calendar_archive (fecha, boleta_id, datos)
                SELECT CURRENT_DATE, id, 
                    jsonb_build_object(
                        'numero_boleta', numero_boleta,
                        'extension', extension,
                        'nombre_usuario', nombre_usuario,
                        'paginas', total_copias,
                        'dia', dia,
                        'operador', operador_responsable
                    )
                FROM boletas
                WHERE dia = %s AND estado = 'Listo' AND cerrado = FALSE
            """, (self._dia_actual,))
            self.conexion.commit()
            cur.close()
        except Exception as e:
            print(f"[ERROR] guardar calendar_archive: {e}")
            
    def marcar_dia_listo(self, archivar: bool = True, motivo: str = ""):
        """Marca día listo y abre formulario"""
        try:
            if not self._dashboard or not self._dia_actual:
                return False
            
            # Validar día actual
            dow = QDate.currentDate().dayOfWeek()
            dias_map = {1:"Lunes",2:"Martes",3:"Miércoles",4:"Jueves",5:"Viernes"}
            dia_sistema = dias_map.get(dow, "Viernes")
            
            if self._dia_actual != dia_sistema:
                QMessageBox.warning(None, "Día incorrecto",
                    f"Solo se puede cerrar el día actual ({dia_sistema})")
                return False
            
            # Abrir formulario de cierre
            self.abrir_cierre_form(self._dashboard, self._dia_actual)
            return True
            
        except Exception as e:
            print(f"[ERROR] marcar_dia_listo: {e}")
            return False
    
    def _close_window(self):
        try:
            if self._win:
                self._win.close()
            self._win = None
            self._ui = None
        except:
            pass