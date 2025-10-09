from models.usuarios import Usuarios as UsuariosModel
from schemas.usuarios import Usuarios

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
    
    def update_usuarios(self, id: int, data: Usuarios):
        usuario = self.db.query(UsuariosModel).filter(UsuariosModel.id == id).first()
        usuario.nombre = data.nombre
        usuario.apellido = data.apellido
        usuario.correo = data.correo
        usuario.password = data.password
        usuario.rol = data.rol
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
    

