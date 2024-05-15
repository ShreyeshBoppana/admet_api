from pydantic import BaseModel


class SearchRequest(BaseModel):
    smile: str
