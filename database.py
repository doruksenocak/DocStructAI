from sqlalchemy import create_engine, String, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


DATABASE_URL = "sqlite:///./docstructai.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass


class ProcessedDocument(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    filename: Mapped[str] = mapped_column(String)

    document_type: Mapped[str] = mapped_column(String)

    data: Mapped[str] = mapped_column(Text)


Base.metadata.create_all(bind=engine)