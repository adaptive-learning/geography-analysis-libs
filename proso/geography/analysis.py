from argparse import ArgumentParser
from os import path, makedirs
import proso.geography.answers as answer
import proso.geography.decorator as decorator
import proso.geography.difficulty
import gc
import numpy as np


def parser_init(required=None):
    parser = ArgumentParser()
    parser.add_argument(
        '-a',
        '--answers',
        metavar='FILE',
        required=_is_required(required, '--answers'),
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
        '--drop-classrooms',
        action='store_true',
        dest='drop_classrooms',
        help='drop users having some of the first answer from classroom')
    parser.add_argument(
        '--drop-tests',
        action='store_true',
        dest='drop_tests',
        help='drop users having at least one test answer')
    parser.add_argument(
        '--answers-per-user',
        type=int,
        dest='answers_per_user',
        help='drop user having less than the given number of answers')
    parser.add_argument(
        '--data-dir',
        type=str,
        metavar='DIRECTORY',
        dest='data_dir',
        default='./data',
        help='directory with data files, used when the data files are specified')
    return parser


def data_hash(args):
    return 'apu_%s__dcs_%s__dts_%s' % (args.answers_per_user, args.drop_classrooms, args.drop_tests)


def parser_group(parser, groups):
    parser.add_argument(
        '--groups',
        choices=groups,
        nargs='+',
        help='generate only a limited set of plots')
    parser.add_argument(
        '--skip-groups',
        choices=groups,
        dest='skip_groups',
        nargs='+',
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
    filename = '%s/geography.answer_%s.csv' % (args.destination, data_hash(args))
    filename_all = '%s/geography.answer.csv' % (args.destination)
    answers_col_types = {
        'session_number': np.uint8,
        'options': str,
        'ab_values': str,
        'last_in_session': bool,
        'rolling_success': np.float16
    }
    # assume the data are already sorted by id in CSV files
    if path.exists(filename):
        return (
            answer.from_csv(filename, answers_col_types=answers_col_types, should_sort=False),
            answer.from_csv(filename_all, answers_col_types=answers_col_types, should_sort=False)
        )
    else:
        if path.exists(args.destination + '/geography.answer.csv'):
            data_all = answer.from_csv(
                args.destination + '/geography.answer.csv', answers_col_types=answers_col_types, should_sort=False)
        else:
            answers_file = args.answers if args.answers else args.data_dir + '/geography.answer.csv'
            options_file = args.options if args.options else args.data_dir + '/geography.answer_options.csv'
            ab_values_file = args.ab_values if args.ab_values else args.data_dir + '/geography.ab_value.csv'
            answer_ab_values_file = args.answer_ab_values if args.answer_ab_values else args.data_dir + '/geography.answer_ab_values.csv'
            if not path.exists(options_file):
                options_file = None
            if not path.exists(ab_values_file):
                ab_values_file = None
            if not path.exists(answer_ab_values_file):
                answer_ab_values_file = None
            data_all = answer.from_csv(
                answer_csv=answers_file,
                answer_options_csv=options_file,
                answer_ab_values_csv=answer_ab_values_file,
                ab_value_csv=ab_values_file,
                answers_col_types=answers_col_types,
                should_sort=False)
            data_all = decorator_optimization(data_all)
            data_all.to_csv(args.destination + '/geography.answer.csv', index=False)
        data = data_all
        if args.drop_tests:
            data = answer.apply_filter(data, lambda x: np.isnan(x['test_id']))
        if args.drop_classrooms:
            data = answer.drop_classrooms(data)
        if args.answers_per_user:
            data = answer.drop_users_by_answers(data, answer_limit_min=args.answers_per_user)
        data.to_csv(filename, index=False)
        return data, data_all


def load_difficulty(args, data_all):
    if not path.exists(args.destination):
        makedirs(args.destination)
    if not path.exists(args.destination + '/difficulty.csv'):
        difficulty = proso.geography.difficulty.prepare_difficulty(data_all)
        proso.geography.difficulty.difficulty_to_csv(
            difficulty, args.destination + '/difficulty.csv')
    else:
        difficulty = proso.geography.difficulty.csv_to_difficulty(
            args.destination + '/difficulty.csv')
    gc.collect()
    return difficulty


def load_prior_skill(args, data_all, difficulty):
    if not path.exists(args.destination):
        makedirs(args.destination)
    if not path.exists(args.destination + '/prior_skill.csv'):
        prior_skill = proso.geography.user.prior_skill(data_all, difficulty)
        proso.geography.user.prior_skill_to_csv(
            prior_skill, args.destination + '/prior_skill.csv')
    else:
        prior_skill = proso.geography.user.csv_to_prior_skill(
            args.destination + '/prior_skill.csv')
    gc.collect()
    return prior_skill


def savefig(args, figure, name):
    if not path.exists(args.destination):
        makedirs(args.destination)
    figure.savefig(args.destination + '/' + name + '.' + args.output, bbox_inches='tight')


def is_group(args, group):
    return (not args.groups or group in args.groups) and (not args.skip_groups or group not in args.skip_groups)


def is_any_group(args, groups):
    return any([is_group(args, group) for group in groups])


def _is_required(required, name):
    return required is not None and name in required
