"""Redis checkpointer initialization with MemorySaver fallback."""

from __future__ import annotations

import structlog

logger = structlog.get_logger()


async def create_checkpointer(redis_url: str):
    """Create an AsyncRedisSaver checkpointer, falling back to MemorySaver."""
    try:
        from langgraph.checkpoint.redis.aio import AsyncRedisSaver

        saver = AsyncRedisSaver.from_conn_string(redis_url)
        # Newer versions return an async context manager
        if hasattr(saver, '__aenter__'):
            checkpointer = await saver.__aenter__()
        else:
            checkpointer = saver
            if hasattr(checkpointer, 'asetup'):
                await checkpointer.asetup()
        return checkpointer
    except Exception as e:
        logger.warning("Redis checkpointer failed, using MemorySaver", error=str(e))
        from langgraph.checkpoint.memory import MemorySaver

        return MemorySaver()
