import os, pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config as AlembicConfig

from main import app
from database import get_db, Base
from models import Organization, User, Membership, Account
from routers.auth import get_password_hash

# ---- DB wiring ----
@pytest.fixture(scope="session")
def db_url(tmp_path_factory):
    dbfile = tmp_path_factory.mktemp("db") / "test.db"
    url = f"sqlite:///{dbfile}"
    os.environ["DATABASE_URL"] = url
    return url

@pytest.fixture(scope="session")
def engine(db_url):
    return create_engine(db_url, connect_args={"check_same_thread": False})

@pytest.fixture(scope="session", autouse=True)
def apply_migrations(db_url):
    # 1) Run Alembic
    cfg = AlembicConfig("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(cfg, "head")

    # 2) Fallback for any declarative-only tables
    eng = create_engine(db_url, connect_args={"check_same_thread": False})
    insp = inspect(eng)
    existing = set(insp.get_table_names())
    missing = set(Base.metadata.tables.keys()) - existing
    if missing:
        Base.metadata.create_all(bind=eng)

    # 3) Ensure user_settings exists (some code reads it)
    if "user_settings" not in insp.get_table_names():
        with eng.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    active_org_id INTEGER
                )
            """))
    yield

@pytest.fixture()
def db_session(engine):
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def override_get_db(db_session):
    def _get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()

# ---- Seed data ----
@pytest.fixture(scope="session", autouse=True)
def seed_data(engine):
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = SessionLocal()

    # 1) Organization
    org = Organization(name="Test Org")
    db.add(org); db.flush()

    # 2) User with whichever password field your model actually uses
    pwd_field = next((f for f in ("hashed_password","password_hash","password") if hasattr(User, f)), None)
    if not pwd_field:
        raise RuntimeError("Could not find password column on User (hashed_password/password_hash/password)")
    owner = User(email="owner@example.com", **{pwd_field: get_password_hash("demo123")})
    db.add(owner); db.flush()

    # 3) Membership (detect org FK or relationship)
    membership = None
    for fk in ("organization_id","org_id","business_id","tenant_id"):
        if hasattr(Membership, fk):
            membership = Membership(user_id=owner.id, role="owner", **{fk: org.id})
            break
    if membership is None:
        for rel in ("organization","org","business","tenant"):
            if hasattr(Membership, rel):
                membership = Membership(user_id=owner.id, role="owner")
                setattr(membership, rel, org)
                break
    if membership is None:
        raise RuntimeError("Could not find org field on Membership")

    db.add(membership)

    # 4) Minimal chart
    def add_account(**kw):
        db.add(Account(**kw))
    acct_kwargs = []
    if hasattr(Account, "organization_id"): key = "organization_id"
    elif hasattr(Account, "org_id"): key = "org_id"
    elif hasattr(Account, "business_id"): key = "business_id"
    else: key = None
    for code, name, typ in [("1000","Cash","asset"), ("5000","Expenses","expense")]:
        base = { "code": code, "name": name, "type": typ }
        if key: base[key] = org.id
        add_account(**base)

    db.commit()

    # 5) Ensure user_settings row (for active org lookups)
    with engine.begin() as conn:
        conn.execute(text("INSERT OR REPLACE INTO user_settings(user_id, active_org_id) VALUES (:u, :o)"),
                     {"u": owner.id, "o": org.id})

    db.close()

@pytest.fixture
def client():
    return TestClient(app)
