from fastapi import Request

from user_agents import parse

from application.dtos.auth import DeviceInfoDTO

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


async def get_device_info(
    request: Request,
) -> DeviceInfoDTO:
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")

    ua = parse(user_agent)

    if ua.is_mobile:
        device_type = "mobile"
    elif ua.is_tablet:
        device_type = "tablet"
    elif ua.is_pc:
        device_type = "desktop"
    elif ua.is_bot:
        device_type = "bot"
    else:
        device_type = "unknown"

    device_name = ua.device.family or device_type.capitalize()

    return DeviceInfoDTO(
        ip_address=ip_address,
        user_agent=user_agent,
        device_name=device_name,
        device_type=device_type
    )