import matplotlib.pyplot as plt

def apply_report_style() -> None:
    """Configures matplotlib rcParams for reports."""
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.rcParams.update({
        'figure.figsize': (10, 8),
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'lines.linewidth': 2,
        'font.family': 'sans-serif'
    })
