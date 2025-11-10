from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from database import create_db_and_tables, get_session
from models import User, TransactionType, Transaction
from auth import get_password_hash, authenticate_user, create_access_token, get_current_user
from datetime import timedelta

app = FastAPI(title="Controle de Gastos API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Criação do banco ao iniciar o app
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# ----------------------------
#  ROTAS DE USUÁRIOS / LOGIN
# ----------------------------
@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: User, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    hashed_password = get_password_hash(user.password)
    user.password = hashed_password
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "Usuário registrado com sucesso"}


@app.post("/login")
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_session)
):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ----------------------------
#  ROTAS DE TRANSAÇÕES
# ----------------------------
@app.post("/transaction_types/", status_code=201)
def create_transaction_type(
        transaction_type: TransactionType,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user)
):
    session.add(transaction_type)
    session.commit()
    session.refresh(transaction_type)
    return transaction_type


@app.post("/transactions/", status_code=201)
def create_transaction(
        transaction: Transaction,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user)
):
    transaction.user_id = user.id
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


@app.get("/transactions/")
def list_transactions(
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user)
):
    transactions = session.exec(select(Transaction).where(Transaction.user_id == user.id)).all()
    return transactions
