from pydantic import BaseModel, SecretStr


class FSM(BaseModel):
    data_bucket: str
    states_bucket: str

    class Config:
        extras = 'allow'


class BotConfig(BaseModel):
    token: SecretStr
    owner_id: int | None = None
    fsm: FSM

    class Config:
        extras = 'allow'
