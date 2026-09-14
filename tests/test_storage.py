"""Transaction smoke tests with SQLite; PostgreSQL TRUNCATE is adapted to DELETE."""
from pathlib import Path
import pandas as pd
import pytest
from sqlalchemy import create_engine, event, text
from connection.DataStorage import DataStorage


@pytest.fixture
def store(tmp_path):
    engine = create_engine('sqlite://')
    @event.listens_for(engine, 'connect')
    def attach(dbapi_connection, _):
        dbapi_connection.execute('ATTACH DATABASE ? AS public', (str(tmp_path / 'catalog.db'),))
    @event.listens_for(engine, 'before_cursor_execute', retval=True)
    def truncate(_, __, statement, parameters, ___, ____):
        return statement.replace('TRUNCATE TABLE temp_imovel', 'DELETE FROM temp_imovel'), parameters
    schema = (Path(__file__).parents[1] / 'sql/init.sql').read_text().replace('SERIAL', 'INTEGER')
    with engine.begin() as conn:
        for statement in schema.split(';'):
            if statement.strip():
                # Create all tables in the attached public schema.
                statement = statement.replace('CREATE TABLE IF NOT EXISTS ', 'CREATE TABLE IF NOT EXISTS public.')
                conn.execute(text(statement))
    store = DataStorage()
    store.engine = engine
    store.connection = engine.connect()
    yield store
    engine.dispose()


def row(price=500000):
    return pd.DataFrame([{'preco': price, 'area': 90, 'quartos': 2, 'vagas': 1, 'banheiros': 2,
        'bairro': "Jardim d'Oeste", 'Status': 'Compra', 'Imobiliaria': 'Teste', 'tipo': 'Apartamento',
        'link': 'https://example.com/imovel/1', 'cidade': 'São Paulo', 'uf': 'SP'}])


def test_load_promotes_and_updates_without_duplicates(store):
    store.save_data(row())
    store.connection = store.engine.connect()
    store.save_data(row(600000))
    with store.engine.connect() as conn:
        rows = conn.execute(text('SELECT preco, cidade FROM imovel')).all()
        assert rows == [(600000, 'São Paulo')]
        assert conn.execute(text('SELECT bairrodesc FROM bairro')).scalar() == "Jardim d'Oeste"


def test_failed_promotion_rolls_back_staging_and_lookups(store):
    store.save_data(row())
    @event.listens_for(store.engine, 'before_cursor_execute')
    def fail(_, __, statement, ___, ____, _____):
        if 'INSERT INTO imovel' in statement:
            raise RuntimeError('Injected failure')
    store.connection = store.engine.connect()
    with pytest.raises(RuntimeError, match='Injected failure'):
        store.save_data(row(900000))
    with store.engine.connect() as conn:
        assert conn.execute(text('SELECT preco FROM imovel')).scalar() == 500000
        assert conn.execute(text('SELECT preco FROM temp_imovel')).scalar() == 500000


def test_empty_extraction_does_not_touch_database(store):
    with pytest.raises(ValueError, match='Extração vazia'):
        store.save_data(pd.DataFrame())
