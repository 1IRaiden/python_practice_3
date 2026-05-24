from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    age: int
    group_id: Optional[int] = None


# 2. Create - when user want to create student
class StudentCreate(StudentBase):
    pass

class StudentRead(StudentBase):
    id: int

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    pass

# deleted group (information about them can store in different store database
class GroupRead(GroupCreate):
    id: int
    created_at: datetime
    members_count: int = 0

    model_config = ConfigDict(from_attributes=True)
