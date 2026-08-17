"""
Pydantic Data Models for MS MARCO-XI Multilingual Dataset

Defines structured schema for MS MARCO translation dataset records supporting 14 Indic target languages
(as, bn, gu, hi, kn, ml, mr, ne, or, pa, sa, ta, te, ur) and original English source content.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


LANGUAGE_NAME_MAP: Dict[str, str] = {
    "as": "Assamese",
    "bn": "Bengali",
    "gu": "Gujarati",
    "hi": "Hindi",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "ne": "Nepali",
    "or": "Odia",
    "pa": "Punjabi",
    "sa": "Sanskrit",
    "ta": "Tamil",
    "te": "Telugu",
    "ur": "Urdu",
    "en": "English",
}


class TranslationMeta(BaseModel):
    """Translation metadata provided in MS MARCO-XI dataset."""
    model_name: Optional[str] = Field(default="", description="Name of translation model used")
    temperature: Optional[float] = Field(default=0.0, description="Model sampling temperature")
    max_tokens: Optional[int] = Field(default=512, description="Maximum token limit for translation")
    top_p: Optional[float] = Field(default=1.0, description="Top-p nucleus sampling probability")
    frequency_penalty: Optional[float] = Field(default=0.0, description="Frequency penalty value")
    presence_penalty: Optional[float] = Field(default=0.0, description="Presence penalty value")


class PassageData(BaseModel):
    """Passage container containing English, target translated passages, and relevance selection flags."""
    English_passages: List[str] = Field(default_factory=list, description="Original English passages")
    Translated_passages: List[str] = Field(default_factory=list, description="Translated target language passages")
    is_selected: List[int] = Field(default_factory=list, description="Binary ground truth flags (1=relevant, 0=not relevant)")

    def get_selected_passages(self) -> List[str]:
        """Returns only the translated passages flagged as relevant (is_selected == 1)."""
        return [
            passage for passage, selected in zip(self.Translated_passages, self.is_selected)
            if selected == 1
        ]

    def get_selected_english_passages(self) -> List[str]:
        """Returns only the original English passages flagged as relevant (is_selected == 1)."""
        return [
            passage for passage, selected in zip(self.English_passages, self.is_selected)
            if selected == 1
        ]


class MSMarcoExample(BaseModel):
    """Complete dataset example record matching AI4Bharat/MSMARCO-XI schema."""
    query_id: int = Field(..., description="Unique query identification number")
    query_type: Optional[str] = Field(default="description", description="Query category type")
    source_lang: Optional[str] = Field(default="en", description="Source language code")
    target_lang: Optional[str] = Field(default="hi", description="Target language code")
    language_name: Optional[str] = Field(default=None, description="Human-readable language name")
    query: str = Field(..., description="Translated query in target language")
    Answer: str = Field(default="", description="Translated answer in target language")
    Eng_Query: Optional[str] = Field(default="", description="Original English query")
    Eng_Answer: Optional[str] = Field(default="", description="Original English answer")
    meta: Optional[TranslationMeta] = Field(default_factory=TranslationMeta, description="Translation metadata")
    passages: PassageData = Field(default_factory=PassageData, description="Associated passages and ground truth relevance")

    def model_post_init(self, __context):
        """Populate language_name if not explicitly set."""
        if not self.language_name and self.target_lang:
            self.language_name = LANGUAGE_NAME_MAP.get(self.target_lang.lower(), self.target_lang)
