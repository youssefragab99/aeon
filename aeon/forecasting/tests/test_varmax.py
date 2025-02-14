"""Tests the VARMAX model."""

__author__ = ["KatieBuc"]

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose

from aeon.forecasting.base import ForecastingHorizon
from aeon.forecasting.model_selection import temporal_train_test_split
from aeon.forecasting.varmax import VARMAX
from aeon.utils.validation._dependencies import _check_soft_dependencies

np.random.seed(13455)
index = pd.date_range(start="2020-01", end="2021-12", freq="M")
df = pd.DataFrame(
    np.random.randint(0, 100, size=(23, 3)),
    columns=list("ABC"),
    index=pd.PeriodIndex(index),
)


@pytest.mark.skipif(
    not all(
        (
            _check_soft_dependencies("statsmodels", severity="none"),
            _check_soft_dependencies("pandas<2.0.0", severity="none"),
        )
    ),
    reason="skip test if required soft dependency not available",
)
def test_VARMAX_against_statsmodels():
    """Compares aeon's and Statsmodel's VARMAX.

    with default variables.
    """
    from statsmodels.tsa.api import VARMAX as _VARMAX

    train, _ = temporal_train_test_split(df.astype("float64"))
    y = train[["A", "B"]]

    aeon_model = VARMAX()
    fh = ForecastingHorizon([1, 3, 4, 5, 7, 9])
    aeon_model.fit(y)
    y_pred = aeon_model.predict(fh=fh)

    stats = _VARMAX(y)
    stats_fit = stats.fit()
    start, end = len(train) + fh[0] - 1, len(train) + fh[-1] - 1
    y_pred_stats = stats_fit.predict(start=start, end=end)
    y_pred_stats = y_pred_stats.loc[fh.to_absolute(train.index[-1]).to_pandas()]

    assert_allclose(y_pred, y_pred_stats)


@pytest.mark.skipif(
    not all(
        (
            _check_soft_dependencies("statsmodels", severity="none"),
            _check_soft_dependencies("pandas<2.0.0", severity="none"),
        )
    ),
    reason="skip test if required soft dependency not available",
)
def test_VARMAX_against_statsmodels_with_exog():
    """Compares aeon's and Statsmodel's VARMAX.

    with exogenous input.
    """
    from statsmodels.tsa.api import VARMAX as _VARMAX

    train, test = temporal_train_test_split(df.astype("float64"))
    y_train, X_train = train[["A", "B"]], train[["C"]]
    _, X_test = test[["A", "B"]], test[["C"]]
    fh = ForecastingHorizon([1, 2, 3, 4, 5, 6])
    assert len(fh) == len(X_test)

    aeon_model = VARMAX()
    aeon_model.fit(y_train, X=X_train)
    y_pred = aeon_model.predict(fh=fh, X=X_test)

    stats = _VARMAX(y_train, exog=X_train)
    stats_fit = stats.fit()
    start, end = len(train) + fh[0] - 1, len(train) + fh[-1] - 1
    y_pred_stats = stats_fit.predict(start=start, end=end, exog=X_test)
    y_pred_stats = y_pred_stats.loc[fh.to_absolute(train.index[-1]).to_pandas()]

    assert_allclose(y_pred, y_pred_stats)
