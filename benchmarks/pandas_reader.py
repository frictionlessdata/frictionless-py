"""Benchmark pandas row conversion separately from complete resource validation.

Run from the repository root with the pandas extra installed. Use the same
Python environment and script for both reader revisions, applying only the
PandasParser row-mapping fix between runs:

    python benchmarks/pandas_reader.py --label before > before.json
    python benchmarks/pandas_reader.py --label after > after.json

The default matrix uses 100/500 rows and 10/50/94/200 columns, with one string
column and otherwise float columns. Override --rows, --columns or --repetitions
to explore other sizes. Run on Linux, where ru_maxrss is reported in KiB.

Each shape/workload runs in a fresh process. Timings are unprofiled; a separate
profile counts Series.to_dict calls. Peak RSS includes imports, frame creation,
warmup and timed repetitions, but excludes the subsequent profile.

pandas_reader_results.json records the baseline revision, versions, individual
timings, medians, conversion counts and peak RSS for both revisions. These are
sequential synthetic runs on a shared host without CPU isolation. Parser timing
includes schema conversion and stream consumption. Validation reads the whole
frame without row limits. Neither workload includes Parquet decoding; these
measurements do not establish a Parquet memory improvement or a general speedup.
"""

import argparse
import cProfile
import json
import platform
import resource
import statistics
import subprocess
import sys
import time
from collections import deque

import numpy as np
import pandas as pd
import pyarrow

import frictionless
from frictionless.formats.pandas import PandasParser
from frictionless.resources import TableResource


def measure(rows, columns, mode, repetitions):
    dataframe = pd.DataFrame(
        {
            "label": [f"row-{index}" for index in range(rows)],
            **{
                f"value_{index}": np.full(rows, float(index))
                for index in range(columns - 1)
            },
        }
    )

    def run():
        source = TableResource(data=dataframe, format="pandas")
        if mode == "parser":
            deque(PandasParser(source).read_cell_stream_create(), maxlen=0)
        else:
            assert source.validate().valid

    run()  # Untimed warmup, identical for both revisions.
    seconds = []
    for _ in range(repetitions):
        start = time.perf_counter()
        run()
        seconds.append(time.perf_counter() - start)
    peak_rss_kib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    profiler = cProfile.Profile()
    profiler.runcall(run)
    calls = sum(
        entry.callcount
        for entry in profiler.getstats()
        if not isinstance(entry.code, str)
        and entry.code.co_filename.endswith("/series.py")
        and entry.code.co_name == "to_dict"
    )
    return dict(
        rows=rows,
        columns=columns,
        mode=mode,
        seconds=seconds,
        median_seconds=statistics.median(seconds),
        series_to_dict_calls=calls,
        peak_rss_kib=peak_rss_kib,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", default="current")
    parser.add_argument("--rows", nargs="+", type=int, default=[100, 500])
    parser.add_argument("--columns", nargs="+", type=int, default=[10, 50, 94, 200])
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--worker", choices=["parser", "validation"])
    args = parser.parse_args()
    if args.worker:
        print(
            json.dumps(
                measure(args.rows[0], args.columns[0], args.worker, args.repetitions)
            )
        )
        return
    results = []
    for rows in args.rows:
        for columns in args.columns:
            for mode in ["parser", "validation"]:
                output = subprocess.check_output(
                    [
                        sys.executable,
                        __file__,
                        "--worker",
                        mode,
                        "--rows",
                        str(rows),
                        "--columns",
                        str(columns),
                        "--repetitions",
                        str(args.repetitions),
                    ],
                    text=True,
                )
                results.append(json.loads(output))
                print(
                    f"{args.label}: {rows} rows, {columns} columns, {mode}",
                    file=sys.stderr,
                )
    print(
        json.dumps(
            dict(
                label=args.label,
                versions=dict(
                    python=sys.version,
                    platform=platform.platform(),
                    frictionless=frictionless.__version__,
                    pandas=pd.__version__,
                    numpy=np.__version__,
                    pyarrow=pyarrow.__version__,
                ),
                repetitions=args.repetitions,
                results=results,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
