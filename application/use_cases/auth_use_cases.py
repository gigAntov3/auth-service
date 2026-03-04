from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from domain.entities.user import UserEntity
from domain.entities.role import RoleType
from domain.services.authorization import AuthorizationService
from domain.value_objects.password import RawPassword
from domain.value_objects.email import Email

from application.interfaces.unit_of_work import UnitOfWork
from application.interfaces.password_hasher import PasswordHasher
from application.interfaces.token_service import TokenService
from application.interfaces.email_sender import EmailSender
from application.interfaces.cache_service import CacheService

from application.dtos.auth_dto import (
    RegisterRequestDTO, RegisterResponseDTO,
    LoginRequestDTO, LoginResponseDTO,
    TokenDTO,
    VerifyEmailRequestDTO, VerifyEmailResponseDTO,
    ForgotPasswordRequestDTO, ForgotPasswordResponseDTO,
    ResetPasswordRequestDTO, ResetPasswordResponseDTO,
    ChangePasswordRequestDTO, ChangePasswordResponseDTO,
    RefreshTokenRequestDTO, RefreshTokenResponseDTO
)

from application.exceptions import (
    AuthenticationError, InvalidCredentialsError,
    UserNotFoundError, UserAlreadyExistsError,
    InvalidTokenError, TokenExpiredError,
    EmailNotVerifiedError, UserNotActiveError,
    ValidationError
)


class RegisterUseCase:
    """Use case: Регистрация нового пользователя"""
    
    def __init__(
        self,
        uow: UnitOfWork,
        password_hasher: PasswordHasher,
        token_service: TokenService,
        email_sender: EmailSender,
        cache: CacheService
    ):
        self.uow = uow
        self.password_hasher = password_hasher
        self.token_service = token_service
        self.email_sender = email_sender
        self.cache = cache
    
    async def execute(self, request: RegisterRequestDTO) -> RegisterResponseDTO:
        # Проверяем, не занят ли email
        async with self.uow:
            existing_user = await self.uow.users.get_by_email(request.email)
            if existing_user:
                raise UserAlreadyExistsError("Пользователь с таким email уже существует")
        
        # Валидируем пароль через доменный Value Object
        try:
            RawPassword(request.password)
        except ValueError as e:
            raise ValidationError(str(e))
        
        # Хешируем пароль
        password_hash = self.password_hasher.hash(request.password)
        
        # Создаем пользователя через доменную фабрику
        user = UserEntity.create(
            email=request.email,
            full_name=request.full_name,
            password_hash=password_hash
        )
        
        # Сохраняем пользователя
        async with self.uow:
            await self.uow.users.save(user)
            
            # Сохраняем роли (базовую роль USER)
            for role in user.roles:
                await self.uow.roles.add(role)
            
            await self.uow.commit()
        
        # Создаем токен для подтверждения email
        verification_token = self.token_service.create_email_verification_token(
            user_id=user.id,
            email=request.email
        )
        
        # Отправляем email с подтверждением
        await self.email_sender.send_verification_email(
            to_email=request.email,
            full_name=request.full_name,
            verification_token=verification_token
        )
        
        # Кэшируем пользователя
        await self.cache.set_user(user)
        
        return RegisterResponseDTO(
            user_id=user.id,
            email=user.email.value,
            full_name=user.full_name,
            message="Регистрация успешна. Проверьте email для подтверждения.",
            requires_verification=True
        )


