def success_per_week(answers):
    return (answers.
        set_index('inserted').
        groupby([lambda x: x.year, lambda x: x.week]).
        apply(lambda x: float(len(x[x['place_asked'] == x['place_answered']])) / float(len(x))).
        to_dict())


def success_by_user_per_week(answers):
    return (answers.
        set_index('inserted').
        groupby(['user', lambda x: x.year, lambda x: x.week]).
        apply(lambda x: float(len(x[x['place_asked'] == x['place_answered']])) / float(len(x))).
        reset_index().
        rename(columns={0: 'sucess'}).
        groupby(['level_1', 'level_2']).
        apply(lambda x: x.sucess.mean()).
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
        set_index('inserted').
        groupby(lambda x: x.date()).
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
