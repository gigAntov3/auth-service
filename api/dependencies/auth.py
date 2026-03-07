from typing import Annotated

from fastapi import Depends

from api.dependencies.base import (
    get_unit_of_work,
    get_email_service,
    get_sms_service,
)
from api.dependencies.security import (
    get_token_service,
    get_password_hasher,
)

from infrastructure.security.jwt_service import JWTTokenService
from infrastructure.security.password_hasher import BcryptPasswordHasher
from infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork
from infrastructure.services.email_service import MockEmailService
from infrastructure.services.sms_service import MockSMSService

from application.use_cases.auth.register_user import RegisterUserUseCase
from application.use_cases.auth.login_user import LoginUserUseCase
from application.use_cases.auth.logout_user import LogoutUserUseCase
from application.use_cases.auth.refresh_user import RefreshUserUseCase
from application.use_cases.auth.verification import VerificationUseCase
from application.use_cases.auth.verify import VerifyUseCase

from api.mappers.auth.register import RegisterSchemaMapper
from api.mappers.auth.login import LoginSchemaMapper
from api.mappers.auth.logout import LogoutSchemaMapper
from api.mappers.auth.refresh import RefreshSchemaMapper
from api.mappers.auth.verification import VerificationSchemaMapper
from api.mappers.auth.verify import VerifySchemaMapper



class AuthMappersDependencies:
    @staticmethod
    def register() -> RegisterSchemaMapper:
        return RegisterSchemaMapper()
    
    @staticmethod
    def login() -> LoginSchemaMapper:
        return LoginSchemaMapper()
    
    @staticmethod
    def refresh() -> RefreshSchemaMapper:
        return RefreshSchemaMapper()
    
    @staticmethod
    def logout() -> LogoutSchemaMapper:
        return LogoutSchemaMapper()
    
    @staticmethod
    def verification() -> VerificationSchemaMapper:
        return VerificationSchemaMapper()
    
    @staticmethod
    def verify() -> VerifySchemaMapper:
        return VerifySchemaMapper()


class AuthUseCaseDependencies:
    @staticmethod
    def login(
        uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)],
        password_hasher: Annotated[BcryptPasswordHasher, Depends(get_password_hasher)],
        token_service: Annotated[JWTTokenService, Depends(get_token_service)],
    ) -> LoginUserUseCase:
        return LoginUserUseCase(
            uow=uow,
            password_hasher=password_hasher,
            token_service=token_service,
        )
    
    @staticmethod
    def register(
        uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)],
        password_hasher: Annotated[BcryptPasswordHasher, Depends(get_password_hasher)],
        token_service: Annotated[JWTTokenService, Depends(get_token_service)],
    ) -> RegisterUserUseCase:
        return RegisterUserUseCase(
            uow=uow,
            password_hasher=password_hasher,
            token_service=token_service,
        )
    
    @staticmethod
    def refresh(
        uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)],
        token_service: Annotated[JWTTokenService, Depends(get_token_service)],
    ) -> RefreshUserUseCase:
        return RefreshUserUseCase(
            uow=uow,
            token_service=token_service,
        )
    
    @staticmethod
    def logout(
        uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)],
        token_service: Annotated[JWTTokenService, Depends(get_token_service)],
    ) -> LogoutUserUseCase:
        return LogoutUserUseCase(
            uow=uow,
            token_service=token_service,
        )
    
    @staticmethod
    def verification(
        uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)],
        email_service: Annotated[MockEmailService, Depends(get_email_service)],
        sms_service: Annotated[MockSMSService, Depends(get_sms_service)],

    ) -> VerificationUseCase:
        return VerificationUseCase(
            uow=uow,
            email_service=email_service,
            sms_service=sms_service,
        )
    
    @staticmethod
    def verify(
        uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)],
        token_service: Annotated[JWTTokenService, Depends(get_token_service)],
    ) -> VerifyUseCase:
        return VerifyUseCase(
            uow=uow,
            token_service=token_service,
        )