class LoginUseCase:
    """Use case: Вход пользователя"""
    
    def __init__(
        self,
        uow: UnitOfWork,
        password_hasher: PasswordHasher,
        token_service: TokenService,
        cache: CacheService
    ):
        self.uow = uow
        self.password_hasher = password_hasher
        self.token_service = token_service
        self.cache = cache
    
    async def execute(self, request: LoginRequestDTO) -> LoginResponseDTO:
        # Ищем пользователя
        async with self.uow:
            user = await self.uow.users.get_by_email(request.email)
            
            if not user:
                raise InvalidCredentialsError("Неверный email или пароль")
            
            # Проверяем пароль
            if not self.password_hasher.verify(request.password, user.password_hash.value):
                raise InvalidCredentialsError("Неверный email или пароль")
            
            # Проверяем активен ли пользователь
            try:
                user.ensure_active()
            except UserNotActiveError as e:
                raise UserNotActiveError(str(e))
            
            # Загружаем все роли пользователя
            roles = await self.uow.roles.get_by_user(user.id)
            
            # Обновляем время последнего входа
            user.update_last_login()
            await self.uow.users.update(user)
            await self.uow.commit()
        
        # Создаем токены
        access_token, expires_in = self.token_service.create_access_token(
            user_id=user.id,
            roles=[r.role_type.value for r in roles],
            permissions=user.get_all_permissions()
        )
        
        refresh_token, refresh_expires_in = self.token_service.create_refresh_token(
            user_id=user.id
        )
        
        # Сохраняем refresh token в кэше
        await self.cache.set_refresh_token(
            user_id=user.id,
            token=refresh_token,
            ttl=refresh_expires_in
        )
        
        # Обновляем кэш пользователя
        await self.cache.set_user(user)
        
        return LoginResponseDTO(
            user_id=user.id,
            email=user.email.value,
            full_name=user.full_name,
            tokens=TokenDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
                refresh_expires_in=refresh_expires_in
            ),
            permissions=user.get_all_permissions()
        )


class VerifyEmailUseCase:
    """Use case: Подтверждение email"""
    
    def __init__(
        self,
        uow: UnitOfWork,
        token_service: TokenService,
        cache: CacheService
    ):
        self.uow = uow
        self.token_service = token_service
        self.cache = cache
    
    async def execute(self, request: VerifyEmailRequestDTO) -> VerifyEmailResponseDTO:
        # Проверяем токен
        payload = self.token_service.verify_email_token(request.token)
        if not payload:
            raise InvalidTokenError("Неверный или истекший токен")
        
        user_id = UUID(payload['user_id'])
        email = payload['email']
        
        async with self.uow:
            user = await self.uow.users.get_by_id(user_id)
            if not user:
                raise UserNotFoundError("Пользователь не найден")
            
            if user.email.value != email:
                raise InvalidTokenError("Токен не соответствует пользователю")
            
            # Подтверждаем email через доменный метод
            user.verify_email()
            await self.uow.users.update(user)
            await self.uow.commit()
        
        # Обновляем кэш
        await self.cache.set_user(user)
        
        return VerifyEmailResponseDTO(
            message="Email успешно подтвержден",
            email=email
        )


class ForgotPasswordUseCase:
    """Use case: Запрос на сброс пароля"""
    
    def __init__(
        self,
        uow: UnitOfWork,
        token_service: TokenService,
        email_sender: EmailSender,
        cache: CacheService
    ):
        self.uow = uow
        self.token_service = token_service
        self.email_sender = email_sender
        self.cache = cache
    
    async def execute(self, request: ForgotPasswordRequestDTO) -> ForgotPasswordResponseDTO:
        # Всегда возвращаем одинаковый ответ для безопасности
        async with self.uow:
            user = await self.uow.users.get_by_email(request.email)
            
            if user and user.is_active:
                # Создаем токен для сброса пароля
                reset_token = self.token_service.create_password_reset_token(
                    user_id=user.id,
                    email=request.email
                )
                
                # Сохраняем токен в кэше
                await self.cache.set_password_reset_token(
                    user_id=user.id,
                    token=reset_token,
                    ttl=3600  # 1 час
                )
                
                # Отправляем email
                await self.email_sender.send_password_reset_email(
                    to_email=request.email,
                    full_name=user.full_name,
                    reset_token=reset_token
                )
        
        return ForgotPasswordResponseDTO()


