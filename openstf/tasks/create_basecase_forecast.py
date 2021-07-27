# SPDX-FileCopyrightText: 2017-2021 Alliander N.V. <korte.termijn.prognoses@alliander.com> # noqa E501>
#
# SPDX-License-Identifier: MPL-2.0

# -*- coding: utf-8 -*-
"""create_basecase_forecast.py

This module should be executed once every day. For all prediction_jobs, it will
create a 'basecase' forecast which is less accurate, but (almost) always available.
For now, it uses the load a week earlier.
Missing datapoints are interpolated.

Example:
    This module is meant to be called directly from a CRON job. A description of the
    CRON job can be found in the /k8s/CronJobs folder.

    Alternatively this code can be run directly by running:

        $ python create_basecase_forecast.py
"""
from datetime import datetime, timedelta
import pandas as pd

from openstf.pipeline.create_basecase_forecast import create_basecase_forecast_pipeline
from openstf.tasks.utils.predictionjobloop import PredictionJobLoop
from openstf.tasks.utils.taskcontext import TaskContext

T_BEHIND_DAYS: int = 15
T_AHEAD_DAYS: int = 3


def create_basecase_forecast_task(pj: dict, context: TaskContext) -> None:
    """Top level task that creates a basecase forecast.
    On this task level all database and context manager dependencies are resolved.

    Args:
        pj (dict): Prediction job
        context (TaskContext): Contect object that holds a config manager and a database connection
    """
    # Define datetime range for input data
    datetime_start = datetime.utcnow() - timedelta(days=T_BEHIND_DAYS)
    datetime_end = datetime.utcnow() + timedelta(days=T_AHEAD_DAYS)

    # Retrieve input data
    input_data = context.database.get_model_input(
        pid=pj["id"],
        location=[pj["lat"], pj["lon"]],
        datetime_start=datetime_start,
        datetime_end=datetime_end,
    )

    # Make basecase forecast using the corresponding pipeline
    basecase_forecast = create_basecase_forecast_pipeline(pj, input_data)

    # Do not store basecase forecasts for moments within next 48 hours.
    # Those should be updated by regular forecast process.
    basecase_forecast = basecase_forecast.loc[
        basecase_forecast.index
        > (pd.to_datetime(datetime.utcnow(), utc=True) + timedelta(hours=48)),
        :,
    ]

    # Write basecase forecast to the database
    context.database.write_forecast(basecase_forecast, t_ahead_series=True)


def main():
    with TaskContext("create_basecase_forecast") as context:
        model_type = ["xgb", "lgb"]

        PredictionJobLoop(context, model_type=model_type).map(
            create_basecase_forecast_task, context
        )


if __name__ == "__main__":
    main()
