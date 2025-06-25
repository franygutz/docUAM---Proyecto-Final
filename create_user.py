from app import app, db
from models import User

EMAIL_A_CREAR = "admin@docuam.com"
CONTRASENA_A_CREAR = "12345"

with app.app_context():
    usuario_existente = User.query.filter_by(email=EMAIL_A_CREAR).first()
    
    if usuario_existente:
        print(f"Error: El usuario con el email '{EMAIL_A_CREAR}' ya existe.")
    else:
        nuevo_usuario = User(email=EMAIL_A_CREAR)
        nuevo_usuario.set_password(CONTRASENA_A_CREAR)
        db.session.add(nuevo_usuario)
        db.session.commit()
        print(f"¡Éxito! Se ha creado el usuario '{EMAIL_A_CREAR}'.")
        print("Ya puedes usar estas credenciales para iniciar sesión.")