from enum import Enum


class ExpertAnswerStatus(str, Enum):
    PUBLISHED = "published"
    HIDDEN = "hidden"
    DELETED = "deleted"
    REJECTED = "rejected"
