from difficulty import DefaultAnswerStream, PreserveDifficultyEnvironment
from proso.geography.answers import first_answers
from proso.geography.dfutil import iterdicts
from proso.geography.model import predict_simple
import pandas


def prior_skill(answers, difficulty):
    '''
    Assuming the given difficulty of places compute the prior skill for users.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data
        difficulty (dict):
            place -> difficulty
    Returns:
        dict: user's id -> prior skill
    '''
    first = first_answers(answers, ['user']).sort('id')
    env = PreserveDifficultyEnvironment(difficulty)
    stream = DefaultAnswerStream(env)
    for a in iterdicts(first):
        stream.stream_answer(a)
    skill_items = env.export_prior_skill().items()
    ids, skills = zip(*skill_items)
    return dict(zip(list(ids), map(lambda x: predict_simple(x, 0)[0], list(skills))))


def prior_skill_to_csv(prior_skill, filename):
    '''
    Save the given prior skill dictionary to the CSV file.

    Args:
        prior_skill (dict):
            user's id -> prior skill
        filename (str):
            name of the file where the data is going to be stored
    '''
    pandas.DataFrame(prior_skill.items()).rename(
        columns={0: 'user', 1: 'prior_skill'}
    ).to_csv(filename, index=False)


def csv_to_prior_skill(filename):
    '''
    Load the prior skill dictionary from the given CSV file.

    Args:
        filename (str):
            name of the file with the data
    Returns:
        dict: user's id-> prior skill
    '''
    return (pandas.
        read_csv(filename).
        set_index('user')['prior_skill'].
        to_dict())


def answers_per_user(answers):
    '''
    Number of answers per user.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data
    Return:
        dict: user's id -> number of answers
    '''
    return (answers.
        groupby('user').
        apply(len).
        reset_index().
        sort(0, ascending=False)[0].
        to_dict())
