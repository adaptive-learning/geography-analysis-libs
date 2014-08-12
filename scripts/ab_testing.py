from os import path
import matplotlib.pyplot as plt
import proso.geography.graph as graph
import proso.geography.user as user
import proso.geography.analysis as analysis
import proso.geography.answers as answer
import proso.geography.decorator as decorator
import proso.geography.abtesting as abtesting


def load_parser():
    parser = analysis.parser_init(required=['--ab-values', '--answer-ab-values'])
    parser = analysis.parser_group(parser, ['time', 'session', 'recommendation', 'knowledge'])
    parser.add_argument(
        '--interested-prefixes',
        nargs='+',
        dest='interested_prefixes',
        type=str,
        required=True,
        help='prefixes of A/B values which are used for analysis')
    return parser


def load_answers_to_ab_testing(args):
    filename = args.destination + '/geography.answer.ab_testing_' + '__'.join(args.interested_prefixes) + '.csv'
    if path.exists(filename):
        return answer.from_csv(filename)
    else:
        data_all = analysis.load_answers(args)
        data = abtesting.prepare_data(data_all, args.interested_prefixes)
        data.to_csv(filename, index=False)
        return data


def main():
    parser = load_parser()
    args = parser.parse_args()
    data = load_answers_to_ab_testing(args)
    data, mapping = decorator.ab_group(data, args.interested_prefixes)

    fig = plt.figure()
    graph.boxplot_answers_per_user(fig, data, 'ab_group', mapping)
    fig.suptitle('AB testing: number of answers per user')
    analysis.savefig(args, fig, 'answers_per_user_boxplot')

    fig = plt.figure()
    graph.hist_answers_per_user(fig, data, 'ab_group', mapping)
    fig.suptitle('AB testing: number of answers per user')
    analysis.savefig(args, fig, 'answers_per_user_hist')

    fig = plt.figure()
    data = decorator.session_number(data)
    graph.boxplot_answers_per_user(fig,
        data[data['session_number'] == 0], 'ab_group', mapping)
    fig.suptitle('AB testing: number of answers per user (only the first session)')
    analysis.savefig(args, fig, 'answers_per_user_session_0_boxplot')

    fig = plt.figure()
    graph.hist_answers_per_user(fig,
        data[data['session_number'] == 0], 'ab_group', mapping)
    fig.suptitle('AB testing: number of answers per user (only the first session)')
    analysis.savefig(args, fig, 'answers_per_user_session_0_hist')

    fig = plt.figure()
    graph.boxplot_success_per_user(fig, data, 'ab_group', mapping)
    fig.suptitle('AB testing: mean success rate')
    analysis.savefig(args, fig, 'success_per_user')

    if all(map(lambda x: not isinstance(x, str) or x.isdigit(), mapping.values())):
        print map(type, mapping.values())
        fig = plt.figure()
        graph.plot_user_ratio(fig, data, 'ab_group', mapping, session_numbers=[2, 3, 4])
        fig.suptitle('AB testing: Users with at least the given number of sessions')
        analysis.savefig(args, fig, 'users_with_2_sessions')

        fig = plt.figure()
        graph.plot_user_ratio(fig, data, 'ab_group', mapping, answer_numbers_min=[20, 50, 100])
        fig.suptitle('AB testing: Users with at least the given number of answers')
        analysis.savefig(args, fig, 'users_with_100_answers')


if __name__ == "__main__":
    main()
