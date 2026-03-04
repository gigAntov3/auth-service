from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
from typing import Callable
import json

logger = logging.getLogger("api")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов и ответов"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        # Логируем запрос
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Получаем тело запроса для логирования (только в debug)
        body = None
        if logger.isEnabledFor(logging.DEBUG):
            try:
                body = await request.json()
                logger.debug(f"Request body: {json.dumps(body, ensure_ascii=False)}")
            except:
                pass
        
        # Обрабатываем запрос
        try:
            response = await call_next(request)
            
            # Логируем ответ
            process_time = time.time() - start_time
            logger.info(
                f"Response: {response.status_code} - {process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            # Логируем ошибку
            process_time = time.time() - start_time
            logger.error(
                f"Error: {str(e)} - {process_time:.3f}s",
                exc_info=True
            )
            raise


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware для сбора метрик"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Здесь можно собирать метрики для Prometheus
        # Например, увеличивать счетчики запросов по эндпоинтам
        
        response = await call_next(request)
        
        # Здесь можно записывать время ответа и статус
        return response