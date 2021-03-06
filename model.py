from sklearn.linear_model import LinearRegression
from sklearn import metrics
import numpy as np
import pandas as pd
import datetime as dt

from collections import namedtuple


Model = namedtuple('Model', 'linearModel r2 actuals predictions offset')
Prediction = namedtuple('Prediction', 'dates actuals predictions')


def BestFitModel(new_cases, new_deaths, max_offset) -> Model:
    best = Model(None, 0.0, None, None, 0)

    # find an offset, in days, where cases best correlate to future deaths
    for offset in range(1, max_offset):
        cases = new_cases[-0:-offset]
        deaths = new_deaths[offset:]

        model = LinearRegression().fit(cases, deaths)
        predictions = model.predict(cases)
        r2 = metrics.r2_score(deaths, predictions)
        if (r2 > best.r2):
            best = Model(model, r2, deaths, predictions, offset)

    return best


def Predict(model: Model, dates, cases, deaths) -> Prediction:
    # create a new date series for the range over which we will predict
    # (it is wider than the source date range by [offset]. that is how far in the future we can predict)
    minDate = np.amin(dates)
    maxDate = np.amax(dates) + np.timedelta64(model.offset + 1, 'D')

    projected_dates = pd.Series([date for date in np.arange(minDate, maxDate, dt.timedelta(days=1))])

    # padding so actuals and predictions can be graphed together within dates
    padding = pd.Series(np.full(model.offset, np.nan))
    
    predicted_deaths = model.linearModel.predict(cases)
    actual_deaths = deaths.append(padding)
    projected_deaths = padding.append(pd.Series(predicted_deaths))

    return Prediction(projected_dates.values, actual_deaths.values, projected_deaths.values)
