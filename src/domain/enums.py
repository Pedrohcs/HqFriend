"""Enumerações do domínio."""
from enum import Enum


class SeriesStatus(str, Enum):
    UNREAD = "UNREAD"
    IN_PROGRESS = "IN_PROGRESS"
    READ = "READ"
