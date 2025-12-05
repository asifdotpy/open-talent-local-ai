"""
Redis-based message bus for inter-agent communication.
Implements pub/sub pattern for event-driven agent collaboration.
"""

import json
import asyncio
import logging
from typing import Callable, Optional, List, Dict, Any
from datetime import datetime
import redis.asyncio as redis
from .models import AgentMessage, MessageType, MessagePriority

logger = logging.getLogger(__name__)


class MessageBus:
    """Redis pub/sub message bus for agent communication"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.subscriptions: Dict[str, List[Callable]] = {}
        self.is_running = False
        
    async def connect(self):
        """Establish Redis connection"""
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info(f"Connected to Redis at {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        self.is_running = False
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Disconnected from Redis")
    
    async def publish(
        self,
        topic: str,
        message: AgentMessage
    ) -> None:
        """
        Publish message to topic
        
        Args:
            topic: Topic/channel name
            message: AgentMessage to publish
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            message_json = message.model_dump_json()
            await self.redis_client.publish(topic, message_json)
            logger.debug(f"Published to {topic}: {message.message_type}")
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            raise
    
    async def publish_event(
        self,
        topic: str,
        source_agent: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        target_agent: Optional[str] = None,
        priority: MessagePriority = MessagePriority.MEDIUM,
        correlation_id: Optional[str] = None
    ) -> None:
        """
        Convenience method to publish an event
        
        Args:
            topic: Topic/channel name
            source_agent: Name of the agent sending the message
            message_type: Type of message
            payload: Message payload data
            target_agent: Optional target agent (None = broadcast)
            priority: Message priority
            correlation_id: Optional correlation ID for tracking
        """
        message = AgentMessage(
            source_agent=source_agent,
            target_agent=target_agent,
            message_type=message_type,
            payload=payload,
            priority=priority,
            correlation_id=correlation_id
        )
        await self.publish(topic, message)
    
    async def subscribe(
        self,
        topics: List[str],
        callback: Callable[[AgentMessage], Any]
    ) -> None:
        """
        Subscribe to topics and register callback
        
        Args:
            topics: List of topic names to subscribe to
            callback: Async function to call with received messages
        """
        if not self.redis_client:
            await self.connect()
        
        # Store callback for each topic
        for topic in topics:
            if topic not in self.subscriptions:
                self.subscriptions[topic] = []
            self.subscriptions[topic].append(callback)
        
        # Create pubsub if not exists
        if not self.pubsub:
            self.pubsub = self.redis_client.pubsub()
        
        # Subscribe to topics
        await self.pubsub.subscribe(*topics)
        logger.info(f"Subscribed to topics: {topics}")
    
    async def listen(self) -> None:
        """
        Start listening for messages
        Should be run as background task
        """
        if not self.pubsub:
            logger.error("No subscriptions found. Call subscribe() first.")
            return
        
        self.is_running = True
        logger.info("Starting message listener...")
        
        try:
            async for message in self.pubsub.listen():
                if not self.is_running:
                    break
                
                if message["type"] == "message":
                    await self._handle_message(message)
        except asyncio.CancelledError:
            logger.info("Message listener cancelled")
        except Exception as e:
            logger.error(f"Error in message listener: {e}")
            raise
    
    async def _handle_message(self, raw_message: Dict) -> None:
        """
        Handle received message
        
        Args:
            raw_message: Raw Redis message
        """
        try:
            channel = raw_message["channel"]
            data = raw_message["data"]
            
            # Parse message
            message = AgentMessage.model_validate_json(data)
            
            # Call registered callbacks for this channel
            if channel in self.subscriptions:
                for callback in self.subscriptions[channel]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(message)
                        else:
                            callback(message)
                    except Exception as e:
                        logger.error(f"Error in callback for {channel}: {e}")
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def get_message_count(self, topic: str) -> int:
        """Get number of subscribers to a topic"""
        if not self.redis_client:
            await self.connect()
        
        channels = await self.redis_client.pubsub_numsub(topic)
        return channels[topic] if channels else 0
    
    async def store_message(
        self,
        key: str,
        message: AgentMessage,
        ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Store message in Redis for later retrieval
        
        Args:
            key: Redis key
            message: Message to store
            ttl_seconds: Optional TTL in seconds
        """
        if not self.redis_client:
            await self.connect()
        
        message_json = message.model_dump_json()
        await self.redis_client.set(key, message_json)
        
        if ttl_seconds:
            await self.redis_client.expire(key, ttl_seconds)
    
    async def get_message(self, key: str) -> Optional[AgentMessage]:
        """
        Retrieve stored message from Redis
        
        Args:
            key: Redis key
            
        Returns:
            AgentMessage or None if not found
        """
        if not self.redis_client:
            await self.connect()
        
        data = await self.redis_client.get(key)
        if data:
            return AgentMessage.model_validate_json(data)
        return None
    
    async def list_active_topics(self) -> List[str]:
        """List all active pub/sub topics"""
        if not self.redis_client:
            await self.connect()
        
        channels = await self.redis_client.pubsub_channels()
        return channels


# Predefined topic names for consistency
class Topics:
    """Standard topic names for agent communication"""
    CANDIDATE_EVENTS = "agents:candidates"
    PIPELINE_EVENTS = "agents:pipeline"
    ENGAGEMENT_EVENTS = "agents:engagement"
    INTERVIEW_EVENTS = "agents:interviews"
    MARKET_INTEL = "agents:market_intel"
    ERRORS = "agents:errors"
    SYSTEM = "agents:system"
