from typing import Annotated

from fastapi import Depends

from infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork

from application.use_cases.users.get_user_by_id import UserGetterUseCase

from api.mappers.users.getter import UserGetterSchemaMapper

from api.dependencies.base import get_unit_of_work


def get_user_getter_use_case(
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> UserGetterUseCase:
    return UserGetterUseCase(uow=uow)


def get_user_getter_schema_mapper():
    return UserGetterSchemaMapper()