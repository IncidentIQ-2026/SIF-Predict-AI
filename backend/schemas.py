from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class ReportCreate(BaseModel):
    report_text: str = Field(min_length=12, max_length=5000)
    report_type: str = Field(default="Near Miss", max_length=40)
    location: str = Field(default="Unspecified", max_length=120)
    department: str = Field(default="Operations", max_length=100)
    activity: str = Field(default="General Operations", max_length=120)


class AnalysisRequest(ReportCreate):
    persist: bool = False


class AnalysisResult(BaseModel):
    sif_label: str
    sif_probability: float
    risk_level: str
    life_saving_rule: str
    activity: str
    barrier_failure: str
    potential_consequence: str
    explanation: str = ""
    report_id: int | None = None


class ReportRead(AnalysisResult):
    model_config = ConfigDict(from_attributes=True)
    id: int
    report_text: str
    report_type: str
    location: str
    department: str
    status: str
    created_at: datetime


class StatusUpdate(BaseModel):
    status: str = Field(pattern="^(Pending Review|Verified SIF|Verified Non-SIF|Action Required|Closed)$")


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    report_id: int
    severity: str
    status: str
    created_at: datetime
    report: ReportRead


class AlertUpdate(BaseModel):
    status: str = Field(pattern="^(Open|Acknowledged|Closed)$")
    acknowledged_by: str | None = Field(default=None, max_length=100)


class ActionCreate(BaseModel):
    report_id: int | None = None
    description: str = Field(min_length=5, max_length=1000)
    responsible: str = Field(min_length=2, max_length=120)
    priority: str = Field(default="Medium", pattern="^(Low|Medium|High|Critical)$")
    due_date: date


class ActionRead(ActionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    completed_at: datetime | None


class ActionUpdate(BaseModel):
    status: str = Field(pattern="^(Open|In Progress|Completed|Overdue)$")
