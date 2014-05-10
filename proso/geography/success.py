import decorator


def rolling_success_hist(answers, window_length=10):
    '''
    Number of rolling windows with the given success rate.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data
        window_length (int, default 10, optional):
            number of answers in window

    Return:
        dict: success rate -> number of windows
    '''
    if 'rolling_success' in answers:
        data = answers
    else:
        data = decorator.rolling_success(answers, window_length=window_length)
    return (data.
        dropna().
        groupby('rolling_success').
        apply(len).
        to_dict())


def stay_on_rolling_success(answers, window_length=10):
    '''
    Compute the probability the user stays in the system (the next answers
    belongs to the same session) based on the rolling success rate.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data
        window_length (int, default 10, optional):
            number of answers in window

    Return:
        dict: success rate -> probability the user stays in the system
    '''
    if 'rolling_success' in answers:
        data = answers
    else:
        data = decorator.rolling_success(answers, window_length=window_length)
    return (data.
        dropna().
        groupby(['user', 'rolling_success']).
        apply(lambda x: sum(~x['last_in_session']) / float(len(x))).
        reset_index().
        rename(columns={0: 'stay'}).
        groupby('rolling_success').
        apply(lambda x: x['stay'].mean()).
        to_dict())
