from uuid import UUID

from datetime import datetime

from pydantic import BaseModel, Field

from domain.entities.verification_code import VerificationType


class VerificationRequestSchema(BaseModel):
    identifier: str = Field(..., description="Идентификатор пользователя", example="alice@example.com")
    identifier_type: VerificationType = Field(..., description="Тип верификации", example=VerificationType.EMAIL)


class VerificationRequestResponseSchema(BaseModel):
    verification_id: UUID = Field(..., description="Идентификатор верификации")
    identifier: str = Field(..., description="Идентификатор пользователя")
    identifier_type: VerificationType = Field(..., description="Тип верификации")
    expires_at: datetime = Field(..., description="Время истечения верификации")