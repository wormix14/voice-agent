from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import os

load_dotenv(".env.local")

engine = create_engine(
    url=os.getenv("DATABASE_URL"),
    connect_args={"connect_timeout": 5},
    pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False)

