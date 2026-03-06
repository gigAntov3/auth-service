from application.dtos.auth import (
    DeviceInfoDTO,
    LogoutRequestDTO,
)


class LogoutSchemaMapper:
    def to_dto(self, refresh_token: str, device_info: DeviceInfoDTO) -> LogoutRequestDTO:
        return LogoutRequestDTO(
            refresh_token=refresh_token,
            ip_address=device_info.ip_address,
            user_agent=device_info.user_agent,
            device_name=device_info.device_name,
            device_type=device_info.device_type
        )