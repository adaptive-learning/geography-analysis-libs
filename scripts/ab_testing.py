from argparse import ArgumentParser
from os import path, makedirs
import matplotlib.pyplot as plt
import proso.geography.answers as answer
import proso.geography.graph as graph
import proso.geography.difficulty
import proso.geography.decorator as decorator
import datetime


def get_parser():
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
        help='path to the CSV with answer options')
    parser.add_argument(
        '-d',
        '--destination',
        metavar='DIR',
        required=True,
        help='path to the directory where the created data will be saved')
    parser.add_argument(
        '-new',
        '--new-users-only',
        type=bool,
        default=True,
        dest='new_users_only',
        help='drop users having some answers without ab_value')
    parser.add_argument(
        '-o'
        '--output',
        metavar='EXT',
        dest='output',
        default='svg',
        help='extension for the output fles')
    parser.add_argument(
        '--decorator',
        default=True,
        metavar='BOOL',
        help='enables decorator optimization')
    return parser


def decorator_options(args, answers):
    if 'options' in answers:
        return answers
    if not args.options:
        raise Exception('you have to define CSV with answer options')
    return answer.options_from_csv(
        answers=answers,
        answer_options_csv=args.options)


def decorator_optimization(args, answers):
    decorated = decorator.rolling_success(
        decorator.last_in_session(
            decorator.session_number(answers)))
    decorated.to_csv(args.answers, index=False)
    return decorated


def main():
    csrf_hotfix = datetime.datetime(year=2014, month=4, day=25, hour=23)
    args = get_parser().parse_args()
    if not path.exists(args.destination):
        makedirs(args.destination)
    data = answer.from_csv(args.answers)
    data = decorator_options(args, data)
    if args.decorator:
        data = decorator_optimization(args, data)

    if not path.exists(args.destination + '/difficulty.csv'):
        difficulty = proso.geography.difficulty.prepare_difficulty(data)
        proso.geography.difficulty.difficulty_to_csv(
            difficulty, args.destination + '/difficulty.csv')
    else:
        difficulty = proso.geography.difficulty.csv_to_difficulty(
            args.destination + '/difficulty.csv')

    data_ab_testing = data.dropna(subset=['ab_value'])
    data_ab_testing = data_ab_testing[data_ab_testing['inserted'] > csrf_hotfix]
    data_ab_testing.to_csv(args.destination + '/geography.answer.ab_testing.csv')
    if args.new_users_only:
        data_before_ab_testing = data[data['ab_value'].isnull()]
        data_before_csrf_hotfix = data[data['inserted'] <= csrf_hotfix]
        data_ab_testing = data_ab_testing[
            ~data_ab_testing['user'].isin(data_before_ab_testing['user'].unique())
        ]
        data_ab_testing = data_ab_testing[
            ~data_ab_testing['user'].isin(data_before_csrf_hotfix['user'].unique())
        ]
    for ab_value, group_data in list(data_ab_testing.groupby('ab_value')):
        fig = plt.figure()
        graph.plot_session_length(fig, group_data)
        fig.suptitle('AB testing: ' + ab_value)
        fig.savefig(args.destination + 'session_length_' + ab_value + '.' + args.output)
        fig = plt.figure()
        graph.plot_session_success(fig, group_data)
        fig.suptitle('AB testing: ' + ab_value)
        fig.savefig(args.destination + 'session_success_' + ab_value + '.' + args.output)
        fig = plt.figure()
        graph.plot_session_prior_skill(fig, group_data, difficulty)
        fig.suptitle('AB testing: ' + ab_value)
        fig.savefig(args.destination + 'session_prior_skill_' + ab_value + '.' + args.output)
    fig = plt.figure()
    graph.boxplot_prior_skill_diff(fig, data_ab_testing, difficulty, 'ab_value', 0, 1)
    fig.suptitle('AB testing: difference between prior skills for the first and for the second session')
    fig.savefig(args.destination + 'session_prior_skill_diff_0vs1.' + args.output)
    fig = plt.figure()
    graph.boxplot_success_diff(fig, data_ab_testing, 'ab_value', 0, 1)
    fig.suptitle('AB testing: success difference from the first and the second session')
    fig.savefig(args.destination + 'session_success_diff_0vs1.' + args.output)
    fig = plt.figure()
    graph.boxplot_answers_per_user(fig, data_ab_testing, 'ab_value')
    fig.suptitle('AB testing: number of answers per user')
    fig.savefig(args.destination + '/answers_per_user.' + args.output)
    fig = plt.figure()
    graph.boxplot_answers_per_user(fig,
        data_ab_testing[data_ab_testing['session_number'] == 0], 'ab_value')
    fig.suptitle('AB testing: number of answers per user (only the first session)')
    fig.savefig(args.destination + '/answers_per_user_session_0.' + args.output)


if __name__ == "__main__":
    main()
