import os
import pandas as pd
import time
from datetime import datetime
from dotenv import load_dotenv
from components.data_analyzer import DataAnalyzer
from components.llm_factory import LLMClientFactory
from components.active_persona import ActivePersona
from components.nielsen_evaluator import NielsenEvaluator
from components.logger import Logger

load_dotenv()

persona_dir = os.getenv("PERSONA_DIR")
prompt_dir = os.getenv("PROMPT_DIR")
result_dir = os.getenv("RESULT_DIR")

def run_evaluations(
    llm_model_names: list[str],
    persona_names: list[str],
    images: list[str] = [],
    save_in: str = "./results/nielsen_evaluations",
    iterations: int = 10
):
    """
    Execute Nielsen heuristics evaluations using AI personas.
    
    This function orchestrates the complete evaluation workflow:
    1. Loads evaluation prompts and system templates
    2. Validates image assets exist
    3. Creates LLM clients and active personas
    4. Runs evaluations with timing metrics
    
    Args:
        llm_model_names: List of LLM model identifiers to use
        persona_names: List of persona file names (without .md extension)
        images: List of image file paths for evaluation
        save_in: Directory path to save evaluation results
        iterations: Number of evaluation runs per persona-model combination
    """
    Logger.info("Starting Nielsen heuristics evaluation workflow")
    
    # Load Nielsen evaluation prompt template
    with open(f"./{prompt_dir}/nielsen_evaluation.md", 'r', encoding='utf-8') as f:
        nielsen_evaluation_prompt = f.read().strip()

    # Initialize evaluator with the prompt
    evaluator = NielsenEvaluator(evaluation_prompt=nielsen_evaluation_prompt)

    # Validate all image files exist before proceeding
    missing_images = [img for img in images if not os.path.isfile(img)]
    if missing_images:
        Logger.error("Missing image files:")
        for img in missing_images:
            Logger.error(f"  {img}")
        raise FileNotFoundError("One or more images are missing. Aborting execution.")
    
    Logger.info("All image files validated")
    evaluator.set_images(images)

    # Create LLM clients for all specified models
    Logger.info("Initializing LLM clients...")
    llm_clients = LLMClientFactory.create_clients(llm_model_names)

    # Load system prompt template for persona configuration
    with open(f"./{prompt_dir}/system_prompt_template.md", 'r', encoding='utf-8') as f:
        system_prompt_template = f.read().strip()

    # Create active personas for each persona-model combination
    Logger.info("Creating active personas...")
    active_personas = {}
    for persona_name in persona_names:
        # Load persona description from markdown file
        with open(f"./{persona_dir}/{persona_name}.md", 'r', encoding='utf-8') as f:
            persona_description = f.read().strip()

        # Inject persona details into system prompt template
        system_prompt = system_prompt_template.replace('[persona_detail]', persona_description)

        # Create persona instance for each LLM model
        for model_name, llm_client in llm_clients.items():
            persona_key = f"{persona_name}_{model_name}"
            active_personas[persona_key] = ActivePersona(
                name=persona_key,
                llm_client=llm_client,
                system_prompt=system_prompt
            )

    # Create output directory and run evaluations
    os.makedirs(save_in, exist_ok=True)
    Logger.info(f"Results directory: {save_in}")

    # Execute evaluations for each persona-model combination
    for persona_key, active_persona in active_personas.items():
        Logger.info(f"Evaluating {persona_key}...")
        
        start_time = time.time()
        evaluator.evaluate_and_save(
            active_persona=active_persona,
            iterations=iterations,
            save_in=save_in
        )
        
        # Log timing metrics
        duration = time.time() - start_time
        avg_duration = duration / iterations
        Logger.info(f"Completed {persona_key} in {duration:.1f}s (avg: {avg_duration:.1f}s per iteration)")

def perform_statistical_analysis(result_dir: str = "./result"):
    """
    Merge evaluation CSV files and perform statistical analysis.
    
    This function consolidates individual evaluation results into a unified dataset
    and runs Kruskal-Wallis tests to identify significant differences between
    persona-model combinations.
    
    Args:
        result_dir: Directory containing evaluation CSV files
    """
    Logger.info("Preparing evaluation dataset...")
    
    # Statistical significance threshold
    ALPHA = 0.05

    # Initialize data analyzer
    analyzer = DataAnalyzer(output_prefix="nielsen")
    analysis_output_dir = os.path.join(result_dir, "stats", "analysis")

    # Merge all evaluation CSV files
    Logger.info("Merging evaluation files...")
    merged_df = analyzer.merge_evaluations(directory=result_dir, stats_only=False)

    if merged_df.empty:
        Logger.error("No data to analyze - merge failed")
        return

    # Perform Kruskal-Wallis statistical tests
    Logger.info("Running statistical analysis...")
    kruskal_results = analyzer.perform_kruskal_wallis_analysis(
        df=merged_df,
        output_dir=analysis_output_dir
    )

    if kruskal_results is None:
        Logger.error("Statistical analysis failed")
        return

    # Interpret results and add decision column
    Logger.info(f"Interpreting results (alpha = {ALPHA})...")
    kruskal_results['Decision'] = kruskal_results['pvalue'].apply(
        lambda p: 'Significant' if p < ALPHA else 'Not significant'
    )
    
    Logger.info("Statistical analysis completed")
    print("Statistical test results:")
    print(str(kruskal_results[['pvalue', 'Decision']]))
    
    decision_summary = kruskal_results['Decision'].value_counts()
    Logger.info("Decision summary:")
    Logger.info(str(decision_summary))

    # Save results with decisions
    output_file = os.path.join(analysis_output_dir, 'kruskal_wallis_results_with_decision.csv')
    kruskal_results.to_csv(output_file)
    Logger.info(f"Results saved to: {output_file}")


def main():
    """
    Main execution function with workflow configuration.
    
    This function controls which parts of the evaluation pipeline to execute:
    - run_evaluations_enabled: Execute new evaluations
    - prepare_dataset_enabled: Merge results and run statistical tests
    - Statistical analysis is always performed if data exists
    """
    # Workflow configuration
    run_evaluations_enabled = True
    perform_statistical_analysis_enabled = True

    # Model and persona configuration
    llm_model_names = ['llama', 'claude', 'gemini', 'openai']
    persona_names = ['claudio', 'ingrid']
    iterations = 2

    # Output directory with today's date
    today_date = datetime.now().strftime("%Y%m%d")
    save_in = f"./{result_dir}/{today_date}"

    # Image assets for evaluation
    images = [
        "./data/img/skn_small/1-skn_home_screen_en.jpg",
        "./data/img/skn_small/2-skn_search_journey_screen_en.jpg",
        "./data/img/skn_small/3-skn_journey_list_screen_en.jpg",
        "./data/img/skn_small/4-skn_journey_list_filter_en.jpg",
        "./data/img/skn_small/5-skn_journey_detail_screen_en.jpg",
        "./data/img/skn_small/6-skn_ticket_selection_screen_en.jpg",
        "./data/img/skn_small/6-skn_ticket_selection_screen_se.jpg",
        "./data/img/skn_small/7-skn_ticket_detail_screen_en.jpg",
        "./data/img/skn_small/7-skn_ticket_detail_screen_se.jpg",
    ]

    # Execute enabled workflow steps
    if run_evaluations_enabled:
        run_evaluations(
            llm_model_names=llm_model_names,
            persona_names=persona_names,
            images=images,
            save_in=save_in,
            iterations=iterations
        )

    if perform_statistical_analysis_enabled:
        perform_statistical_analysis(result_dir = save_in)

if __name__ == "__main__":
    main()