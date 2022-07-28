from __future__ import annotations
import statistics
from math import nan
from typing import TYPE_CHECKING, Union, List
from collections import Counter
from decimal import Decimal
from math import fsum, sqrt
from ... import helpers

if TYPE_CHECKING:
    from ..resource import Resource


def analyze(self: Resource, *, detailed=False) -> dict:
    """Analyze the resource

    This feature is currently experimental, and its API may change
    without warning.

    Parameters:
        detailed? (bool): detailed analysis

    Returns:
        dict: resource analysis

    """

    # Create state
    timer = helpers.Timer()

    # Row stats
    analysis_report = {}
    analysis_report["variableTypes"] = {}
    analysis_report["notNullRows"] = 0
    analysis_report["rowsWithNullValues"] = 0
    analysis_report["fieldStats"] = {}

    # Iterate rows
    columns_data = {}
    numeric = ["integer", "numeric", "number"]
    with self:
        for row in self.row_stream:
            null_columns = 0
            for field_name in row:
                field = self.schema.get_field(field_name)
                cell = field.read_cell(row.get(field_name))[0]
                if field.name not in columns_data:
                    columns_data[field.name] = []
                if cell is None:
                    if field.type in numeric:
                        cell = nan
                    null_columns += 1
                if isinstance(cell, Decimal):
                    cell = float(cell)
                columns_data[field.name].append(cell)
            if null_columns > 0:
                analysis_report["rowsWithNullValues"] += 1

    # Field/Column Stats
    if columns_data and detailed:
        analysis_report["correlations"] = {}
        for field in self.schema.fields:
            analysis_report["fieldStats"][field.name] = {}

            if field.type not in analysis_report["variableTypes"]:
                analysis_report["variableTypes"][field.type] = 0
            analysis_report["variableTypes"][field.type] += 1

            # summary - categorical data
            if field.type not in [*numeric, "boolean"]:
                analysis_report["fieldStats"][field.name]["type"] = "categorical"
                analysis_report["fieldStats"][field.name]["values"] = set(
                    columns_data[field.name]
                )

            # descriptive statistics - numeric data
            if field.type in numeric:
                analysis_report["fieldStats"][field.name]["type"] = "numeric"
                rows_without_nan_values = [
                    cell for cell in columns_data[field.name] if cell is not nan
                ]

                # skip rows with nan values
                if len(rows_without_nan_values) < 2:
                    continue

                analysis_report["fieldStats"][field.name].update(
                    _statistics(rows_without_nan_values)  # type: ignore
                )
                analysis_report["fieldStats"][field.name]["outliers"] = []
                analysis_report["fieldStats"][field.name]["missingValues"] = self.stats.rows - len(rows_without_nan_values)  # type: ignore

                # calculate correlation between variables(columns/fields)
                for field_y in self.schema.fields:
                    if field_y.type in numeric:
                        # filter rows with nan values, correlation return nan if any of the
                        # row has nan value.
                        var_x, var_y = [], []
                        for cell_x, cell_y in zip(
                            columns_data[field.name], columns_data[field_y.name]
                        ):
                            if nan not in [cell_x, cell_y]:
                                var_x.append(cell_x)
                                var_y.append(cell_y)

                        # check for atleast 2 data points for correlation calculation
                        if len(var_x) > 2:
                            if field.name not in analysis_report["correlations"]:
                                analysis_report["correlations"][field.name] = []
                            correlation_result = {
                                "fieldName": field_y.name,
                                "corr": _correlation(var_x, var_y),
                            }
                            analysis_report["correlations"][field.name].append(
                                correlation_result
                            )

                # calculate outliers
                lower_bound, upper_bound = analysis_report["fieldStats"][field.name][
                    "bounds"
                ]
                for cell in columns_data[field.name]:
                    if cell is not nan:
                        if not lower_bound < cell < upper_bound:
                            analysis_report["fieldStats"][field.name]["outliers"].append(
                                cell
                            )

    analysis_report["notNullRows"] = self.stats.rows - analysis_report["rowsWithNullValues"]  # type: ignore
    analysis_report["averageRecordSizeInBytes"] = 0
    if self.stats.rows and self.stats.bytes:
        analysis_report["averageRecordSizeInBytes"] = self.stats.bytes / self.stats.rows  # type: ignore
    analysis_report["timeTaken"] = timer.time
    return {**analysis_report, **self.stats.to_descriptor()}


