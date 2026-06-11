from enum import Enum


class SocialPostType(str, Enum):
    QUESTION = "question"
    EXPERIENCE = "experience"
    PROBLEM = "problem"
    GUIDE = "guide"
    GENERAL = "general"


class SocialPostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    HIDDEN = "hidden"
    DELETED = "deleted"
    REJECTED = "rejected"


class SocialPostVisibility(str, Enum):
    PUBLIC = "public"
    MEMBERS = "members"


class SocialCommentStatus(str, Enum):
    PUBLISHED = "published"
    HIDDEN = "hidden"
    DELETED = "deleted"
    REJECTED = "rejected"


class SocialReactionType(str, Enum):
    LIKE = "like"
    HELPFUL = "helpful"
    THANKS = "thanks"


class SocialReportTargetType(str, Enum):
    POST = "post"
    COMMENT = "comment"


class SocialReportReason(str, Enum):
    SPAM = "spam"
    ABUSE = "abuse"
    MISINFORMATION = "misinformation"
    ADVERTISEMENT = "advertisement"
    INAPPROPRIATE = "inappropriate"
    OTHER = "other"


class SocialReportStatus(str, Enum):
    OPEN = "open"
    REVIEWED = "reviewed"
    DISMISSED = "dismissed"
    ACTION_TAKEN = "action_taken"


class SocialModerationTargetType(str, Enum):
    POST = "post"
    COMMENT = "comment"


class SocialModerationActionType(str, Enum):
    HIDE = "hide"
    UNHIDE = "unhide"
    DELETE = "delete"
    REJECT = "reject"
    RESTORE = "restore"
