import csv
import pandas as pd
import os
import glob
import numpy as np
from scipy.stats import kruskal
from .logger import Logger

class DataAnalyzer:
    """
    A class for analyzing evaluation results data by merging CSV files and extracting statistical information.
    """
    
    def __init__(self, output_prefix: str = "merged"):
        """
        Initialize the DataAnalyzer.
        
        Args:
            output_prefix (str): Prefix for output files (default: "merged")
        """
        self.output_prefix = output_prefix
        Logger.debug(f"DataAnalyzer initialized with output_prefix: {output_prefix}")
    
    def merge_evaluations(self, directory: str, stats_only: bool = False) -> pd.DataFrame:
        """
        Scan CSV files in directory, merge them into a single DataFrame with proper formatting.
        
        Args:
            directory (str): Directory containing CSV evaluation files
            stats_only (bool): If True, save only statistical columns (id, persona_name, model, q01-q20).
                              If False, save all columns. Default: False
        
        Returns:
            pd.DataFrame: Merged DataFrame with id, persona columns added
        """
        Logger.info(f"Starting merge_evaluations for directory: {directory}")
        Logger.debug(f"Stats only mode: {stats_only}")
        
        # Scan for CSV files in the directory, excluding subdirectories like 'stats'
        pattern = os.path.join(directory, "*.csv")
        file_list = [f for f in glob.glob(pattern) if os.path.isfile(f)]
        
        if not file_list:
            Logger.error(f"No CSV files found in directory: {directory}")
            return pd.DataFrame()
        
        Logger.info(f"Found {len(file_list)} CSV files in {directory}")
        
        # Load and merge all CSV files
        dfs = []
        for file_path in file_list:
            try:
                df = pd.read_csv(file_path, header=0, dtype=str)
                Logger.debug(f"Loaded: {os.path.basename(file_path)} ({len(df)} rows)")
                dfs.append(df)

            except Exception as e:
                Logger.error(f"Error loading {file_path}: {e}")
                continue
        
        if not dfs:
            Logger.error("No valid CSV files could be loaded")
            return pd.DataFrame()
        
        # Merge all DataFrames
        merged_df = pd.concat(dfs, ignore_index=True)
        Logger.info(f"Merged {len(dfs)} files into DataFrame with {len(merged_df)} total rows")
        
        # Add 'id' column at the beginning
        merged_df['id'] = [f"eval_{i+1}" for i in range(len(merged_df))]
        
        # Extract 'persona' from 'persona_name' if it exists
        if 'persona_name' in merged_df.columns:
            merged_df['persona'] = merged_df['persona_name'].apply(
                lambda x: str(x).split('_')[0] if pd.notnull(x) else ''
            )

            Logger.info(f"Extracted personas: {sorted(merged_df['persona'].unique())}")
        
        # Reorder columns: id first, then persona after persona_name
        cols = merged_df.columns.tolist()
        
        # Move 'id' to first position
        if 'id' in cols:
            cols.insert(0, cols.pop(cols.index('id')))
        
        # Move 'persona' after 'persona_name'
        if 'persona' in cols and 'persona_name' in cols:
            persona_idx = cols.index('persona')
            persona_name_idx = cols.index('persona_name')
            # Remove 'persona' from current position
            cols.pop(persona_idx)
            # Insert 'persona' after 'persona_name'
            cols.insert(persona_name_idx + 1, 'persona')
        
        merged_df = merged_df[cols]
        
        # Save the merged DataFrame
        self._save_dataframe(merged_df, directory, stats_only)
        
        Logger.info(f"Merge evaluations completed successfully")
        return merged_df
    
    def perform_kruskal_wallis_analysis(self, df: pd.DataFrame, output_dir: str):
        """
        Performs Kruskal-Wallis H-test on the provided DataFrame to check for significant
        differences between persona-model groups for each question.
        
        This method coordinates the preparation, execution, and saving of the analysis.
        
        Args:
            df (pd.DataFrame): The DataFrame to analyze (should be the output of merge_evaluations).
            output_dir (str): The directory to save analysis results (CSVs).
        """
        Logger.info("Performing Kruskal-Wallis analysis...")
        
        os.makedirs(output_dir, exist_ok=True)
        Logger.debug(f"Created output directory: {output_dir}")
        
        # 1. Prepare data for analysis
        df_analysis, question_columns = self._prepare_analysis_data(df)
        if df_analysis is None:
            Logger.error("Failed to prepare analysis data")
            return None
            
        # 2. Run statistical tests
        results_df = self._run_kruskal_wallis_tests(df_analysis, question_columns)
        
        # 3. Save results to CSV file
        output_path = os.path.join(output_dir, 'kruskal_wallis_results.csv')
        results_df.to_csv(output_path, quotechar='"', quoting=csv.QUOTE_ALL)
        
        Logger.info(f"Analysis complete. Results saved to: {output_path}")
        return results_df

    def _prepare_analysis_data(self, df: pd.DataFrame):
        """Prepares the DataFrame for Kruskal-Wallis analysis."""
        Logger.debug("Preparing data for Kruskal-Wallis analysis")
        
        if not all(col in df.columns for col in ['persona', 'model']):
            Logger.error("Error: 'persona' and 'model' columns are required for this analysis")
            return None, None
            
        df_analysis = df.copy()
        df_analysis['persona_model'] = df_analysis['persona'] + '_' + df_analysis['model']
        Logger.debug(f"Created persona_model combinations: {df_analysis['persona_model'].unique()}")
        
        question_columns = sorted([col for col in df_analysis.columns if col.startswith('q') and col[1:].isdigit()])
        if not question_columns:
            Logger.error("Error: No question columns (e.g., 'q01', 'q02') found for analysis")
            return None, None
            
        for col in question_columns:
            df_analysis[col] = pd.to_numeric(df_analysis[col], errors='coerce')
            
        Logger.info(f"Analyzing {len(question_columns)} questions across {len(df_analysis['persona_model'].unique())} groups.")
        return df_analysis, question_columns

    def _run_kruskal_wallis_tests(self, df_analysis: pd.DataFrame, question_columns: list):
        """Runs the Kruskal-Wallis test for each question."""
        Logger.debug(f"Running Kruskal-Wallis tests for {len(question_columns)} questions")
        
        results = {}
        for question in question_columns:
            groups = [df_analysis[question].dropna()[df_analysis['persona_model'] == group] for group in df_analysis['persona_model'].unique()]
            
            try:
                h_stat, p_value = kruskal(*groups)
                Logger.debug(f"Question {question}: H-stat={h_stat:.4f}, p-value={p_value:.6f}")
            except ValueError as e:
                if 'All numbers are identical' in str(e) or 'must contain at least one dimension' in str(e):
                    h_stat, p_value = np.nan, 1.0
                    Logger.debug(f"Question {question}: All values identical or insufficient data")
                else:
                    Logger.error(f"Error in Kruskal-Wallis test for {question}: {e}")
                    raise e
            
            results[question] = {'hstat': h_stat, 'pvalue': p_value}
            
        results_df = pd.DataFrame(results).T
        
        Logger.info(f"Completed Kruskal-Wallis tests for {len(question_columns)} statements")
        
        return results_df

    def _save_dataframe(self, df: pd.DataFrame, directory: str, stats_only: bool):
        """
        Save the DataFrame to CSV file(s) based on the stats_only flag.
        
        Args:
            df (pd.DataFrame): DataFrame to save
            directory (str): Output directory
            stats_only (bool): Whether to save only statistical columns
        """
        Logger.debug(f"Saving DataFrame to directory: {directory}")
        
        # Create stats subdirectory if it doesn't exist
        stats_dir = os.path.join(directory, "stats")
        os.makedirs(stats_dir, exist_ok=True)
        
        Logger.debug(f"Created stats directory: {stats_dir}")
        
        if stats_only:
            # Save only statistical columns
            stats_columns = self._get_stats_columns(df)
            df_stats = df[stats_columns]
            
            output_path = os.path.join(stats_dir, f"_stats_{self.output_prefix}_evaluation_results.csv")
            df_stats.to_csv(output_path, index=False, quotechar='"', quoting=csv.QUOTE_ALL)
            
            Logger.info(f"Saved stats-only DataFrame to: {output_path}")
            Logger.debug(f"Stats DataFrame shape: {df_stats.shape}")
            
        else:
            # Save full DataFrame
            full_output_path = os.path.join(stats_dir, f"_{self.output_prefix}_evaluation_results.csv")
            df.to_csv(full_output_path, index=False, quotechar='"', quoting=csv.QUOTE_ALL)
            
            Logger.info(f"Saved full DataFrame to: {full_output_path}")
            
            # Also save stats version
            stats_columns = self._get_stats_columns(df)
            df_stats = df[stats_columns]
            stats_output_path = os.path.join(stats_dir, f"_stats_{self.output_prefix}_evaluation_results.csv")
            df_stats.to_csv(stats_output_path, index=False, quotechar='"', quoting=csv.QUOTE_ALL)
            
            Logger.info(f"Saved stats DataFrame to: {stats_output_path}")
            Logger.debug(f"Full DataFrame shape: {df.shape}, Stats DataFrame shape: {df_stats.shape}")
    
    def _get_stats_columns(self, df: pd.DataFrame) -> list:
        """
        Get columns needed for statistical analysis.
        
        Args:
            df (pd.DataFrame): Input DataFrame
            
        Returns:
            list: List of column names for statistical analysis
        """
        # Base columns
        base_columns = ['id', 'persona_name', 'persona']
        
        # Add model column if it exists
        if 'model' in df.columns:
            base_columns.append('model')
        
        # Add question columns (q01, q02, ..., q20)
        question_columns = [col for col in df.columns if col.startswith('q') and len(col) <= 3 and col[1:].isdigit()]
        question_columns = sorted(question_columns, key=lambda x: int(x[1:]))
        
        # Combine all columns that exist in the DataFrame
        stats_columns = [col for col in base_columns + question_columns if col in df.columns]
        
        Logger.debug(f"Stats columns identified: {len(stats_columns)} columns")
        return stats_columns
    
    def get_summary_stats(self, df: pd.DataFrame) -> dict:
        """
        Get summary statistics about the merged DataFrame.
        
        Args:
            df (pd.DataFrame): Input DataFrame
            
        Returns:
            dict: Summary statistics
        """
        Logger.debug("Generating summary statistics")
        
        stats = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'unique_personas': len(df['persona'].unique()) if 'persona' in df.columns else 0,
            'personas': sorted(df['persona'].unique()) if 'persona' in df.columns else [],
            'unique_models': len(df['model'].unique()) if 'model' in df.columns else 0,
            'models': sorted(df['model'].unique()) if 'model' in df.columns else [],
            'question_columns': [col for col in df.columns if col.startswith('q') and len(col) <= 3 and col[1:].isdigit()]
        }
        
        Logger.debug(f"Summary stats: {stats['total_rows']} rows, {stats['total_columns']} columns")
        Logger.debug(f"Personas: {stats['personas']}, Models: {stats['models']}")
        
        return stats
    