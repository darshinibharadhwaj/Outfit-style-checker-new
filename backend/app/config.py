from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MySQL (structured data: users, preferences, outfit-check history)
    # Example production value: mysql+pymysql://user:password@localhost:3306/outfit_checker
    # Defaults to a local SQLite file so the app runs instantly with zero setup.
    database_url: str = "sqlite:///./dev.db"

    # MongoDB (flexible data: style tips library, detailed analysis logs)
    # Example production value: mongodb://localhost:27017
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "outfit_checker"

    # If true, uses an in-memory fake Mongo (mongomock) instead of a real
    # MongoDB server. Handy for first run / testing without installing Mongo.
    use_mongomock: bool = True

    cors_origins: list[str] = ["http://localhost:5173"]

    # Login tokens (JWT). The secret MUST be changed in production.
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    class Config:
        env_file = ".env"


settings = Settings()
