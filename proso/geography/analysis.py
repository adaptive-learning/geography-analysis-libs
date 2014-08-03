from argparse import ArgumentParser
from os import path, makedirs
import proso.geography.answers as answer
import proso.geography.decorator as decorator
import proso.geography.difficulty


def parser_init(required=None):
    parser = ArgumentParser()
    parser.add_argument(
        '-a',
        '--answers',
        metavar='FILE',
        required=True,
        help='path to the CSV with answers')
    parser.add_argument(
        '--options',
        metavar='FILE',
        required=_is_required(required, '--options'),
        help='path to the CSV with answer options')
    parser.add_argument(
        '--ab-values',
        metavar='FILE',
        dest='ab_values',
        required=_is_required(required, '--ab-values'),
        help='path to the CSV with ab values')
    parser.add_argument(
        '--answer-ab-values',
        metavar='FILE',
        dest='answer_ab_values',
        required=_is_required(required, '--answer-ab-values'),
        help='path to the CSV with answer ab values')
    parser.add_argument(
        '-d',
        '--destination',
        metavar='DIR',
        required=True,
        help='path to the directory where the created data will be saved')
    parser.add_argument(
        '-o',
        '--output',
        metavar='EXT',
        dest='output',
        default='svg',
        help='extension for the output fles')
    parser.add_argument(
        '--optimize',
        action='store_true',
        help='enables decorator optimization')
    parser.add_argument(
        '--drop-classrooms',
        action='store_true',
        dest='drop_classrooms',
        help='drop users having some of the first answer from classroom')
    parser.add_argument(
        '--answers-per-user',
        type=int,
        dest='answers_per_user',
        help='drop user having less than the given number of answers')
    return parser


def parser_group(parser, groups):
    parser.add_argument(
        '--group',
        choices=groups,
        help='generate only a limited set of plots')
    return parser


def decorator_optimization(answers):
    decorated = decorator.rolling_success(
        decorator.last_in_session(
            decorator.session_number(answers)))
    return decorated


def load_answers(args):
    if not path.exists(args.destination):
        makedirs(args.destination)
    if path.exists(args.destination + '/geography.answer.csv'):
        return answer.from_csv(args.destination + '/geography.answer.csv')
    else:
        data = answer.from_csv(
            answer_csv=args.answers,
            answer_options_csv=args.options,
            answer_ab_values_csv=args.answer_ab_values,
            ab_value_csv=args.ab_values)
        if args.drop_classrooms:
            classroom_users = [
                user
                for ip, users in (
                    data.sort('id').drop_duplicates('user').
                    groupby('ip_address').
                    apply(lambda x: x['user'].unique()).
                    to_dict().
                    items())
                for user in users
                if len(users) > 5
            ]
            data = data[~data['user'].isin(classroom_users)]
        if args.answers_per_user:
            valid_users = map(
                lambda (u, n): u,
                filter(
                    lambda (u, n): n >= args.answers_per_user,
                    data.groupby('user').apply(len).to_dict().items()
                )
            )
            data = data[data['user'].isin(valid_users)]
        if args.optimize:
            data = decorator_optimization(data)
            data.to_csv(args.destination + '/geography.answer.csv', index=False)
        return data


def load_difficulty(args, data):
    if not path.exists(args.destination):
        makedirs(args.destination)
    if not path.exists(args.destination + '/difficulty.csv'):
        difficulty = proso.geography.difficulty.prepare_difficulty(data)
        proso.geography.difficulty.difficulty_to_csv(
            difficulty, args.destination + '/difficulty.csv')
    else:
        difficulty = proso.geography.difficulty.csv_to_difficulty(
            args.destination + '/difficulty.csv')
    return difficulty


def load_prior_skill(args, data, difficulty):
    if not path.exists(args.destination):
        makedirs(args.destination)
    if not path.exists(args.destination + '/prior_skill.csv'):
        prior_skill = proso.geography.user.prior_skill(data, difficulty)
        proso.geography.user.prior_skill_to_csv(
            prior_skill, args.destination + '/prior_skill.csv')
    else:
        prior_skill = proso.geography.user.csv_to_prior_skill(
            args.destination + '/prior_skill.csv')
    return prior_skill


def savefig(args, figure, name):
    if not path.exists(args.destination):
        makedirs(args.destination)
    figure.save(args.destination + '/' + name + '.' + args.output)


def is_group(args, group):
    return not args.group or args.group == group


def is_any_group(args, groups):
    return not args.group or args.group in groups


def _is_required(required, name):
    return required is not None and name in required
