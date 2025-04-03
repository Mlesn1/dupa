"""
Rate limiter utility for controlling API request frequency.
"""
import time
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Rate limiter utility class to restrict the frequency of requests.
    """
    
    def __init__(self, max_requests_per_minute):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests_per_minute: Maximum allowed requests per minute per user
        """
        self.max_requests = max_requests_per_minute
        self.window_seconds = 60  # 1 minute window
        
        # Store request timestamps for each user
        # user_id -> list of timestamps
        self.request_timestamps = defaultdict(list)
    
    def check_rate_limit(self, user_id) -> bool:
        """
        Check if a user has exceeded their rate limit.
        
        Args:
            user_id: The user's identifier
        
        Returns:
            True if the request is allowed, False if rate limit exceeded
        """
        current_time = time.time()
        user_timestamps = self.request_timestamps[user_id]
        
        # Clean up old timestamps outside the window
        while user_timestamps and user_timestamps[0] < current_time - self.window_seconds:
            user_timestamps.pop(0)
        
        # Check if adding this request would exceed the limit
        if len(user_timestamps) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return False
        
        # Record this request timestamp and allow it
        user_timestamps.append(current_time)
        return True
