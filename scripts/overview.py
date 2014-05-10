from argparse import ArgumentParser
from os import path, makedirs
import matplotlib.pyplot as plt
import proso.geography.answers as answer
import proso.geography.decorator as decorator
import proso.geography.graph as graph
import proso.geography.difficulty
import proso.geography.user as user


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
        '-o',
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
    parser.add_argument(
        '--group',
        choices=['time', 'session', 'recommendation', 'knowledge'],
        help='generate only a limited set of plots')
    return parser


def decorator_optimization(args, answers):
    decorated = decorator.rolling_success(
        decorator.last_in_session(
            decorator.session_number(answers)))
    decorated.to_csv(args.answers, index=False)
    return decorated


def decorator_options(args, answers):
    if 'options' in answers:
        return answers
    if not args.options:
        raise Exception('you have to define CSV with answer options')
    return answer.options_from_csv(
        answers=answers,
        answer_options_csv=args.options)


def main():
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

    if not path.exists(args.destination + '/prior_skill.csv'):
        prior_skill = proso.geography.user.prior_skill(data, difficulty)
        proso.geography.user.prior_skill_to_csv(
            prior_skill, args.destination + '/prior_skill.csv')
    else:
        prior_skill = proso.geography.user.csv_to_prior_skill(
            args.destination + '/prior_skill.csv')

    if not args.group or args.group == 'time':
        fig = plt.figure()
        graph.plot_answers_per_day(fig, data)
        fig.suptitle('Average number of answers per user')
        fig.savefig(args.destination + '/answers_per_day.' + args.output)
        fig = plt.figure()
        graph.plot_success_per_week(fig, data)
        fig.savefig(args.destination + '/success_per_week.' + args.output)
    if not args.group or args.group == 'session':
        fig = plt.figure()
        graph.plot_session_length(fig, data)
        fig.suptitle('Session length')
        fig.savefig(args.destination + '/session_length.' + args.output)
        fig = plt.figure()
        graph.plot_session_success(fig, data)
        fig.savefig(args.destination + '/session_success.' + args.outputi)
    if not args.group or args.group == 'recommendation':
        fig = plt.figure()
        graph.plot_stay_on_success(fig, data, prior_skill)
        fig.savefig(args.destination + '/stay_on_success.' + args.output)
    if not args.group or args.group == 'knowledge':
        fig = plt.figure()
        graph.plot_session_prior_skill(fig, data, difficulty)
        fig.savefig(args.destination + '/session_prior_skill.' + args.output)


if __name__ == "__main__":
    main()
