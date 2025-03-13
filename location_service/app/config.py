from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_TOPIC: str = "user_locations"
    API_KEY: str
    
    class Config:
        env_file = ".env"

settings = Settings() 