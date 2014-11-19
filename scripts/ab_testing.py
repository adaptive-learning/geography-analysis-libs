from os import path
import sys
import matplotlib.pyplot as plt
import proso.geography.graph as graph
import proso.geography.user as user
import proso.geography.analysis as analysis
import proso.geography.answers as answer
import proso.geography.decorator as decorator
import proso.geography.abtesting as abtesting
import proso.geography.textstats as textstats


def load_parser():
    parser = analysis.parser_init()
    parser = analysis.parser_group(parser, ['motivation', 'progress', 'text', 'difference'])
    parser.add_argument(
        '--interested-prefixes',
        nargs='+',
        dest='interested_prefixes',
        type=str,
        required=True,
        help='prefixes of A/B values which are used for analysis')
    return parser


def load_answers_to_ab_testing(args):
    filename = 'geography.answer.ab_testing_' + '__'.join(args.interested_prefixes) + '__' + analysis.data_hash(args)
    data = analysis.read_cache(args, filename, csv_parser=answer.from_csv)
    if data is not None:
        return data
    data, _ = analysis.load_answers(args, all_needed=False)
    data = abtesting.prepare_data(data, args.interested_prefixes)
    analysis.write_cache(args, data, filename)
    return data


def main():
    parser = load_parser()
    args = parser.parse_args()

    prefix = '__'.join(sorted(args.interested_prefixes)) + '_'

    data = load_answers_to_ab_testing(args)
    data, mapping = decorator.ab_group(data, args.interested_prefixes)

    if len(data) == 0:
        print "There are no answers to analyze"
        return

    if analysis.is_group(args, 'motivation'):
        fig = plt.figure()
        graph.boxplot_answers_per_user(fig, data, 'ab_group', mapping)
        fig.suptitle('AB testing: number of answers per user')
        analysis.savefig(args, fig, 'answers_per_user_boxplot', prefix=prefix)

        fig = plt.figure()
        graph.hist_answers_per_user(fig, data, 'ab_group', mapping)
        fig.suptitle('AB testing: number of answers per user')
        analysis.savefig(args, fig, 'answers_per_user_hist', prefix=prefix)

        fig = plt.figure()
        graph.boxplot_maps_per_user(fig, data, 'ab_group', mapping)
        fig.suptitle('AB testing: number of maps per user')
        analysis.savefig(args, fig, 'maps_per_user_boxplot', prefix=prefix)

        fig = plt.figure()
        graph.hist_maps_per_user(fig, data, 'ab_group', mapping)
        fig.suptitle('AB testing: number of maps per user')
        analysis.savefig(args, fig, 'maps_per_user_hist', prefix=prefix)

        fig = plt.figure()
        data = decorator.session_number(data)
        graph.boxplot_answers_per_user(fig,
            data[data['session_number'] == 0], 'ab_group', mapping)
        fig.suptitle('AB testing: number of answers per user (only the first session)')
        analysis.savefig(args, fig, 'answers_per_user_session_0_boxplot', prefix=prefix)

        fig = plt.figure()
        graph.hist_answers_per_user(fig,
            data[data['session_number'] == 0], 'ab_group', mapping)
        fig.suptitle('AB testing: number of answers per user (only the first session)')
        analysis.savefig(args, fig, 'answers_per_user_session_0_hist', prefix=prefix)

        fig = plt.figure()
        graph.boxplot_success_per_user(fig, data, 'ab_group', mapping)
        fig.suptitle('AB testing: mean success rate')
        analysis.savefig(args, fig, 'success_per_user', prefix=prefix)
        print "Group [motivation] processed"
    else:
        print "Group [motivation] skipped"

    if analysis.is_group(args, 'progress') and all(map(lambda x: not isinstance(x, str) or x.isdigit(), mapping.values())):
        fig = plt.figure()
        graph.plot_user_ratio(fig, data, 'ab_group', mapping, session_numbers=[1, 2])
        fig.suptitle('AB testing: Users with at least the given number of sessions')
        analysis.savefig(args, fig, 'users_with_n_sessions', prefix=prefix)

        fig = plt.figure()
        graph.plot_user_ratio(fig, data, 'ab_group', mapping, answer_numbers_min=[20, 30, 50])
        fig.suptitle('AB testing: Users with at least the given number of answers')
        analysis.savefig(args, fig, 'users_with_n_answers', prefix=prefix)
        print "Group [progress] processed"
    else:
        print "Group [progress] skipped"

    if analysis.is_group(args, 'difference'):
        fig = plt.figure()
        graph.boxplot_number_of_options(fig, data, 'ab_group', mapping)
        fig.suptitle('AB testing: Number of options')
        analysis.savefig(args, fig, 'number_of_options', prefix=prefix)

        fig = plt.figure()
        graph.boxplot_time_gap(fig, data, 'ab_group', mapping)
        fig.suptitle('AB testing: Average Time Gap per User')
        analysis.savefig(args, fig, 'time_gap', prefix=prefix)

        fig = plt.figure()
        graph.hist_answers_per_place_user(fig, data, 'ab_group', mapping)
        fig.suptitle('AB testing: Number of Answer per Place and User')
        analysis.savefig(args, fig, 'answers_per_place_user', prefix=prefix)
        print "Group [difference] processed"
    else:
        print "Group [difference] skipped"

    if analysis.is_group(args, 'text'):
        with open(analysis.get_destination(args, prefix) + '/output.txt', 'w') as f:
            textstats.answers_per_user(f, data, 'ab_group', mapping)
            textstats.answers_per_user_pvalues(f, data, 'ab_group', mapping)
            textstats.user_ratio(f, data, 'ab_group', mapping)
        print "Group [text] processed"
    else:
        print "Group [text] skipped"


if __name__ == "__main__":
    main()
