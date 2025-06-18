uvicorn main:app --reload

### Criando migrations

alembic revision --autogenerate -m "initial migration"

### Executando migrations

alembic upgrade head
