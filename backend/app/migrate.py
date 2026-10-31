from app.main import Base, engine

Base.metadata.create_all(engine)
print("migrations done")
