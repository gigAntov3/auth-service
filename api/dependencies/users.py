from typing import Annotated

from fastapi import Depends

from infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork

from application.use_cases.users.get_user_by_id import UserGetterUseCase
from application.use_cases.users.update_user import UpdateUserUseCase

from api.mappers.users.getter import UserGetterSchemaMapper
from api.mappers.users.update import UserUpdateSchemaMapper

from api.dependencies.base import get_unit_of_work


class UsersMappersDependencies:
    @staticmethod
    def getter() -> UserGetterSchemaMapper:
        return UserGetterSchemaMapper()
    
    @staticmethod
    def update() -> UserUpdateSchemaMapper:
        return UserUpdateSchemaMapper()
    

class UsersUseCaseDependencies:
    @staticmethod
    def getter(
        uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)],
    ) -> UserGetterUseCase:
        return UserGetterUseCase(uow=uow)
    
    @staticmethod
    def update(
        uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)],
    ) -> UpdateUserUseCase:
        return UpdateUserUseCase(uow=uow)