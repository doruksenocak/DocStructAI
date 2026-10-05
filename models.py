from pydantic import BaseModel


class Education(BaseModel):
    institution: str
    degree: str
    start_date: str | None = None
    end_date: str | None = None


class Experience(BaseModel):
    company: str
    position: str
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None


class CVData(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    education: list[Education]
    experience: list[Experience]
    skills: list[str]
