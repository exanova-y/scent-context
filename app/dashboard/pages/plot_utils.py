"""
Plotting utilities for sensor data visualization using Plotly.
This module provides functions for creating various types of plots
for analyzing BME688 sensor data.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict, Union, Optional, Tuple


def load_csv_data(file_path: str) -> pd.DataFrame:
    """
    Load sensor data from a CSV file.

    The CSV file is expected to have columns for timestamp, gas resistance,
    temperature, and humidity. The timestamp column is converted to datetime
    format.

    Args:
        file_path: Path to the CSV file

    Returns:
        DataFrame with the sensor data
    """
    df = pd.read_csv(file_path)
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def preprocess_data(df: pd.DataFrame, 
                   smooth_window: Optional[int] = None,
                   normalize: bool = False) -> pd.DataFrame:
    """
    Preprocess sensor data with optional smoothing and normalization.
    
    Args:
        df: DataFrame with sensor data
        smooth_window: Window size for rolling average smoothing (None for no smoothing)
        normalize: Whether to normalize numerical columns to 0-1 range
        
    Returns:
        Preprocessed DataFrame
    """
    # Make a copy to avoid modifying the original
    processed_df = df.copy()
    
    # Apply smoothing if specified
    if smooth_window is not None and smooth_window > 1:
        numeric_cols = ['gas_resistance', 'temperature', 'humidity']
        for col in numeric_cols:
            if col in processed_df.columns:
                processed_df[f'{col}_raw'] = processed_df[col]
                processed_df[col] = processed_df[col].rolling(window=smooth_window, center=True).mean()
                processed_df[col] = processed_df[col].fillna(processed_df[f'{col}_raw'])
    
    # Apply normalization if specified
    if normalize:
        numeric_cols = ['gas_resistance', 'temperature', 'humidity']
        for col in numeric_cols:
            if col in processed_df.columns:
                min_val = processed_df[col].min()
                max_val = processed_df[col].max()
                if max_val > min_val:  # Avoid division by zero
                    processed_df[f'{col}_normalized'] = (processed_df[col] - min_val) / (max_val - min_val)
    
    return processed_df


def align_dataframes(dfs: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Align multiple dataframes to use the same time range based on the shortest dataset.
    
    Args:
        dfs: Dictionary of DataFrames with sensor data
        
    Returns:
        Dictionary of aligned DataFrames
    """
    if not dfs:
        return {}
    
    # Find the shortest time range
    min_start = None
    max_end = None
    
    for df in dfs.values():
        if 'timestamp' not in df.columns:
            continue
            
        start = df['timestamp'].min()
        end = df['timestamp'].max()
        
        if min_start is None or start > min_start:
            min_start = start
        
        if max_end is None or end < max_end:
            max_end = end
    
    # Align all dataframes to this range
    aligned_dfs = {}
    for name, df in dfs.items():
        if 'timestamp' not in df.columns:
            aligned_dfs[name] = df
            continue
            
        aligned_df = df[(df['timestamp'] >= min_start) & (df['timestamp'] <= max_end)]
        aligned_dfs[name] = aligned_df
    
    return aligned_dfs


def plot_time_series(df: pd.DataFrame, 
                    y_column: str, 
                    title: str = None,
                    color_by: str = None,
                    log_scale: bool = False) -> go.Figure:
    """
    Create a time series plot of sensor data.
    
    Args:
        df: DataFrame with sensor data
        y_column: Column to plot on y-axis
        title: Plot title
        color_by: Column to use for coloring (e.g., 'scent')
        log_scale: Whether to use log scale for y-axis
        
    Returns:
        Plotly figure object
    """
    if title is None:
        title = f"{y_column} over Time"
    
    fig = px.line(df, 
                 x='timestamp', 
                 y=y_column, 
                 color=color_by,
                 title=title)
    
    if log_scale and df[y_column].min() > 0:
        fig.update_layout(yaxis_type="log")
    
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title=y_column,
        legend_title=color_by if color_by else "",
        template="plotly_white"
    )
    
    return fig


