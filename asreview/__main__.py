#!/usr/bin/env python
# encoding: utf-8

"""Command Line Interface (CLI) for ASReview project."""

import argparse
import sys
import warnings
from argparse import RawTextHelpFormatter

import numpy as np

from asreview import __version__  # noqa
from asreview.review import review_oracle, review_simulate  # noqa
from asreview.config import AVAILABLE_MODI  # noqa

# Descriptions

PROG_DESCRIPTION = f"""
Automated Systematic Review (ASReview).

Use one of the modi: '{AVAILABLE_MODI[0]}' or '{AVAILABLE_MODI[1]}'
"""

PROG_DESCRIPTION_SIMULATE = """
Automated Systematic Review (ASReview) for simulation runs.

The simulation modus is used to measure the performance of our
software on existing systematic reviews. The software shows how many
papers you could have potentially skipped during the systematic
review."""

PROG_DESCRIPTION_ORACLE = """
Automated Systematic Review (ASReview) with interaction with oracle.

The oracle modus is used to perform a systematic review with
interaction by the reviewer (the ‘oracle’ in literature on active
learning). The software presents papers to the reviewer, whereafter
the reviewer classifies them."""

# CLI defaults
DEFAULT_MODEL = "lstm_pool"
DEFAULT_QUERY_STRATEGY = "rand_max"
DEFAULT_BALANCE_STRATEGY = "triple_balance"
DEFAULT_N_INSTANCES = 20
DEFAULT_N_PRIOR_INCLUDED = 10
DEFAULT_N_PRIOR_EXCLUDED = 10


def _parse_arguments(mode, prog=sys.argv[0]):
    """Argument parser for oracle and simulate.

    Parameters
    ----------
    mode : str
        The mode to run ASReview. Options:
        'simulate' and 'oracle'.
    prog : str
        The program name. For example 'asreview'.

    Returns
    -------
    argparse.ArgumentParser
        Configured argparser.
    """

    if mode == "simulate":
        prog_description = PROG_DESCRIPTION_SIMULATE
    elif mode == "oracle":
        prog_description = PROG_DESCRIPTION_ORACLE
    else:
        prog_description = ""

    # parse arguments if available
    parser = argparse.ArgumentParser(
        prog=prog,
        description=prog_description,
        formatter_class=RawTextHelpFormatter
    )
    # File path to the data.
    parser.add_argument(
        "dataset",
        type=str,
        metavar="X",
        help="File path to the dataset or one of the built-in datasets."
    )
    # Active learning parameters
    parser.add_argument(
        "-m", "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"The prediction model for Active Learning. "
             f"Default '{DEFAULT_MODEL}'.")
    parser.add_argument(
        "-q", "--query_strategy",
        type=str,
        default=DEFAULT_QUERY_STRATEGY,
        help=f"The query strategy for Active Learning. "
             f"Default '{DEFAULT_QUERY_STRATEGY}'.")
    parser.add_argument(
        "-b", "--balance_strategy",
        type=str,
        default=DEFAULT_BALANCE_STRATEGY,
        help="Data rebalancing strategy mainly for RNN methods. Helps against"
             " imbalanced dataset with few inclusions and many exclusions. "
             f"Default '{DEFAULT_BALANCE_STRATEGY}'")
    parser.add_argument(
        "--n_instances",
        default=DEFAULT_N_INSTANCES,
        type=int,
        help="Number of papers queried each query."
             f"Default {DEFAULT_N_INSTANCES}.")
    parser.add_argument(
        "--n_queries",
        type=int,
        default=None,
        help="The number of queries. By default, the program"
             "stops after all documents are reviewed or is "
             "interrupted by the user."
    )
    parser.add_argument(
        "--embedding",
        type=str,
        default=None,
        dest='embedding_fp',
        help="File path of embedding matrix. Required for LSTM models."
    )
    # Configuration file with model/balance/query parameters.
    parser.add_argument(
        "--config_file",
        type=str,
        default=None,
        help="Configuration file with model parameters"
    )
    # Continue with previous log file.
    parser.add_argument(
        "-s", "--session-from-log",
        type=str,
        default=None,
        dest="src_log_fp",
        help="Continue session starting from previous log file."
    )
    # Initial data (prior knowledge)
    parser.add_argument(
        "--prior_included",
        default=None,
        type=int,
        nargs="*",
        help="A list of included papers.")

    parser.add_argument(
        "--prior_excluded",
        default=None,
        type=int,
        nargs="*",
        help="A list of excluded papers. Optional.")

    # these flag are only available for the simulation modus
    if mode == "simulate":

        # Initial data (prior knowledge)
        parser.add_argument(
            "--n_prior_included",
            default=DEFAULT_N_PRIOR_INCLUDED,
            type=int,
            help="Sample n prior included papers. "
                 "Only used when --prior_included is not given. "
                 f"Default {DEFAULT_N_PRIOR_INCLUDED}")

        parser.add_argument(
            "--n_prior_excluded",
            default=DEFAULT_N_PRIOR_EXCLUDED,
            type=int,
            help="Sample n prior excluded papers. "
                 "Only used when --prior_excluded is not given. "
                 f"Default {DEFAULT_N_PRIOR_EXCLUDED}")

    # logging and verbosity
    parser.add_argument(
        "--log_file", "-l",
        default=None,
        type=str,
        help="Location to store the log results."
    )
    parser.add_argument(
        "--save_model",
        default=None,
        type=str,
        dest='save_model_fp',
        help="Location to store the model and weights. "
             "Only works for Keras/RNN models. "
             "End file extension with '.json'."
    )
    parser.add_argument(
        "--verbose", "-v",
        default=1,
        type=int,
        help="Verbosity")

    return parser


def _review_oracle():

    parser = _parse_arguments("oracle", prog="asreview oracle")
    args = parser.parse_args(sys.argv[2:])

    args_dict = vars(args)
    path = args_dict.pop("dataset")

    review_oracle(path, **args_dict)


def _review_simulate():
    """CLI to the oracle mode."""

    parser = _parse_arguments("simulate", prog="asreview simulate")
    args = parser.parse_args(sys.argv[2:])

    args_dict = vars(args)
    path = args_dict.pop("dataset")

    review_simulate(path, **args_dict)


def main_depr():
    warnings.warn("'asr' has been renamed to "
                  "'asreview', it will be removed in the future.\n",
                  np.VisibleDeprecationWarning)
    main()


def main():
    # launch asr interactively
    if len(sys.argv) > 1 and sys.argv[1] == "oracle":
        _review_oracle()

    # launch asr with oracle
    elif len(sys.argv) > 1 and sys.argv[1] == "simulate":
        _review_simulate()

    # no valid sub command
    else:
        parser = argparse.ArgumentParser(
            prog="asr",
            description=PROG_DESCRIPTION
        )
        parser.add_argument(
            "subcommand",
            nargs="?",
            type=lambda x: isinstance(x, str) and x in AVAILABLE_MODI,
            default=None,
            help=f"The subcommand to launch. Available commands: "
            f"{AVAILABLE_MODI}"
        )

        # version
        parser.add_argument(
            "-V", "--version",
            action='store_true',
            help="print the ASR version number and exit")

        args = parser.parse_args()

        # output the version
        if args.version:
            print(__version__)
            return

        if args.subcommand is None:
            print("Use 'asr -h' to view help.")


# execute main function
if __name__ == "__main__":
    main()