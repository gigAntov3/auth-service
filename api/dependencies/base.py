from infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork

from infrastructure.services.email_service import MockEmailService
from infrastructure.services.sms_service import MockSMSService

from infrastructure.database.session import db_manager


def get_email_service():
    return MockEmailService()

def get_sms_service():
    return MockSMSService()

def get_unit_of_work():
    return SQLAlchemyUnitOfWork(db_manager.session_factory)