def plot_multi_series(df: pd.DataFrame, 
                     columns: List[str], 
                     title: str = "Sensor Readings",
                     color_by: str = None) -> go.Figure:
    """
    Create a multi-panel plot with multiple sensor readings.
    
    Args:
        df: DataFrame with sensor data
        columns: List of columns to plot
        title: Plot title
        color_by: Column to use for coloring (e.g., 'scent')
        
    Returns:
        Plotly figure object
    """
    n_plots = len(columns)
    fig = make_subplots(rows=n_plots, cols=1, 
                       shared_xaxes=True,
                       vertical_spacing=0.05,
                       subplot_titles=columns)
    
    # Get unique values for color grouping if specified
    if color_by and color_by in df.columns:
        groups = df[color_by].unique()
        for i, col in enumerate(columns):
            for group in groups:
                group_df = df[df[color_by] == group]
                fig.add_trace(
                    go.Scatter(
                        x=group_df['timestamp'],
                        y=group_df[col],
                        name=f"{group} - {col}" if len(groups) > 1 else col,
                        mode='lines',
                        legendgroup=group,
                        showlegend=i == 0,  # Show legend only for the first subplot
                    ),
                    row=i+1, col=1
                )
    else:
        for i, col in enumerate(columns):
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df[col],
                    name=col,
                    mode='lines'
                ),
                row=i+1, col=1
            )
    
    fig.update_layout(
        height=300 * n_plots,
        title_text=title,
        template="plotly_white"
    )
    
    return fig


def create_plotly_figure(df: pd.DataFrame, 
                        plot_type: str = 'line',
                        x: str = 'timestamp',
                        y: Union[str, List[str]] = 'gas_resistance',
                        color: str = None,
                        title: str = None,
                        **kwargs) -> go.Figure:
    """
    Create a Plotly figure with various plot types.
    
    Args:
        df: DataFrame with sensor data
        plot_type: Type of plot ('line', 'scatter', 'bar', 'box', 'violin', 'heatmap')
        x: Column for x-axis
        y: Column(s) for y-axis
        color: Column to use for coloring
        title: Plot title
        **kwargs: Additional arguments for specific plot types
        
    Returns:
        Plotly figure object
    """
    if title is None:
        if isinstance(y, list):
            title = f"{', '.join(y)} vs {x}"
        else:
            title = f"{y} vs {x}"
    
    if plot_type == 'line':
        fig = px.line(df, x=x, y=y, color=color, title=title, **kwargs)
    elif plot_type == 'scatter':
        fig = px.scatter(df, x=x, y=y, color=color, title=title, **kwargs)
    elif plot_type == 'bar':
        fig = px.bar(df, x=x, y=y, color=color, title=title, **kwargs)
    elif plot_type == 'box':
        fig = px.box(df, x=x, y=y, color=color, title=title, **kwargs)
    elif plot_type == 'violin':
        fig = px.violin(df, x=x, y=y, color=color, title=title, **kwargs)
    elif plot_type == 'heatmap':
        # For heatmap, we need to pivot the data
        if isinstance(y, list) and len(y) > 1:
            raise ValueError("Heatmap requires a single y column")
        pivot_df = df.pivot(index=x, columns=color, values=y)
        fig = px.imshow(pivot_df, title=title, **kwargs)
    else:
        raise ValueError(f"Unsupported plot type: {plot_type}")
    
    fig.update_layout(template="plotly_white")
    return fig


def plot_comparison(dfs: Dict[str, pd.DataFrame], 
                   y_column: str,
                   title: str = None,
                   log_scale: bool = False) -> go.Figure:
    """
    Create a comparison plot of multiple datasets.
    
    Args:
        dfs: Dictionary of DataFrames with sensor data
        y_column: Column to plot on y-axis
        title: Plot title
        log_scale: Whether to use log scale for y-axis
        
    Returns:
        Plotly figure object
    """
    if title is None:
        title = f"Comparison of {y_column}"
    
    # Align dataframes to use the shortest time range
    aligned_dfs = align_dataframes(dfs)
    
    fig = go.Figure()
    
    for name, df in aligned_dfs.items():
        if 'timestamp' not in df.columns or y_column not in df.columns:
            continue
            
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df[y_column],
                mode='lines',
                name=name
            )
        )
    
    if log_scale:
        fig.update_layout(yaxis_type="log")
    
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title=y_column,
        template="plotly_white"
    )
    
    return fig


