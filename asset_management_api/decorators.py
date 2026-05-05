import logging
from functools import wraps

logger = logging.getLogger(__name__)


def log_user_activity(action_name):
    """
    Logs user activity for DRF ViewSet methods
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):

            user = request.user if request.user.is_authenticated else None

            # 🔹 BEFORE execution
            logger.info(
                f"[START] Action={action_name} | "
                f"User={user.username if user else 'Anonymous'} | "
                f"Method={request.method} | Path={request.path}"
            )

            try:
                response = view_func(self, request, *args, **kwargs)

                # 🔹 AFTER execution
                logger.info(
                    f"[SUCCESS] Action={action_name} | "
                    f"Status={response.status_code}"
                )

                return response

            except Exception as e:
                # 🔹 ERROR logging
                logger.error(
                    f"[ERROR] Action={action_name} | "
                    f"User={user.username if user else 'Anonymous'} | "
                    f"Error={str(e)}"
                )
                raise  # VERY IMPORTANT → don't swallow exception

        return wrapper

    return decorator