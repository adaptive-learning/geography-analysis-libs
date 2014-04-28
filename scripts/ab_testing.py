from argparse import ArgumentParser
from os import path, makedirs
import matplotlib.pyplot as plt
import proso.geography.answers as answer
import proso.geography.graph as graph


def get_parser():
    parser = ArgumentParser()
    parser.add_argument(
        '-a',
        '--answers',
        metavar='FILE',
        required=True,
        help='path to the CSV with answers')
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
    return parser


def main():
    args = get_parser().parse_args()
    if not path.exists(args.destination):
        makedirs(args.destination)
    data = answer.from_csv(args.answers)
    data_ab_testing = data.dropna(subset=['ab_value'])
    if args.new_users_only:
        data_before_ab_testing = data[data['ab_value'].isnull()]
        data_ab_testing = data_ab_testing[
            ~data_ab_testing['user'].isin(data_before_ab_testing['user'].values)
        ]
    for ab_value, group_data in list(data_ab_testing.groupby('ab_value')):
        filename = 'session_length_' + ab_value + '.svg'
        fig = plt.figure()
        graph.plot_session_length(fig, group_data)
        fig.suptitle('AB testing: ' + ab_value)
        fig.savefig(args.destination + '/' + filename)
    fig = plt.figure()
    graph.boxplot_answers_per_user(fig, data_ab_testing, 'ab_value')
    fig.suptitle('AB testing: number of answers per user')
    fig.savefig(args.destination + '/answers_per_user.svg')


if __name__ == "__main__":
    main()
