import numpy as np
import pandas as pd


def session_number(answers, delta_in_seconds=1800, override=False):
    '''
    Assign session number to every answer.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data
        time_delta (numpy.timedelta64, optional):
            maximal time gap between 2 answers to be marked in the same session
        override (bool, optional, default False):
            if False and the data contains 'session_number' column already, the
            decoration will be skipped.
    Returns:
        pandas.DataFrame: data frame containing answer data
    '''
    if not override and 'session_number' in answers:
        return answers
    return (answers.
        sort(['user', 'id']).
        groupby('user').
        apply(lambda x: _session_number_for_user(x, delta_in_seconds)).
        sort())


def _session_number_for_user(group, delta_in_seconds):
    session_duration = np.timedelta64(delta_in_seconds, 's')
    group['session_number'] = (
        (group['inserted'] - group['inserted'].shift(1) > session_duration).
        fillna(1).
        cumsum())
    return group
