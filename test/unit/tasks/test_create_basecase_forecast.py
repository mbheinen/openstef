# SPDX-FileCopyrightText: 2017-2021 Alliander N.V. <korte.termijn.prognoses@alliander.com> # noqa E501>
#
# SPDX-License-Identifier: MPL-2.0
from unittest import TestCase
from unittest.mock import MagicMock, patch

from openstf.tasks.create_basecase_forecast import create_basecase_forecast_task

from test.utils import TestData

FORECAST_MOCK = "forecast_mock"


class TestCreateBasecaseForecastTask(TestCase):
    def setUp(self) -> None:
        self.pj = TestData.get_prediction_job(pid=307)

    @patch(
        "openstf.tasks.create_basecase_forecast.create_basecase_forecast_pipeline",
        MagicMock(return_value=FORECAST_MOCK),
    )
    def test_create_basecase_forecast_task_happy_flow(self):
        # Test happy flow of create forecast task
        context = MagicMock()
        create_basecase_forecast_task(self.pj, context)
        self.assertEqual(context.mock_calls[1].args[0], FORECAST_MOCK)