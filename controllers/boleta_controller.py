# -*- coding: utf-8 -*-
"""
controllers/boleta_controller.py
VERSIÓN CORREGIDA - Guarda cambios del operador correctamente
"""

from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Qt
from datetime import datetime
import traceback
import json

try:
    from db.boletas import insertar as crear_boleta
except Exception:
    crear_boleta = None


class BoletaController:
    def __init__(self, ui, conexion, usuario: dict, auditoria_ctrl=None, 
                 solicitudes_ctrl=None, modo="form", parent_window=None, boleta_id=None):
        self.ui = ui
        self.conexion = conexion
        self.usuario = usuario or {}
        self.auditoria_ctrl = auditoria_ctrl
        self.solicitudes_ctrl = solicitudes_ctrl
        self.parent_window = parent_window
        self.modo = modo
        self.boleta_id = boleta_id
        
        self.rol = (self.usuario.get("rol") or "usuario").lower().strip()
        
        self._configurar_permisos_por_rol()
        self._conectar_botones()
        
        if boleta_id and modo in ("view", "edit"):
            self._cargar_boleta(boleta_id)
    
    def _configurar_permisos_por_rol(self):
        """Configura qué puede editar cada rol"""
        try:
            solo_lectura = self.modo == "view"
            
            if self.rol == "usuario":
                self.ui.group_datos_solicitante.setEnabled(not solo_lectura and self.modo == "form")
                self.ui.group_seleccionar_servicio.setEnabled(not solo_lectura and self.modo == "form")
                self.ui.group_empaste.setEnabled(False)
                self.ui.group_operador.setEnabled(False)
                self.ui.group_uso_exclusivo.setEnabled(False)
                self.ui.btn_enviar.setVisible(not solo_lectura and self.modo == "form")
                self.ui.btn_guardar.setVisible(False)
                
            elif self.rol == "encargado":
                if self.modo == "view":
                    self.ui.group_datos_solicitante.setEnabled(False)
                    self.ui.group_seleccionar_servicio.setEnabled(False)
                    self.ui.group_empaste.setEnabled(False)
                    self.ui.group_operador.setEnabled(False)
                    self.ui.group_uso_exclusivo.setEnabled(False)
                    self.ui.btn_enviar.setVisible(False)
                    self.ui.btn_guardar.setVisible(False)
                elif self.modo == "form":
                    self.ui.group_datos_solicitante.setEnabled(True)
                    self.ui.group_seleccionar_servicio.setEnabled(True)
                    self.ui.group_empaste.setEnabled(False)
                    self.ui.group_operador.setEnabled(False)
                    self.ui.group_uso_exclusivo.setEnabled(False)
                    self.ui.btn_enviar.setVisible(True)
                    self.ui.btn_guardar.setVisible(False)
                else:
                    self.ui.group_datos_solicitante.setEnabled(False)
                    self.ui.group_seleccionar_servicio.setEnabled(False)
                    self.ui.group_empaste.setEnabled(False)
                    self.ui.group_operador.setEnabled(False)
                    self.ui.group_uso_exclusivo.setEnabled(False)
                    self.ui.btn_enviar.setVisible(False)
                    self.ui.btn_guardar.setVisible(False) 

            elif self.rol == "operador":
                self.ui.group_datos_solicitante.setEnabled(False)
                self.ui.group_seleccionar_servicio.setEnabled(False)
                self.ui.group_empaste.setEnabled(not solo_lectura)
                self.ui.group_operador.setEnabled(not solo_lectura)
                self.ui.group_uso_exclusivo.setEnabled(False)
                self.ui.btn_enviar.setVisible(False)
                self.ui.btn_guardar.setVisible(not solo_lectura)
                
            elif self.rol == "admin":
                self.ui.group_datos_solicitante.setEnabled(not solo_lectura)
                self.ui.group_seleccionar_servicio.setEnabled(not solo_lectura)
                self.ui.group_empaste.setEnabled(not solo_lectura)
                self.ui.group_operador.setEnabled(not solo_lectura)
                self.ui.group_uso_exclusivo.setEnabled(not solo_lectura)
                self.ui.btn_enviar.setVisible(True)
                self.ui.btn_guardar.setVisible(True)
        except Exception as e:
            print(f"[ERROR] _configurar_permisos_por_rol: {e}")
    
    def _conectar_botones(self):
        """Conecta eventos de botones"""
        try:
            if hasattr(self.ui, "btn_enviar"):
                try: 
                    self.ui.btn_enviar.clicked.disconnect()
                except RuntimeError:
                    pass
                self.ui.btn_enviar.clicked.connect(self.enviar_boleta)
            
            if hasattr(self.ui, "btn_guardar"):
                try: 
                    self.ui.btn_guardar.clicked.disconnect()
                except RuntimeError:
                    pass
                self.ui.btn_guardar.clicked.connect(self.guardar_cambios_operador)
            
            if hasattr(self.ui, "btn_cancelar"):
                try: 
                    self.ui.btn_cancelar.clicked.disconnect()
                except RuntimeError:
                    pass
                self.ui.btn_cancelar.clicked.connect(self._on_cancelar)
        except Exception as e:
            print(f"[ERROR] _conectar_botones: {e}")
    
    def _cargar_boleta(self, boleta_id):
        """Carga boleta existente"""
        try:
            try:
                self.conexion.rollback()
            except:
                pass
            
            from psycopg2.extras import RealDictCursor
            cur = self.conexion.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT b.*, u.nombre_completo
                FROM boletas b
                LEFT JOIN usuarios u ON u.extension = b.extension
                WHERE b.id=%s
            """, (boleta_id,))
            row = cur.fetchone()
            cur.close()
            
            if not row:
                QMessageBox.warning(None, "Error", "Boleta no encontrada")
                return
            
            # Área
            if hasattr(self.ui, 'input_area'):
                meta = row.get('meta')
                if isinstance(meta, str):
                    meta = json.loads(meta)
                elif not isinstance(meta, dict):
                    meta = {}
                
                area = meta.get('area', '')
                self.ui.input_area.setText(area)
                self.ui.input_area.setReadOnly(True)
            
            # Nombre usuario
            if hasattr(self.ui, 'input_nombre_usuario'):
                nombre = row.get('nombre_completo') or row.get('nombre_usuario') or ''
                self.ui.input_nombre_usuario.setText(nombre)
                self.ui.input_nombre_usuario.setReadOnly(True)

            # Nombre operador según rol
            if hasattr(self.ui, 'input_nombre_operador'):
                nombre_op = self.usuario.get('nombre_completo', '')
                self.ui.input_nombre_operador.setText(nombre_op)
                if self.modo == "edit" and self.rol in ("operador", "admin"):
                    self.ui.input_nombre_operador.setReadOnly(True)
                else:
                    if self.rol in ("operador", "admin"):
                        nombre_op = self.usuario.get('nombre_completo', '')
                        self.ui.input_nombre_operador.setText(nombre_op)
                        self.ui.input_nombre_operador.setReadOnly(True)
                    else:
                        nombre_op = row.get('operador_responsable') or ''
                        self.ui.input_nombre_operador.setText(nombre_op)
                        self.ui.input_nombre_operador.setReadOnly(True)
            
            # Nombre documento
            if hasattr(self.ui, 'input_nombre_documento'):
                meta = row.get('meta')
                if isinstance(meta, str):
                    meta = json.loads(meta)
                elif not isinstance(meta, dict):
                    meta = {}
                self.ui.input_nombre_documento.setText(meta.get('nombre_documento', ''))
                self.ui.input_nombre_documento.setReadOnly(True)
            
            # Copias
            if hasattr(self.ui, 'spin_copias_color'):
                self.ui.spin_copias_color.setValue(int(row.get('copias_color') or 0))
            if hasattr(self.ui, 'spin_copias_bn'):
                self.ui.spin_copias_bn.setValue(int(row.get('copias_bn') or 0))
            if hasattr(self.ui, 'spin_total_copias'):
                self.ui.spin_total_copias.setValue(int(row.get('total_copias') or 0))
            if hasattr(self.ui, 'spin_cantidad_documentos'):
                self.ui.spin_cantidad_documentos.setValue(int(row.get('cantidad_documentos') or 0))
            
            # Servicios principales
            servicios = row.get('servicios')
            if isinstance(servicios, str):
                servicios = json.loads(servicios)
            elif not isinstance(servicios, dict):
                servicios = {}
            
            if hasattr(self.ui, 'chk_fotocopiado'):
                self.ui.chk_fotocopiado.setChecked(servicios.get('fotocopiado', False))
            if hasattr(self.ui, 'chk_impresion_llave'):
                self.ui.chk_impresion_llave.setChecked(servicios.get('impresion_llave', False))
            if hasattr(self.ui, 'chk_impresion_email'):
                self.ui.chk_impresion_email.setChecked(servicios.get('impresion_email', False))
            
            # Servicios de empaste
            if hasattr(self.ui, 'chk_empaste_grapa'):
                self.ui.chk_empaste_grapa.setChecked(servicios.get('empaste_grapa', False))
            if hasattr(self.ui, 'chk_empaste_resorte'):
                self.ui.chk_empaste_resorte.setChecked(servicios.get('empaste_resorte', False))
            if hasattr(self.ui, 'chk_empaste_cuadernillo'):
                self.ui.chk_empaste_cuadernillo.setChecked(servicios.get('empaste_cuadernillo', False))
            if hasattr(self.ui, 'chk_empaste_portada'):
                self.ui.chk_empaste_portada.setChecked(servicios.get('empaste_portada', False))
            if hasattr(self.ui, 'chk_empaste_engomado'):
                self.ui.chk_empaste_engomado.setChecked(servicios.get('empaste_engomado', False))
            if hasattr(self.ui, 'chk_empaste_guillotina'):
                self.ui.chk_empaste_guillotina.setChecked(servicios.get('empaste_guillotina', False))
            if hasattr(self.ui, 'chk_escaneo_email'):
                self.ui.chk_escaneo_email.setChecked(servicios.get('escaneo_email', False))
            if hasattr(self.ui, 'txt_email_escaneo'):
                meta = row.get('meta')
                if isinstance(meta, str):
                    meta = json.loads(meta)
                elif not isinstance(meta, dict):
                    meta = {}
                email = meta.get('operador', {}).get('email_escaneo', '')
                self.ui.txt_email_escaneo.setText(email)
                
            # Empaste (spinboxes operador)
            empaste = row.get('empaste')
            if isinstance(empaste, str):
                empaste = json.loads(empaste)
            elif not isinstance(empaste, dict):
                empaste = {}
            
            if hasattr(self.ui, 'spin_empaste_grapa'):
                self.ui.spin_empaste_grapa.setValue(empaste.get('grapa', 0))
            if hasattr(self.ui, 'spin_empaste_resorte'):
                self.ui.spin_empaste_resorte.setValue(empaste.get('resorte', 0))
            if hasattr(self.ui, 'spin_empaste_cuadernillo'):
                self.ui.spin_empaste_cuadernillo.setValue(empaste.get('cuadernillo', 0))
            if hasattr(self.ui, 'spin_empaste_portada_cartulina'):
                self.ui.spin_empaste_portada_cartulina.setValue(empaste.get('portada_cartulina', 0))
            if hasattr(self.ui, 'spin_empaste_engomado'):
                self.ui.spin_empaste_engomado.setValue(empaste.get('engomado', 0))
            if hasattr(self.ui, 'spin_empaste_guillotina'):
                self.ui.spin_empaste_guillotina.setValue(empaste.get('guillotina', 0))
            
            # Observaciones
            if hasattr(self.ui, 'text_observaciones_servicio'):
                self.ui.text_observaciones_servicio.setPlainText(row.get('observaciones') or '')
            
            if hasattr(self.ui, 'input_numero_fotocopiadora'):
                meta = row.get('meta')
                if isinstance(meta, str):
                    meta = json.loads(meta)
                elif not isinstance(meta, dict):
                    meta = {}
                num_foto = meta.get('operador', {}).get('numero_fotocopiadora', '')
                self.ui.input_numero_fotocopiadora.setText(str(num_foto))
            
            if hasattr(self.ui, 'spin_personas_atendidas'):
                meta = row.get('meta')
                if isinstance(meta, str):
                    meta = json.loads(meta)
                elif not isinstance(meta, dict):
                    meta = {}
                personas = meta.get('operador', {}).get('personas_atendidas', 0)
                self.ui.spin_personas_atendidas.setValue(int(personas))
            
            print(f"[✓] Boleta {boleta_id} cargada")
            
        except Exception as e:
            print(f"[ERROR] _cargar_boleta: {e}")
            traceback.print_exc()
    
    def enviar_boleta(self):
        """Envía boleta nueva (usuarios, encargados)"""
        try:
            if not hasattr(self, 'rol'):
                self.rol = (self.usuario.get("rol") or "usuario").lower().strip()
            if not hasattr(self, 'parent_window'):
                self.parent_window = None
            
            # ✅ CORREGIDO: Validar rol (incluye encargado)
            print(f"[INFO] Rol detectado: '{self.rol}'")
            
            if self.rol not in ("usuario", "admin", "encargado"):
                QMessageBox.warning(self.parent_window, "Acceso denegado",
                    f"Solo usuarios y encargados pueden enviar boletas.\n\nRol actual: {self.rol}")
                return
            
            print(f"[✓] Rol '{self.rol}' autorizado para enviar boletas")
            
            # Validar campos
            if hasattr(self.ui, '_validar_antes_enviar'):
                try:
                    if not self.ui._validar_antes_enviar():
                        return
                except Exception as e:
                    print(f"[WARN] Validación: {e}")
            
            if not self.solicitudes_ctrl:
                QMessageBox.critical(self.parent_window, "Error",
                    "SolicitudesController no disponible.")
                return
            
            data = self.ui.get_all_data()
            
            # Validaciones mínimas
            if not data.get("area", "").strip():
                QMessageBox.warning(self.parent_window, "Campo obligatorio",
                    "Debe ingresar el Área / Departamento")
                return
            
            if not data.get("nombre_usuario", "").strip():
                QMessageBox.warning(self.parent_window, "Campo obligatorio",
                    "Debe ingresar el Nombre completo")
                return
            
            servicios = data.get("servicios", {})
            if not any(servicios.values()):
                QMessageBox.warning(self.parent_window, "Servicio requerido",
                    "Debe seleccionar al menos un servicio")
                return
            
            # Generar número de boleta
            import random
            numero_boleta = f"B-{random.randint(1000, 9999)}"
            extension = self.usuario.get("extension", "")[:32]
            nombre_usuario = data.get("nombre_usuario", "Usuario")
            copias = data.get("copias", {})
            paginas = copias.get("total", 0)
            
            # Crear boleta
            new_id = self.solicitudes_ctrl.crear_solicitud(
                numero_boleta=numero_boleta,
                extension=extension,
                nombre_usuario=nombre_usuario,
                paginas=paginas,
                servicios=servicios,
                copias_color=copias.get("color", 0),
                copias_bn=copias.get("bn", 0),
                cantidad_documentos=copias.get("documentos", 0),
                empaste=data.get("empaste", {}),
                observaciones=data.get("observaciones_servicio", ""),
                dia=None,
                meta=data
            )
            
            if new_id:
                if self.auditoria_ctrl:
                    self.auditoria_ctrl.registrar(extension, "enviar_boleta",
                        f"Boleta {numero_boleta} enviada")
                
                QMessageBox.information(self.parent_window, "✓ Boleta enviada",
                    f"Boleta {numero_boleta} enviada correctamente al operador.")
                
                if self.parent_window:
                    self.parent_window.close()
            else:
                QMessageBox.critical(self.parent_window, "Error",
                    "No se pudo crear la boleta.")
        except Exception as e:
            print(f"[ERROR] enviar_boleta: {e}")
            traceback.print_exc()
            QMessageBox.critical(self.parent_window, "Error", f"Error al enviar:\n{str(e)}")
    
    def guardar_cambios_operador(self):
        try:
            if self.rol not in ("operador", "admin"):
                QMessageBox.warning(self.parent_window, "Acceso denegado", "Solo operadores.")
                return
            
            if not self.boleta_id:
                return
            
            try:
                self.conexion.rollback()
            except:
                pass
            
            data = self.ui.get_all_data()
            
            # Obtener meta existente
            cur = self.conexion.cursor()
            cur.execute("SELECT meta FROM boletas WHERE id = %s", (self.boleta_id,))
            row = cur.fetchone()
            meta = {}
            if row and row[0]:
                if isinstance(row[0], str):
                    meta = json.loads(row[0])
                elif isinstance(row[0], dict):
                    meta = row[0]
            
            # Actualizar meta
            meta['operador'] = data.get('operador', {})
            meta['servicios'] = data.get('servicios', {})
            
            cur.execute("""
                UPDATE boletas SET
                    empaste = %s::jsonb,
                    observaciones = %s,
                    operador_responsable = %s,
                    meta = %s::jsonb
                WHERE id = %s
            """, (
                json.dumps(data.get("empaste", {})),
                data.get("observaciones_servicio", ""),
                self.usuario.get('nombre_completo', ''),
                json.dumps(meta),
                self.boleta_id
            ))
            self.conexion.commit()
            cur.close()
            
            QMessageBox.information(self.parent_window, "✓ Guardado", "Cambios guardados.")
            
            if self.auditoria_ctrl:
                self.auditoria_ctrl.registrar(
                    self.usuario.get("extension", ""),
                    "guardar_boleta_operador",
                    f"Boleta {self.boleta_id} actualizada"
                )
            
            if self.parent_window:
                self.parent_window.close()
            
        except Exception as e:
            print(f"[ERROR] guardar_cambios_operador: {e}")
            traceback.print_exc()
            try:
                self.conexion.rollback()
            except:
                pass
            QMessageBox.critical(self.parent_window, "Error", f"Error:\n{e}")
    
    def _on_cancelar(self):
        """Cierra formulario con confirmación"""
        try:
            if self.parent_window:
                confirm = QMessageBox.question(
                    self.parent_window,
                    "Cancelar",
                    "¿Desea cancelar sin guardar?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if confirm == QMessageBox.Yes:
                    self.parent_window.close()
        except Exception as e:
            print(f"[ERROR] _on_cancelar: {e}")