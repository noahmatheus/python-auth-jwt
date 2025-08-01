from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import datetime, timedelta

# Chave secreta para assinar o JWT (pode ser UUID)
SECRET_KEY = "c0d395de-bd3c-45f9-92b3-7d3233f2d1c0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# Simulação de banco de dados
fake_user_db = {
    "user@example.com": {
        "email": "user@example.com",
        "password": "admin"  # Em um app real, isso seria um hash
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Rota para login
@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    user_db = fake_user_db.get(user.email)

    if not user_db or user.senha != user_db["password"]:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = criar_token_jwt({"sub": user.email}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}

# Dependência para verificar token
def verificar_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Rota protegida
@app.get("/protegido")
async def rota_protegida(email: str = Depends(verificar_token)):
    return {"mensagem": f"Acesso liberado para {email}"}

# rota de salvar

# rota de editar

# rota de delete
