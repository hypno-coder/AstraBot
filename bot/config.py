from pydantic import BaseModel, SecretStr


class FSM(BaseModel):
    data_bucket: str
    states_bucket: str

    class Config:
        extras = 'allow'


class RedisConfig(BaseModel):
    host: str = "redis"
    port: int = 6379
    db: int = 0


class BotConfig(BaseModel):
    token: SecretStr
    owner_id: int | None = None
    fsm: FSM

    class Config:
        extras = 'allow'
