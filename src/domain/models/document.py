"""
文件領域模型

ABP 對比：
- ABP: public class Document : AggregateRoot<Guid>
- ABP 實體通常有 Id、CreationTime、LastModificationTime 等屬性
- Python: 使用 dataclass 定義，更輕量
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Document:
    """
    文件領域模型

    ABP 對比：
    public class Document : FullAuditedAggregateRoot<Guid>
    {
        public string Title { get; set; }
        public string Content { get; set; }
        public Guid OwnerId { get; set; }
    }
    """

    id: str | None
    title: str
    content: str
    owner_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
