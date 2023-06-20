from __future__ import annotations

import statistics
from collections import Counter
from decimal import Decimal
from math import nan
from typing import TYPE_CHECKING, Any, Dict, List, Union

import attrs

from .. import helpers
from . import types

if TYPE_CHECKING:
    from ..resources import TableResource


class Analyzer:
    # Resoure

    def analyze_table_resource(
        self, resource: TableResource, *, detailed: bool = False
    ) -> types.IAnalysisReport:
        # Create state
        timer = helpers.Timer()

        # Row stats
        analysis_report = {}
        analysis_report["variableTypes"] = {}
        analysis_report["notNullRows"] = 0
        analysis_report["rowsWithNullValues"] = 0
        analysis_report["fieldStats"] = {}

        # Iterate rows
        columns_data: Dict[str, List[Any]] = {}
        numeric = ["integer", "numeric", "number"]
        with resource:
            for row in resource.row_stream:
                null_columns = 0
                for field_name in row:
                    field = resource.schema.get_field(field_name)
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
                    analysis_report["rowsWithNullValues"] += 1  # type: ignore

        # Field/Column Stats
        if columns_data and detailed:
            analysis_report["correlations"] = {}
            for field in resource.schema.fields:
                analysis_report["fieldStats"][field.name] = {}

                if field.type not in analysis_report["variableTypes"]:
                    analysis_report["variableTypes"][field.type] = 0
                analysis_report["variableTypes"][field.type] += 1  # type: ignore

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

                    analysis_report["fieldStats"][field.name].update(  # type: ignore
                        _statistics(rows_without_nan_values)  # type: ignore
                    )
                    analysis_report["fieldStats"][field.name]["outliers"] = []
                    analysis_report["fieldStats"][field.name]["missingValues"] = resource.stats.rows - len(rows_without_nan_values)  # type: ignore

                    # calculate correlation between variables(columns/fields)
                    for field_y in resource.schema.fields:
                        if field_y.type in numeric:
                            # filter rows with nan values, correlation return nan if any of the
                            # row has nan value.
                            var_x: List[Any] = []
                            var_y: List[Any] = []
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
                                correlation_result = {  # type: ignore
                                    "fieldName": field_y.name,
                                    "corr": statistics.correlation(var_x, var_y),  # type: ignore
                                }
                                analysis_report["correlations"][field.name].append(  # type: ignore
                                    correlation_result
                                )

                    # calculate outliers
                    lower_bound, upper_bound = analysis_report["fieldStats"][field.name][  # type: ignore
                        "bounds"
                    ]
                    for cell in columns_data[field.name]:
                        if cell is not nan:
                            if not lower_bound < cell < upper_bound:
                                analysis_report["fieldStats"][field.name][  # type: ignore
                                    "outliers"
                                ].append(cell)

        analysis_report["notNullRows"] = resource.stats.rows - analysis_report["rowsWithNullValues"]  # type: ignore
        analysis_report["averageRecordSizeInBytes"] = 0
        if resource.stats.rows and resource.stats.bytes:
            analysis_report["averageRecordSizeInBytes"] = resource.stats.bytes / resource.stats.rows  # type: ignore
        analysis_report["timeTaken"] = timer.time
        return {
            **analysis_report,
            **attrs.asdict(resource.stats, filter=lambda _, v: v is not None),
        }


# Internal


def _common_values(data: Union[float, int]) -> Union[float, int]:
    """Finds highly common data with frequency

    Args:
        data (float|int): data

    Returns:
        (float|int): highly common element and its count
    """
    column = Counter(data)  # type: ignore
    common_value = column.most_common(1)  # type: ignore
    if common_value and common_value[0][1] > 1:
        return common_value[0][0]  # type: ignore
    return None  # type: ignore


def _statistics(data: Union[float, int]) -> Dict[str, Any]:
    """Calculate the descriptive statistics of the data

    Args:
        data (float|int): data

    Returns:
        dict : statistics of the data
    """
    resource_stats: Dict[str, Any] = {}
    resource_stats["mean"] = statistics.mean(data)  # type: ignore
    resource_stats["median"] = statistics.median(data)  # type: ignore
    resource_stats["mode"] = _common_values(data)
    resource_stats["variance"] = statistics.variance(data)  # type: ignore
    resource_stats["quantiles"] = statistics.quantiles(data)  # type: ignore
    resource_stats["stdev"] = statistics.stdev(data)  # type: ignore
    resource_stats["max"] = max(data)  # type: ignore
    resource_stats["min"] = min(data)  # type: ignore
    resource_stats["bounds"] = _find_bounds(resource_stats["quantiles"])  # type: ignore
    resource_stats["uniqueValues"] = len(set(data))  # type: ignore
    return resource_stats


def _find_bounds(quartiles: List[Any]):
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
