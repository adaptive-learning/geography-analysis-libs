from proso.geography.model import AnswerStream, DefaultModel
from proso.geography.environment import InMemoryEnvironment
from proso.geography.answers import first_answers
from proso.geography.dfutil import iterdicts
from proso.geography.model import predict_simple
import pandas


def difficulty_to_dataframe(difficulty):
    return pandas.DataFrame(difficulty.items()).rename(
        columns={0: 'place', 1: 'difficulty'}
    )


def dataframe_to_difficulty(dataframe):
    return dataframe.set_index('place')['difficulty'].to_dict()


def prepare_difficulty_and_prior_skill(answers, difficulty=None):
    '''
    Compute the difficulty for places.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data
    Returns:
        dict: place -> difficulty, user's id -> prior skill
    '''
    first = first_answers(answers, ['user']).sort('id').sort('id')
    if difficulty:
        env = PreserveDifficultyEnvironment(difficulty)
    else:
        env = InMemoryEnvironment()
    stream = DefaultAnswerStream(env)
    for a in iterdicts(first):
        stream.stream_answer(a)
    skill_items = env.export_prior_skill().items()
    ids, skills = zip(*skill_items)
    prior_skill = dict(zip(list(ids), map(lambda x: predict_simple(x, 0)[0], list(skills))))
    return env.export_difficulty(), prior_skill


class DefaultAnswerStream(AnswerStream):

    def __init__(self, environment):
        AnswerStream.__init__(self, DefaultModel(), environment)


class PreserveDifficultyEnvironment(InMemoryEnvironment):

    def __init__(self, difficulty):
        InMemoryEnvironment.__init__(self)
        self._difficulty = difficulty

    def difficulty(self, place_id, new_value=None):
        if new_value is None:
            return InMemoryEnvironment.difficulty(self, place_id)
