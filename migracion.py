from app import db, app

with app.app_context():
    #db.drop_all()  # Esto eliminará todas las tablas
    db.create_all()  # Esto creará las tablas de nuevo con la nueva estructura
    print("Migración completada.")
