"""
Các exception dùng chung cho hệ thống TKB Planner Pro.
Giúp phân loại lỗi rõ ràng và hỗ trợ logging/handle nhất quán.
"""


class TKBError(Exception):
    """Base exception cho các lỗi liên quan đến TKB."""


class ValidationError(TKBError):
    """Lỗi validate dữ liệu đầu vào (thời gian, tiết, mã môn, v.v.)."""


class ConflictError(TKBError):
    """Lỗi xung đột lịch (trùng phòng, trùng giáo viên, trùng giờ bận...)."""


