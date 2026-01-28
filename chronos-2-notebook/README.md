# Satellite Communications Capacity Forecasting

This notebook demonstrates how to use Chronos-2, a foundation model for time series forecasting, to predict satellite communications capacity utilization.

## Overview

The notebook `satcom-chronos-forecast.ipynb` implements time series forecasting for satellite communications data using Chronos-2, which offers significant improvements over previous models including:
- Univariate and multivariate forecasting
- Cross-learning across multiple time series
- Support for both real and categorical covariates
- Extended context length up to 8192 time steps
- Fine-tuning capabilities

## Prerequisites

- Python 3.x
- Jupyter Notebook or JupyterLab
- Required Python packages:
  - chronos-forecasting >= 2.2
  - numpy
  - matplotlib
  
## Installation

1. Clone this top-level repository
2. Install the required packages (already done in the Jupyter notebook):

## Usage
The notebook can be run in multiple environments:
- Amazon SageMaker Studio Lab
- Local Jupyter environment

To run the notebook:

Open satcom-chronos-forecast.ipynb

Follow the step-by-step instructions in the notebook

Execute each cell in sequence

## Features
- Time series based forecasting with multiple related variables
- Forecasting of future satellite capacity utilization
- Visualization of results
- Support for both zero-shot forecasting and fine-tuning

## Modifications
Update the following for your own use-case: -
- bucket_name      # Replace with your S3 bucket name
- train_key        # Replace with your training file path in S3
- test_key         # Replace with your test file path in S3

- target           # Column name containing the values to forecast 
- prediction_length   # 1 day (6 x 10 mins x 24)
- id_column        # Column identifying different time series 
- timestamp_column # Column containing datetime information

- timeseries_id    # Specific time series to visualize (spot beam)