def detect_events(df: pd.DataFrame, 
                 column: str, 
                 threshold: float,
                 window: int = 1,
                 direction: str = 'above') -> pd.DataFrame:
    """
    Detect events in sensor data based on threshold crossing.
    
    Args:
        df: DataFrame with sensor data
        column: Column to analyze for events
        threshold: Threshold value for event detection
        window: Minimum number of consecutive points to consider an event
        direction: Whether to detect values 'above' or 'below' the threshold
        
    Returns:
        DataFrame with events marked
    """
    result_df = df.copy()
    
    # Create a boolean mask for threshold crossing
    if direction == 'above':
        mask = result_df[column] > threshold
    elif direction == 'below':
        mask = result_df[column] < threshold
    else:
        raise ValueError("direction must be 'above' or 'below'")
    
    # Apply rolling window to ensure consecutive points
    if window > 1:
        mask = mask.rolling(window=window).sum() >= window
        mask = mask.fillna(False)
    
    # Mark events in the DataFrame
    result_df['event'] = mask
    
    # Create event groups
    result_df['event_group'] = (result_df['event'] != result_df['event'].shift()).cumsum()
    result_df['event_id'] = result_df['event_group'] * result_df['event']
    
    return result_df


def create_dashboard(df: pd.DataFrame, 
                    columns: List[str] = None) -> go.Figure:
    """
    Create a comprehensive dashboard with multiple plots.
    
    Args:
        df: DataFrame with sensor data
        columns: List of columns to include (defaults to gas_resistance, temperature, humidity)
        
    Returns:
        Plotly figure object
    """
    if columns is None:
        columns = ['gas_resistance', 'temperature', 'humidity']
    
    # Create subplots: time series for each column and a scatter plot
    fig = make_subplots(
        rows=len(columns) + 1, 
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=[f"{col} over Time" for col in columns] + ["Correlation Plot"]
    )
    
    # Add time series for each column
    for i, col in enumerate(columns):
        if 'scent' in df.columns:
            for scent in df['scent'].unique():
                scent_df = df[df['scent'] == scent]
                fig.add_trace(
                    go.Scatter(
                        x=scent_df['timestamp'],
                        y=scent_df[col],
                        mode='lines',
                        name=f"{scent} - {col}",
                        legendgroup=scent,
                        showlegend=i == 0  # Show in legend only for first plot
                    ),
                    row=i+1, col=1
                )
        else:
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df[col],
                    mode='lines',
                    name=col
                ),
                row=i+1, col=1
            )
    
    # Add correlation scatter plot (first two columns)
    if len(columns) >= 2:
        if 'scent' in df.columns:
            for scent in df['scent'].unique():
                scent_df = df[df['scent'] == scent]
                fig.add_trace(
                    go.Scatter(
                        x=scent_df[columns[0]],
                        y=scent_df[columns[1]],
                        mode='markers',
                        name=scent,
                        legendgroup=scent,
                        showlegend=False  # Already in legend
                    ),
                    row=len(columns) + 1, col=1
                )
        else:
            fig.add_trace(
                go.Scatter(
                    x=df[columns[0]],
                    y=df[columns[1]],
                    mode='markers',
                    name=f"{columns[1]} vs {columns[0]}"
                ),
                row=len(columns) + 1, col=1
            )
    
    # Update layout
    fig.update_layout(
        height=300 * (len(columns) + 1),
        title_text="Sensor Data Dashboard",
        template="plotly_white"
    )
    
    # Update x and y axis labels
    for i, col in enumerate(columns):
        fig.update_yaxes(title_text=col, row=i+1, col=1)
    
    if len(columns) >= 2:
        fig.update_xaxes(title_text=columns[0], row=len(columns) + 1, col=1)
        fig.update_yaxes(title_text=columns[1], row=len(columns) + 1, col=1)
    
    fig.update_xaxes(title_text="Time", row=len(columns), col=1)
    
    return fig
