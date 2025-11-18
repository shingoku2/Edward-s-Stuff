"""
Error recovery and fallback mechanisms
"""

import logging
import traceback
from typing import Any, Callable, Optional
from functools import wraps

logger = logging.getLogger(__name__)

class ErrorRecovery:
    """Comprehensive error recovery system"""
    
    @staticmethod
    def with_fallback(primary_func: Callable, fallback_func: Callable, 
                     logger: Optional[logging.Logger] = None) -> Any:
        """Execute primary function with fallback on failure"""
        log = logger or logging.getLogger(__name__)
        
        try:
            return primary_func()
        except Exception as e:
            log.warning(f"Primary function failed: {e}, trying fallback")
            try:
                return fallback_func()
            except Exception as fallback_error:
                log.error(f"Fallback also failed: {fallback_error}")
                raise e
    
    @staticmethod
    def graceful_degrade(feature_name: str, 
                        primary_action: Callable,
                        fallback_action: Optional[Callable] = None) -> Any:
        """Execute action with graceful degradation"""
        log = logging.getLogger(f"degrade.{feature_name}")
        
        try:
            result = primary_action()
            log.debug(f"Feature '{feature_name}' executed successfully")
            return result
        except Exception as e:
            log.warning(f"Feature '{feature_name}' failed: {e}")
            
            if fallback_action:
                try:
                    result = fallback_action()
                    log.info(f"Feature '{feature_name}' degraded gracefully")
                    return result
                except Exception as fallback_error:
                    log.error(f"Fallback for '{feature_name}' failed: {fallback_error}")
                    
            # Return a safe default or re-raise
            log.error(f"Feature '{feature_name}' completely unavailable")
            raise
    
    @staticmethod
    def safe_api_call(api_func: Callable, 
                     max_retries: int = 3,
                     retry_delay: float = 1.0,
                     default_response: Optional[str] = None) -> Optional[str]:
        """Make safe API call with retry logic"""
        import time
        
        for attempt in range(max_retries):
            try:
                return api_func()
            except Exception as e:
                logger.warning(f"API call attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error(f"All API call attempts failed after {max_retries} tries")
        
        return default_response

def error_boundary(feature_name: str, 
                  fallback_return: Any = None,
                  log_errors: bool = True) -> Callable:
    """Decorator to add error boundaries around functions"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"Error in {feature_name}.{func.__name__}: {e}")
                    logger.debug(traceback.format_exc())
                
                return fallback_return
                
        return wrapper
    return decorator
