import pandas as pd
from typing import Dict, List

def build_frequency_matrix(sources: Dict[str, Dict[str, int]]) -> pd.DataFrame:
    """Builds a matrix of absolute letter frequencies per source."""
    return pd.DataFrame(sources)

def build_delta_table(sources: Dict[str, Dict[str, int]], reference_label: str = "tanach_wlc") -> pd.DataFrame:
    """Calculates letter count deltas against a specified reference source."""
    df = build_frequency_matrix(sources)
    
    if reference_label not in df.columns:
        raise ValueError(f"Reference label '{reference_label}' not found in sources.")
        
    reference_col = df[reference_label]
    delta_df = df.sub(reference_col, axis=0)
    delta_df = delta_df.drop(columns=[reference_label])
    return delta_df

def suspicion_report(results: List[dict], top_n: int = 20) -> List[dict]:
    """Orders page results by the number of illegible characters descending."""
    return sorted(results, key=lambda x: x.get("caracteres_ilegibles_count", 0), reverse=True)[:top_n]
