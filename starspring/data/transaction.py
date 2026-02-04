"""
Transaction management

Provides declarative transaction support.
"""

from typing import Callable
from functools import wraps
from starspring.data.orm_gateway import get_orm_gateway


def Transactional(func: Callable) -> Callable:
    """
    Mark a method as transactional
    
    Similar to Spring Boot's @Transactional annotation.
    Automatically commits on success and rolls back on exception.
    
    Example:
        @Service
        class UserService:
            @Transactional
            async def create_user(self, user: User):
                # Operations here are wrapped in a transaction
                return await self.user_repository.save(user)
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        gateway = get_orm_gateway()
        
        try:
            gateway.begin_transaction()
            result = await func(*args, **kwargs)
            gateway.commit()
            return result
        except Exception as e:
            gateway.rollback()
            raise e
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        gateway = get_orm_gateway()
        
        try:
            gateway.begin_transaction()
            result = func(*args, **kwargs)
            gateway.commit()
            return result
        except Exception as e:
            gateway.rollback()
            raise e
    
    # Return appropriate wrapper based on function type
    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
