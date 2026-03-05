from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
import time
import asyncio
from collections import defaultdict

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware для ограничения частоты запросов"""
    
    def __init__(
        self,
        app,
        calls: int = 100,
        period: int = 60,
        whitelist: list = None
    ):
        super().__init__(app)
        self.calls = calls  # Максимальное количество запросов
        self.period = period  # Период в секундах
        self.whitelist = whitelist or []
        
        # Хранилище: {ip: [(timestamp, count)]}
        self.requests: Dict[str, list] = defaultdict(list)
        self._cleanup_task = None
    
    async def dispatch(self, request: Request, call_next):
        # Проверяем, нужно ли ограничивать
        if self._should_rate_limit(request):
            client_ip = self._get_client_ip(request)
            
            # Очищаем старые записи
            self._cleanup_old_requests(client_ip)
            
            # Проверяем лимит
            if len(self.requests[client_ip]) >= self.calls:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later."
                )
            
            # Добавляем новый запрос
            self.requests[client_ip].append(time.time())
        
        # Обработка запроса
        response = await call_next(request)
        return response
    
    def _should_rate_limit(self, request: Request) -> bool:
        """Проверка, нужно ли применять rate limiting"""
        # Не ограничиваем whitelist
        if request.client.host in self.whitelist:
            return False
        
        # Ограничиваем только определенные эндпоинты
        sensitive_paths = ["/auth/login", "/auth/register", "/auth/refresh"]
        return any(request.url.path.startswith(p) for p in sensitive_paths)
    
    def _get_client_ip(self, request: Request) -> str:
        """Получение IP клиента"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0]
        return request.client.host
    
    def _cleanup_old_requests(self, client_ip: str):
        """Очистка старых запросов"""
        now = time.time()
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip]
            if now - ts < self.period
        ]