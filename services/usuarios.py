from models.usuarios import Usuarios as UsuariosModel
from schemas.usuarios import Usuarios, UsuarioUpdate
from utils.security import get_password_hash


class UsuariosService():
    
    def __init__(self, db) -> None:
        self.db = db

    def get_usuarios(self):
        result = self.db.query(UsuariosModel).filter(UsuariosModel.activo == True).all()
        return result

    def get_usuario_id(self, id):
        result = self.db.query(UsuariosModel).filter(UsuariosModel.id == id).first()
        return result
    
    def create_usuarios(self, Usuario: Usuarios):
        new_usuario = UsuariosModel(**Usuario.model_dump(exclude={"id"}))
        self.db.add(new_usuario)
        self.db.commit()
        return
    
    def update_usuarios(self, id: int, data: UsuarioUpdate):
        usuario = self.db.query(UsuariosModel).filter(UsuariosModel.id == id).first()
        if data.nombre is not None:
            usuario.nombre = data.nombre
        if data.apellido is not None:
            usuario.apellido = data.apellido
        if data.correo is not None:
            usuario.correo = data.correo
        if data.rol is not None:
            usuario.rol = data.rol
        if hasattr(data, 'password') and data.password.strip() != "":
            usuario.password = get_password_hash(data.password)
        self.db.commit()
        return
    

    def delete_usuarios(self, id: int):
       usuario = self.db.query(UsuariosModel).filter(UsuariosModel.id == id).first()
       usuario.activo = False
       self.db.commit()
       return
    
    def otorgar_permiso_usuario(self, id: int, data: Usuarios):
        usuario = self.db.query(UsuariosModel).filter(UsuariosModel.id == id).first()
        usuario.permiso = data.permiso
        self.db.commit()
        return
    