import numpy as np
import pandas as pd
from proso.geography.dfutil import iterdicts


def interested_ab_values(answers, group_prefixes, override=False):
    if not override and 'interested_ab_values' in answers:
        return answers

    answers['interested_ab_values'] = (
        answers['ab_values'].
        apply(lambda values: '__'.join(sorted(filter_ab_values_by_prefix(values, group_prefixes))))
    )
    return answers


def success_before(feedback, answers, override=False):
    if len(feedback) == 0:
        return feedback
    if not override and 'success_before' in feedback:
        return feedback
    feedback.sort(['user', 'id'], inplace=True)
    last_user = None
    user_data = None
    last_date = None
    success_before_dict = {}
    for row in iterdicts(feedback):
        if row['user'] != last_user:
            last_user = row['user']
            last_date = None
            user_data = answers[answers['user'] == last_user]
        filter_fun = lambda x: x['inserted'] < row['inserted'] and (last_date is None or x['inserted'] > last_date)
        interval_data = user_data[user_data.apply(filter_fun, axis=1)]
        prob = sum(interval_data['place_asked'] == interval_data['place_answered']) / float(len(interval_data))
        success_before_dict[row['id']] = int(5 * round(float(prob * 100) / 5))
    feedback['success_before'] = feedback.apply(lambda x: success_before_dict[x['id']], axis=1)
    return feedback


def filter_ab_values_by_prefix(values, prefixes):
    def _valid_value(value):
        for prefix in prefixes:
            if prefix == 'recommendation_target_prob_':
                if value.startswith(prefix) and not value.startswith('recommendation_target_prob_adjustment_'):
                    return True
            elif value.startswith(prefix):
                return True
        return False
    return filter(_valid_value, values)


def ab_group(answers, group_prefixes, override=False):
    if not override and 'ab_group' in answers:
        return answers
    if 'interested_ab_values' not in answers:
        answers = interested_ab_values(answers, group_prefixes)

    def drop_prefixes(name, prefixes):
        for prefix in prefixes:
            name = name.replace(prefix, "")
        return name
    uniques = answers['interested_ab_values'].unique()
    mapping = dict(zip(
        range(len(uniques)),
        map(lambda x: drop_prefixes(x, group_prefixes), uniques)))
    mapping_reverse = dict(zip(
        uniques,
        range(len(uniques))))
    answers['ab_group'] = answers['interested_ab_values'].apply(lambda x: mapping_reverse[x])
    return answers, mapping


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


def last_in_session(answers, override=False):
    '''
    Assign the boolean marker to each answer whether the answer is the last in
    the given session.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data
        override (bool, optional, default False):
            if False and the data contains 'last_in_session' column already, the
            decoration will be skipped.
    Returns:
        pandas.DataFrame: data frame containing answer data
    '''
    if not override and 'last_in_session' in answers:
        return answers
    if 'session_number' in answers:
        data = answers
    else:
        data = session_number(answers)
    return (data.
        groupby('user').
        apply(_last_in_session_for_user).
        sort())


def rolling_success(answers, window_length=10, override=False):
    '''
    Assign the rolling success to each answer.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data
        window_length (int, optional):
            the rolling success is computed for only a few last answers - window,
            this parameter sets the size of this window
        override (bool, optional, default False):
            if False and the data contains 'rolling_success' column already, the
            decoration will be skipped.
    Returns:
        pandas.DataFrame: data frame containing answer data
    '''
    if not override and 'rolling_success' in answers:
        return answers
    if 'last_in_session' in answers:
        data = answers
    else:
        data = last_in_session(answers)
    return (data.
        groupby(['user', 'session_number']).
        apply(lambda x: _rolling_succcess_for_user_session(x, window_length)).
        sort())


def _last_in_session_for_user(group):
    data = group.sort(['session_number', 'id'])
    data['last_in_session'] = data['session_number'] != data.shift(-1)['session_number']
    return data


def _rolling_succcess_for_user_session(group, window_length):
    group['rolling_success'] = pd.rolling_apply(
        group['place_asked'] == group['place_answered'],
        window_length,
        lambda x: sum(x) / float(window_length))
    return group


def _session_number_for_user(group, delta_in_seconds):
    session_duration = np.timedelta64(delta_in_seconds, 's')
    group['session_number'] = (
        (group['inserted'] - group['inserted'].shift(1) > session_duration).
        fillna(1).
        cumsum())
    return group
