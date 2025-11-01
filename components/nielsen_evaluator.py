import logging
from datetime import datetime
from typing import Dict, Any, Optional
from .active_persona import ActivePersona
from .evaluator import EvaluatorBase
from .logger import Logger

logger = logging.getLogger(__name__)

class NielsenEvaluator(EvaluatorBase):
    """
    Nielsen Heuristics Evaluator for UX analysis.
    
    This class conducts user experience evaluations based on Jakob Nielsen's 
    10 usability heuristics. It leverages AI personas to provide structured
    feedback on interface designs and user workflows.
    
    Key Responsibilities:
    - Execute Nielsen heuristics-based evaluation sessions
    - Process evaluation guide templates with Nielsen questionnaires
    - Generate structured evaluation reports with persona insights
    - Support multiple evaluation iterations for consistency analysis
    
    Evaluation Output:
    - Timestamped evaluation results with persona metadata
    - Support for both nested and flattened JSON formats
    - Integration with persona-driven evaluation workflows
    """
    
    def __init__(self, evaluation_prompt: str, auto_reset: bool = True):
        Logger.debug(f"Initializing NielsenEvaluator with auto_reset={auto_reset}")
        Logger.debug(f"Evaluation prompt length: {len(evaluation_prompt)} characters")
        
        super().__init__(
            evaluation_prompt = evaluation_prompt,
            auto_reset = auto_reset
        )
        
        Logger.debug("NielsenEvaluator initialization completed successfully")
    
    def evaluate_and_save(self, active_persona: ActivePersona, iterations: int = 1, save_in: str = None) -> Dict[str, Any]:
        """
        Save evaluation results to a JSON file.
        
        Args:
            active_persona (ActivePersona): The persona to conduct the evaluation
            iterations (int): Number of evaluation iterations to run (default: 1)
            save_in (str): Path where to save the results
        """
        Logger.debug(f"NielsenEvaluator starting evaluation for persona '{active_persona.name}'")
        Logger.debug(f"Parameters: iterations={iterations}, save_in={save_in}")
        
        try:
            result = super().evaluate_and_save(
                active_persona = active_persona, 
                iterations = iterations, 
                save_in = save_in
            )
            
            Logger.debug(f"NielsenEvaluator evaluation completed successfully for persona '{active_persona.name}'")
            Logger.debug(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Non-dict result'}")
            
            return result
            
        except Exception as e:
            Logger.error(f"NielsenEvaluator evaluation failed for persona '{active_persona.name}': {str(e)}")
            raise
