"""
UX Evaluation Components Package

This package provides a comprehensive toolkit for conducting user experience
evaluations using AI-powered personas and structured methodologies.

Core Components:
- EvaluatorBase: Abstract base class for evaluation workflows
- NielsenEvaluator: Nielsen heuristics-based UX evaluation
- SusEvaluator: System Usability Scale (SUS) evaluation
- Persona: AI persona for simulating user behavior and feedback
- LLMClient: Interface for large language model interactions
- LLMClientFactory: Factory for creating configured LLM clients
- WhisperTranscriber: Speech-to-text for voice-based evaluations
- GooglePlayScraper: User feedback collection from app stores

Key Features:
- Multi-modal evaluation support (text, images, audio)
- Standardized evaluation methodologies (Nielsen, SUS)
- Persona-driven qualitative insights
- Quantitative scoring and analysis
- Multi-provider LLM support
- Structured data output for analysis
"""

from .active_persona import ActivePersona
from .data_analyzer import DataAnalyzer
from .evaluator import EvaluatorBase
from .google_play_scraper import GooglePlayScraper
from .llm_client import LLMClient
from .llm_factory import LLMClientFactory
from .nielsen_evaluator import NielsenEvaluator
from .whisper_transcriber import WhisperTranscriber

__all__ = [
    'ActivePersona',
    'DataAnalyzer',
    'EvaluatorBase',
    'GooglePlayScraper',
    'LLMClient',
    'LLMClientFactory', 
    'NielsenEvaluator',
    'WhisperTranscriber',
]
