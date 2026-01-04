from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "FastAPI App")
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"

    MYSQL_USER: str = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB: str = os.getenv("MYSQL_DB")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:"
            f"{self.MYSQL_PASSWORD}@"
            f"{self.MYSQL_HOST}:"
            f"{self.MYSQL_PORT}/"
            f"{self.MYSQL_DB}"
        )

settings = Settings()
