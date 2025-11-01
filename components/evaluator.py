import json
import os
import pandas as pd
import re
from datetime import datetime
from .active_persona import ActivePersona
from .logger import Logger
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class EvaluatorBase(ABC):
    """
    Abstract base class for evaluation workflows (e.g., Nielsen, SUS).
    Handles loading materials, setting images, preparing messages, running and saving evaluations.
    """

    def __init__(self, evaluation_prompt: str, auto_reset: bool = True):
        self.evaluation_prompt = evaluation_prompt
        self.auto_reset = auto_reset
        self.images_paths = []

    def set_images(self, images_paths: List[str]):
        self.images_paths = images_paths

    def _prepare_evaluation_messages(self) -> list:
        """
        Prepare the messages for persona evaluation.
        
        Returns:
            list: Formatted messages including questionnaire and images
        """
        
        # Start with the questionnaire text
        messages = []

        messages.append({"type": "text", "text": self.evaluation_prompt})
        
        # Add all images
        for image_path in self.images_paths:
            if os.path.exists(image_path):
                messages.append({"type": "image", "path": image_path})
            else:
                Logger.error(f"Warning: Image not found: {image_path}")

        return messages

    def _preprocess_entry(self, entry: dict) -> dict:
        """
        Manipulate or clean the response_json as needed before saving.
        Subclasses can override this to implement custom logic.
        By default, returns the response_json unchanged.
        """
        return entry

    def evaluate(self, active_persona: ActivePersona, iterations: int = 1) -> Dict[str, Any]:
        """
        Conduct SUS evaluation using the provided persona.
        Args:
            persona (Persona): The persona to conduct the evaluation
            iterations (int): Number of evaluation iterations to run (default: 1)
        Returns:
            Dict[str, Any]: JSON object containing evaluation results
        """

        if iterations < 1:
            iterations = 1

        messages = self._prepare_evaluation_messages()
        evaluation_results = []

        entry_template = {
            "timestamp": datetime.now().isoformat(),
            "persona_name": getattr(active_persona, 'name', 'Unknown'),
            "model": getattr(active_persona.llm_client, 'model_name', 'Unknown'),
        }

        Logger.info(f"Running {self.__class__.__name__}")
        for iteration in range(1, iterations + 1):
            try:
                Logger.info(f"-- iteration {iteration}/{iterations}")

                if self.auto_reset:
                    active_persona.reset_history()

                response = active_persona.interact(messages)
                Logger.debug(f"Response: {response}")
                
                response_json = json.loads(
                    self._extract_json(response)
                )

                #print(response_json)

                processed_entry = self._preprocess_entry(response_json)

                entry = entry_template.copy()
                entry.update(processed_entry)

                evaluation_results.append(entry)

                Logger.info(f"-- iteration {iteration} completed successfully")
                
            except Exception as e:
                Logger.error(f"-- iteration {iteration} failed: {e}")
                #print(f"Response content: {response_json}")

        Logger.info(f"{self.__class__.__name__} completed")
        
        return evaluation_results

    def evaluate_and_save(self, active_persona: ActivePersona, iterations: int = 1, save_in: str = None) -> Any:
        evaluation_results = self.evaluate(active_persona, iterations)

        if save_in is None:
            return evaluation_results
        
        persona_name = getattr(active_persona, 'name', 'Unknown')
        pre_path = f"{save_in}/{persona_name}_{self.__class__.__name__.lower()}_evaluation_results"
        csv_path = f"{pre_path}.csv"

        df = pd.DataFrame(evaluation_results)
        
        df.to_csv(csv_path, index=False, encoding='utf-8')

        Logger.info(f"{self.__class__.__name__} saved to {csv_path}")

        return evaluation_results

    def _extract_json(self, text: str) -> str:
        """
        Extract the JSON part from a string that may contain extra text before or after the JSON.
        Returns the JSON substring, or raises ValueError if not found.
        """
        
        # Find the first curly brace and try to parse from there
        match = re.search(r'({.*)', text, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in text")
        
        json_part = match.group(1)
        # Try to find the matching closing brace for the JSON object
        # This is a simple approach, assumes no nested objects with unmatched braces
        stack = []
        for i, c in enumerate(json_part):
            if c == '{':
                stack.append(i)
            elif c == '}':
                stack.pop()
                if not stack:
                    return json_part[:i+1]

        Logger.error(f"Could not extract complete JSON object. Response content: {text}")
        raise ValueError("Could not extract complete JSON object")