class ResetPasswordUseCase:
    """Use case: Сброс пароля"""
    
    def __init__(
        self,
        uow: UnitOfWork,
        password_hasher: PasswordHasher,
        token_service: TokenService,
        cache: CacheService
    ):
        self.uow = uow
        self.password_hasher = password_hasher
        self.token_service = token_service
        self.cache = cache
    
    async def execute(self, request: ResetPasswordRequestDTO) -> ResetPasswordResponseDTO:
        # Проверяем токен
        payload = self.token_service.verify_password_reset_token(request.token)
        if not payload:
            raise InvalidTokenError("Неверный или истекший токен")
        
        user_id = UUID(payload['user_id'])
        email = payload['email']
        
        # Проверяем токен в кэше
        cached_token = await self.cache.get_password_reset_token(user_id)
        if cached_token != request.token:
            raise InvalidTokenError("Неверный или истекший токен")
        
        # Валидируем новый пароль
        try:
            RawPassword(request.new_password)
        except ValueError as e:
            raise ValidationError(str(e))
        
        async with self.uow:
            user = await self.uow.users.get_by_id(user_id)
            if not user or user.email.value != email:
                raise UserNotFoundError("Пользователь не найден")
            
            if not user.is_active:
                raise UserNotActiveError("Пользователь деактивирован")
            
            # Хешируем новый пароль
            new_password_hash = self.password_hasher.hash(request.new_password)
            
            # Обновляем пароль
            user.password_hash = new_password_hash
            user.updated_at = datetime.now(timezone.utc)
            
            await self.uow.users.update(user)
            await self.uow.commit()
        
        # Удаляем использованный токен из кэша
        await self.cache.delete_password_reset_token(user_id)
        
        # Инвалидируем refresh token
        await self.cache.delete_refresh_token(user_id)
        
        return ResetPasswordResponseDTO()


class RefreshTokenUseCase:
    """Use case: Обновление access token"""
    
    def __init__(
        self,
        uow: UnitOfWork,
        token_service: TokenService,
        cache: CacheService
    ):
        self.uow = uow
        self.token_service = token_service
        self.cache = cache
    
    async def execute(self, request: RefreshTokenRequestDTO) -> RefreshTokenResponseDTO:
        # Проверяем refresh token
        payload = self.token_service.verify_refresh_token(request.refresh_token)
        if not payload:
            raise InvalidTokenError("Неверный refresh token")
        
        user_id = UUID(payload['sub'])
        
        # Проверяем token в кэше
        cached_token = await self.cache.get_refresh_token(user_id)
        if cached_token != request.refresh_token:
            raise InvalidTokenError("Неверный refresh token")
        
        async with self.uow:
            user = await self.uow.users.get_by_id(user_id)
            if not user or not user.is_active:
                raise UserNotFoundError("Пользователь не найден или деактивирован")
            
            # Получаем роли
            roles = await self.uow.roles.get_by_user(user_id)
        
        # Создаем новый access token
        access_token, expires_in = self.token_service.create_access_token(
            user_id=user_id,
            roles=[r.role_type.value for r in roles],
            permissions=user.get_all_permissions()
        )
        
        return RefreshTokenResponseDTO(
            access_token=access_token,
            expires_in=expires_in
        )


class ChangePasswordUseCase:
    """Use case: Изменение пароля"""
    
    def __init__(
        self,
        uow: UnitOfWork,
        password_hasher: PasswordHasher,
        cache: CacheService
    ):
        self.uow = uow
        self.password_hasher = password_hasher
        self.cache = cache
    
    async def execute(self, user_id: UUID, 
                      request: ChangePasswordRequestDTO) -> ChangePasswordResponseDTO:
        async with self.uow:
            user = await self.uow.users.get_by_id(user_id)
            if not user:
                raise UserNotFoundError("Пользователь не найден")
            
            # Проверяем текущий пароль
            if not self.password_hasher.verify(request.current_password, 
                                               user.password_hash.value):
                raise InvalidCredentialsError("Неверный текущий пароль")
            
            # Валидируем новый пароль
            try:
                RawPassword(request.new_password)
            except ValueError as e:
                raise ValidationError(str(e))
            
            # Хешируем новый пароль
            new_password_hash = self.password_hasher.hash(request.new_password)
            
            # Обновляем пароль
            user.password_hash = new_password_hash
            user.updated_at = datetime.now(timezone.utc)
            
            await self.uow.users.update(user)
            await self.uow.commit()
        
        # Инвалидируем refresh token
        await self.cache.delete_refresh_token(user_id)
        
        return ChangePasswordResponseDTO()


class LogoutUseCase:
    """Use case: Выход из системы"""
    
    def __init__(self, cache: CacheService):
        self.cache = cache
    
    async def execute(self, user_id: UUID) -> None:
        # Удаляем refresh token
        await self.cache.delete_refresh_token(user_id)