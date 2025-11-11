from database import crear_conexion
import hashlib

def encriptar_clave(clave):
    return hashlib.sha256(clave.encode()).hexdigest()

def obtener_usuarios():
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, usuario, clave, rol FROM usuarios")
        usuarios = cursor.fetchall()
        conexion.close()
        return usuarios
    return []

def obtener_usuario_por_id(usuario_id):
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre, usuario, clave, rol FROM usuarios WHERE id = ?", (usuario_id,))
        usuario = cursor.fetchone()
        conexion.close()
        return usuario
    return None

def registrar_usuario(nombre, usuario, clave, rol):
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ?", (usuario,))
        if cursor.fetchone()[0] > 0:
            return False
        clave_encriptada = encriptar_clave(clave)
        cursor.execute("INSERT INTO usuarios (nombre, usuario, clave, rol) VALUES (?, ?, ?, ?)",
                       (nombre, usuario, clave_encriptada, rol))
        conexion.commit()
        conexion.close()
        return True
    return False

def actualizar_usuario(usuario_id, nombre, usuario, clave, rol):
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ? AND id != ?", (usuario, usuario_id))
        if cursor.fetchone()[0] > 0:
            return False
        if clave:
            clave_encriptada = encriptar_clave(clave)
            cursor.execute("UPDATE usuarios SET nombre=?, usuario=?, clave=?, rol=? WHERE id=?",
                           (nombre, usuario, clave_encriptada, rol, usuario_id))
        else:
            cursor.execute("UPDATE usuarios SET nombre=?, usuario=?, rol=? WHERE id=?",
                           (nombre, usuario, rol, usuario_id))
        conexion.commit()
        conexion.close()
        return True
    return False

def eliminar_usuario_por_id(usuario_id):
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id=?", (usuario_id,))
        conexion.commit()
        conexion.close()
        return True
    return False