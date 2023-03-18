from dataclasses import dataclass, field
from typing import List, Dict, Optional


class ApiResponse:
    def __init__(self, data):
        self.data = data

    def is_error(self):
        return False


class VoicesResponse(ApiResponse):
    def get_voices(self):
        return self.data.get("voices", [])


class ErrorResponse(ApiResponse):
    def __init__(self, data, status_code):
        super().__init__(data)
        self.status_code = status_code

    def is_error(self):
        return True

    def get_errors(self):
        return self.data.get("detail", [])


@dataclass
class Sample:
    sample_id: str
    file_name: str
    mime_type: str
    size_bytes: int
    hash: str


@dataclass
class FineTuning:
    model_id: Optional[str]
    is_allowed_to_fine_tune: bool
    fine_tuning_requested: bool
    finetuning_state: str
    verification_attempts: Optional[List]
    verification_failures: List[str]
    verification_attempts_count: int


@dataclass
class Voice:
    voice_id: str
    name: str
    samples: Optional[List[Sample]]
    category: str
    fine_tuning: FineTuning
    labels: Dict
    preview_url: str
    available_for_tiers: List[str]
    settings: Optional[Dict]


@dataclass
class VoicesResponse(ApiResponse):
    voices: List[Voice] = field(default_factory=list)

    def get_voices(self):
        return self.voices
