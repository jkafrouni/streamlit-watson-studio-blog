import pandas as pd
import plotly.express as px

def format_tuples(t):
    """A helper function to format tuples in dropdowns.

    Args:
        t (tuple): A tuple made of an id and name, e.g. (project_id, project_name)
    """
    if isinstance(t, tuple):
        return f"{t[0]} (id: {t[1]})"
    else:
        return str(t)


def make_basic_roc_curve(fpr, tpr):
    """Given fpr and tpr values for an ROC curve,
    generates an ROC curve with TPR against FPR in plotly express
    as commonly used.

    Args:
        fpr (array-like): List or vector of False Positive Rates
        fpr (array-like): List or vector of True Positive Rates

    Returns:
        fig (plotly figure): An ROC curve plotted in plotly.
    """
    fig = px.area(
        x=fpr, y=tpr,
        title=f'ROC Curve',
        labels=dict(x='False Positive Rate', y='True Positive Rate'),
        width=700, height=500
    )
    fig.add_shape(
        type='line', line=dict(dash='dash'),
        x0=0, x1=1, y0=0, y1=1
    )

    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_xaxes(constrain='domain')
    return fig


def make_advanced_roc_curve(fpr, tpr, thresholds):
    """Given fpr and tpr values for an ROC curve, as well as thresholds used
    to calculate these rates, generates two line plots for FPR against threshold
    and TPR against threshold.

    Args:
        fpr (array-like): List or vector of False Positive Rates
        fpr (array-like): List or vector of True Positive Rates
        thresholds (array-like): List or vector of Thresholds

    Returns:
        fig (plotly figure): A plotly figure as described above
    """
    # see https://plotly.com/python/roc-and-pr-curves/
    df_roc = pd.DataFrame({
        "False Positive Rate": fpr,
        "True Positive Rate": tpr,
    }, index=thresholds)
    df_roc.index.name = "Thresholds"
    df_roc.columns.name = "Rate"

    fig = px.line(
        df_roc, title='TPR and FPR at every threshold',
        width=700, height=500
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_xaxes(range=[0, 1], constrain='domain')
    return fig


def format_autoai_results(metrics):
    """Parses and pivots metrics from a model trained in AutoAI.

    Args:
        metrics (dict): A dictionary of metrics from training and holdout sets

    Returns:
        metrics (pd.DataFrame): A pivotted metrics dataframe with training v.
        holdout groups as columns and metric names as index
    """
    metrics = pd.DataFrame({'raw_metric': metrics})
    metrics['group'] = metrics.index.str.split('_').map(lambda s: s[0])
    metrics['metric'] = metrics.index.str.split('_').map(lambda s: '_'.join(s[1:]))
    metrics = metrics.pivot_table('raw_metric', 'metric', 'group')
    return metrics
