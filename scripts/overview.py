from argparse import ArgumentParser
from os import path, makedirs
import matplotlib.pyplot as plt
import proso.geography.answers as answer
import proso.geography.decorator as decorator
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
    return parser


def main():
    args = get_parser().parse_args()
    if not path.exists(args.destination):
        makedirs(args.destination)
    data = answer.from_csv(args.answers)
    fig = plt.figure()
    graph.plot_answers_per_day(fig, data)
    fig.suptitle('Average number of answers per user')
    fig.savefig(args.destination + '/answers_per_day.svg')
    fig = plt.figure()
    graph.plot_session_length(fig, data)
    fig.suptitle('Session length')
    fig.savefig(args.destination + '/session_length')


if __name__ == "__main__":
    main()
