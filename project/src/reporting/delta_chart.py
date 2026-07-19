import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from src.styles.report_style import apply_report_style

def render_delta_chart(delta_table: pd.DataFrame, output_path: str | Path) -> None:
    """Renders and saves a horizontal bar chart of letter deltas."""
    apply_report_style()
    
    fig, ax = plt.subplots()
    delta_table.plot(kind='barh', ax=ax, width=0.8)
    
    ax.set_title("Letter Frequency Deltas (vs Reference)")
    ax.set_xlabel("Delta")
    ax.set_ylabel("Hebrew Letter")
    
    ax.axvline(0, color='black', linewidth=1)
    
    plt.tight_layout()
    plt.savefig(str(output_path), dpi=300)
    plt.close(fig)
