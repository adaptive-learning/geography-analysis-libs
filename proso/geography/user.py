def answers_per_user(answers):
    '''
    Number of answers per user.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data
    Return:
        dict: user id -> number of answers
    '''
    return (answers.
        groupby('user').
        apply(len).
        reset_index().
        sort(0, ascending=False)[0].
        to_dict())


def users_per_day(answers):
    '''
    Number of user having answers in the given day.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data

    Return:
        dict: datetime.date -> number of users
    '''
    return (answers.
        groupby(lambda x: answers.inserted[x].date()).
        apply(lambda x: x.user.nunique()).
        to_dict())


def answers_per_day(answers):
    '''
    Number of answers per day.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data

    Return:
        dict: datetime.date -> number of answers
    '''
    return (answers.
        groupby(['user', lambda x: answers.inserted[x].date()]).
        apply(len).
        reset_index().
        rename(columns={0: 'answers_count', 'level_1': 'inserted_date'}).
        groupby('inserted_date').
        apply(lambda x: x.answers_count.mean()).
        to_dict())
