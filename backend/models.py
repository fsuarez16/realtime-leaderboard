from pydantic import BaseModel

class User(BaseModel):
    username: str
    password: str

class ScoreSubmission(BaseModel):
    game: str
    score: float