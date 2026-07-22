from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import redis

from orderflow_common.models import QueueMessage


class OrderQueue:
    def __init__(
        self,
        redis_url: str,
        stream: str = "orders",
        group: str = "order-workers",
        dlq_stream: str = "orders-dlq",
    ) -> None:
        self.client = redis.Redis.from_url(redis_url, decode_responses=True)
        self.stream = stream
        self.group = group
        self.dlq_stream = dlq_stream

    def ensure_group(self) -> None:
        try:
            self.client.xgroup_create(self.stream, self.group, id="0", mkstream=True)
        except redis.ResponseError as exc:
            if "BUSYGROUP" not in str(exc):
                raise

    def health(self) -> str:
        try:
            return "ok" if self.client.ping() else "error"
        except Exception:
            return "error"

    def enqueue(self, message: QueueMessage) -> str:
        payload = message.model_dump(mode="json")
        return str(
            self.client.xadd(
                self.stream,
                {"payload": json.dumps(payload)},
            )
        )

    def read_group(self, consumer: str, count: int = 1, block_ms: int = 2000) -> list[tuple[str, QueueMessage]]:
        results = self.client.xreadgroup(
            self.group,
            consumer,
            {self.stream: ">"},
            count=count,
            block=block_ms,
        )
        messages: list[tuple[str, QueueMessage]] = []
        if not results:
            return messages
        for _stream, entries in results:
            for msg_id, fields in entries:
                raw = fields.get("payload", "{}")
                messages.append((msg_id, QueueMessage.model_validate(json.loads(raw))))
        return messages

    def ack(self, message_id: str) -> None:
        self.client.xack(self.stream, self.group, message_id)

    def dead_letter(self, message: QueueMessage, reason: str) -> None:
        payload = message.model_dump(mode="json")
        payload["dead_letter_reason"] = reason
        self.client.xadd(self.dlq_stream, {"payload": json.dumps(payload)})

    def stream_length(self) -> int:
        return int(self.client.xlen(self.stream))

    def pending_count(self) -> int:
        try:
            pending = self.client.xpending(self.stream, self.group)
            return int(pending.get("pending", 0)) if isinstance(pending, dict) else int(pending[0])
        except Exception:
            return 0

    def oldest_age_seconds(self) -> float:
        entries = self.client.xrange(self.stream, min="-", max="+", count=1)
        if not entries:
            return 0.0
        _msg_id, fields = entries[0]
        raw = fields.get("payload")
        if not raw:
            return 0.0
        data: dict[str, Any] = json.loads(raw)
        enqueued = datetime.fromisoformat(data["enqueued_at"].replace("Z", "+00:00"))
        return max(0.0, (datetime.now(timezone.utc) - enqueued).total_seconds())
