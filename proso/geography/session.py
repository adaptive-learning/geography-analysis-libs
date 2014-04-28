import decorator


def session_length(answers):
    '''
    Compute average length of session according to the session number.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data, if it is not decorated by 'session_number',
            it will be decorated
    Return:
        dict: session number -> number of answers
    '''
    if 'session_number' in answers:
        data = answers
    else:
        data = decorator.session_number(answers)
    return (data.
        groupby(['user', 'session_number']).
        apply(lambda x: len(x)).
        reset_index().
        rename(columns={0: 'session_length'}).
        groupby('session_number').
        apply(lambda x: x['session_length'].mean()).
        reset_index().
        rename(columns={0: 'session_length'}).
        set_index('session_number')['session_length'].
        to_dict())


def session_users(answers):
    '''
    Compute number of users having answers in the given sessions according to
    the session number.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data, if it is not decorated by 'session_number',
            it will be decorated
    Return:
        dict: session number -> number of users
    '''
    if 'session_number' in answers:
        data = answers
    else:
        data = decorator.session_number(answers)
    return (data.
        groupby(['session_number']).
        apply(lambda x: x['user'].nunique()).
        reset_index().
        rename(columns={0: 'frequency'}).
        set_index('session_number')['frequency'].
        to_dict())