# TODO:This is a temporary function to use with statistics library as
# python 3.7 does not support quantiles
# code: https://github.com/python/cpython/blob/3.8/Lib/statistics.py#L620
def _quantiles(data, *, n=4, method="exclusive") -> List:
    """Divide *data* into *n* continuous intervals with equal probability.
    Returns a list of (n - 1) cut points separating the intervals.
    Set *n* to 4 for quartiles (the default).  Set *n* to 10 for deciles.
    Set *n* to 100 for percentiles which gives the 99 cuts points that
    separate *data* in to 100 equal sized groups.
    The *data* can be any iterable containing sample.
    The cut points are linearly interpolated between data points.
    If *method* is set to *inclusive*, *data* is treated as population
    data.  The minimum value is treated as the 0th percentile and the
    maximum value is treated as the 100th percentile.
    """
    if n < 1:
        raise statistics.StatisticsError("n must be at least 1")
    data = sorted(data)
    ld = len(data)
    if ld < 2:
        raise statistics.StatisticsError("must have at least two data points")
    if method == "inclusive":
        m = ld - 1
        result = []
        for i in range(1, n):
            j, delta = divmod(i * m, n)
            interpolated = (data[j] * (n - delta) + data[j + 1] * delta) / n
            result.append(interpolated)
        return result
    if method == "exclusive":
        m = ld + 1
        result = []
        for i in range(1, n):
            j = i * m // n  # rescale i to m/n
            j = 1 if j < 1 else ld - 1 if j > ld - 1 else j  # clamp to 1 .. ld-1
            delta = i * m - j * n  # exact integer math
            interpolated = (data[j - 1] * (n - delta) + data[j] * delta) / n
            result.append(interpolated)
        return result
    raise ValueError(f"Unknown method: {method!r}")


def _common_values(data: Union[float, int]) -> Union[float, int]:
    """Finds highly common data with frequency

    Args:
        data (float|int): data

    Returns:
        (float|int): highly common element and its count
    """
    column = Counter(data)  # type: ignore
    common_value = column.most_common(1)
    if common_value and common_value[0][1] > 1:
        return common_value[0][0]
    return None  # type: ignore


def _statistics(data: Union[float, int]) -> dict:
    """Calculate the descriptive statistics of the data

    Args:
        data (float|int): data

    Returns:
        dict : statistics of the data
    """
    resource_stats = {}
    resource_stats["mean"] = statistics.mean(data)  # type: ignore
    resource_stats["median"] = statistics.median(data)  # type: ignore
    resource_stats["mode"] = _common_values(data)
    resource_stats["variance"] = statistics.variance(data)  # type: ignore
    resource_stats["quantiles"] = _quantiles(data)
    resource_stats["stdev"] = statistics.stdev(data)  # type: ignore
    resource_stats["max"] = max(data)  # type: ignore
    resource_stats["min"] = min(data)  # type: ignore
    resource_stats["bounds"] = _find_bounds(resource_stats["quantiles"])
    resource_stats["uniqueValues"] = len(set(data))  # type: ignore
    return resource_stats


def _find_bounds(quartiles: List):
    """Calculate the higher and lower bound of distribution

    Args:
        quantiles (List): list of quartiles of distribution

    Returns:
        List: upper and lower bound
    """
    q1, _, q3 = quartiles
    inter_quartile_range = q3 - q1
    upper_bound = round(q3 + (1.5 * inter_quartile_range))
    lower_bound = round(q1 - (1.5 * inter_quartile_range))
    return [lower_bound, upper_bound]


# TODO:This is a temporary function to use with statistics library as
# python 3.7 does not support correlation
# code: https://github.com/python/cpython/blob/3.10/Lib/statistics.py#L889
def _correlation(x, y) -> float:
    """Pearson's correlation coefficient
    Return the Pearson's correlation coefficient for two inputs. Pearson's
    correlation coefficient *r* takes values between -1 and +1. It measures the
    strength and direction of the linear relationship, where +1 means very
    strong, positive linear relationship, -1 very strong, negative linear
    relationship, and 0 no linear relationship
    """
    n = len(x)
    if len(y) != n:
        raise statistics.StatisticsError(
            "correlation requires that both inputs have same number of data points"
        )
    if n < 2:
        raise statistics.StatisticsError("correlation requires at least two data points")
    xbar = fsum(x) / n
    ybar = fsum(y) / n
    sxy = fsum((xi - xbar) * (yi - ybar) for xi, yi in zip(x, y))
    sxx = fsum((xi - xbar) ** 2.0 for xi in x)
    syy = fsum((yi - ybar) ** 2.0 for yi in y)
    try:
        return sxy / sqrt(sxx * syy)
    except ZeroDivisionError:
        raise statistics.StatisticsError("at least one of the inputs is constant")
