from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import datetime, timedelta

from bdconfig import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Usuario
from passlib.context import CryptContext


## bd config
from models import Base, Usuario   # importa o mesmo Base
from bdconfig import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# aqui cria as tabelas
Base.metadata.create_all(bind=engine)
## bd config

# Contexto para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Dependency para obter sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# Configuração DB ========== ========== ==========

# Chave secreta para assinar o JWT (pode ser UUID)
SECRET_KEY = "c0d395de-bd3c-45f9-92b3-7d3233f2d1c0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Modelo para criação
class UsuarioCreate(BaseModel):
    email: str
    senha: str

# Modelo para visualização (sem senha)
class UsuarioOut(BaseModel):
    id_usuario: int
    email: str
    data_criacao: datetime

    class Config:
        orm_mode = True

# Modelos Pydantic
class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    email: str
    senha: str

# Função para criar JWT
def criar_token_jwt(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=15))
    to_encode.update({
        "exp": expire,
        "iat": now,       # <-- aqui adicionamos a data de criação
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Rota para login atualizada
def verificar_senha(senha_plain: str, senha_hash: str):
    return pwd_context.verify(senha_plain, senha_hash)

# Rota para login
@app.post("/login")
def login(user: UsuarioCreate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == user.email).first()
    if not usuario or not verificar_senha(user.senha, usuario.password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = criar_token_jwt({"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer"}

# Dependência para verificar token
def verificar_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        iat = payload.get("iat")  # timestamp de criação do token
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return {"email": email, "iat": iat}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Rota protegida
@app.get("/protegido")
async def rota_protegida(email: str = Depends(verificar_token)):
    return {"mensagem": f"Acesso liberado para {email}"}

# Rota de listar
@app.get("/usuarios", response_model=list[UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db), usuario: Usuario = Depends(verificar_token)):
    usuarios = db.query(Usuario).all()
    return usuarios

# Rota de salvar
@app.post("/usuarios")
def criar_usuario(usuario_in: UsuarioCreate, db: Session = Depends(get_db), usuario: Usuario = Depends(verificar_token)):
    # Verifica se já existe
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario_in.email).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    # Hash da senha
    hashed_password = pwd_context.hash(usuario_in.senha)

    novo_usuario = Usuario(
        email=usuario_in.email,
        password=hashed_password
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return {"id": novo_usuario.id_usuario, "email": novo_usuario.email}

# rota de editar
@app.put("/usuarios/{id_usuario}", response_model=UsuarioOut)
def atualizar_usuario(id_usuario: int, usuario_in: UsuarioCreate, db: Session = Depends(get_db), usuario: Usuario = Depends(verificar_token)):
    db_usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Atualiza dados do usuario
    db_usuario.email = usuario_in.email
    db_usuario.password = pwd_context.hash(usuario_in.senha)
    
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario

# rota de delete
@app.delete("/usuarios/{id_usuario}")
def deletar_usuario(id_usuario: int, db: Session = Depends(get_db), usuario: Usuario = Depends(verificar_token)):
    db_usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db.delete(db_usuario)
    db.commit()

    return {"mensagem": f"Usuário {id_usuario} deletado com sucesso"}