import matplotlib.pyplot as plt
import proso.geography.graph as graph
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
    parser.add_argument(
        '--split-maps',
        nargs='+',
        type=str,
        dest='split_maps')
    parser.add_argument(
        '--filter-abvalue',
        nargs='+',
        type=str,
        dest='filter_abvalue')
    parser.add_argument(
        '--buckets',
        type=int,
        help='create buckets for the given A/B testing values')
    return parser


def load_answers_to_ab_testing(args):
    filename = 'geography.answer.ab_testing_' + '__'.join(args.interested_prefixes) + '_f_' + '__'.join(args.filter_abvalue if args.filter_abvalue else []) + '__' + analysis.data_hash(args)
    data = analysis.read_cache(args, filename, csv_parser=answer.from_csv)
    if data is not None:
        return data
    data, _ = analysis.load_answers(args, all_needed=False)
    data = abtesting.prepare_data(data, args.interested_prefixes)
    if args.filter_abvalue:
        data = answer.apply_filter(data, lambda d: all(map(lambda g: g in d['ab_values'], args.filter_abvalue)))
    analysis.write_cache(args, data, filename)
    return data


def map_graphs(args, data, feedback, prior_skill, mapping, prefix, filename_prefix, group_column):
    filename_prefix += str(group_column) + "_"
    if analysis.is_group(args, 'motivation'):
        fig = plt.figure()
        graph.boxplot_answers_per_user(fig, data, prior_skill, group_column, mapping, verbose=args.verbose)
        fig.suptitle('AB testing: number of answers per user')
        analysis.savefig(args, fig, filename_prefix + 'answers_per_user_boxplot', prefix=prefix, resize=2)

        fig = plt.figure()
        graph.hist_answers_per_user(fig, data, group_column, mapping, verbose=args.verbose)
        fig.suptitle('AB testing: number of answers per user')
        analysis.savefig(args, fig, filename_prefix + 'answers_per_user_hist', prefix=prefix)

        fig = plt.figure()
        graph.boxplot_maps_per_user(fig, data, group_column, mapping, verbose=args.verbose)
        fig.suptitle('AB testing: number of maps per user')
        analysis.savefig(args, fig, filename_prefix + 'maps_per_user_boxplot', prefix=prefix)

        fig = plt.figure()
        graph.hist_maps_per_user(fig, data, group_column, mapping, verbose=args.verbose)
        fig.suptitle('AB testing: number of maps per user')
        analysis.savefig(args, fig, filename_prefix + 'maps_per_user_hist', prefix=prefix)

        fig = plt.figure()
        data = decorator.session_number(data)
        graph.boxplot_answers_per_user(fig,
            data[data['session_number'] == 0], prior_skill, group_column, mapping, verbose=args.verbose)
        fig.suptitle('AB testing: number of answers per user (only the first session)')
        analysis.savefig(args, fig, filename_prefix + 'answers_per_user_session_0_boxplot', prefix=prefix, resize=2)

        fig = plt.figure()
        graph.hist_answers_per_user(fig,
            data[data['session_number'] == 0], group_column, mapping, verbose=args.verbose)
        fig.suptitle('AB testing: number of answers per user (only the first session)')
        analysis.savefig(args, fig, filename_prefix + 'answers_per_user_session_0_hist', prefix=prefix)

        fig = plt.figure()
        graph.boxplot_success_per_user(fig, data, group_column, mapping, verbose=args.verbose)
        fig.suptitle('AB testing: mean success rate')
        analysis.savefig(args, fig, filename_prefix + 'success_per_user', prefix=prefix)

        if feedback is not None:
            fig = plt.figure()
            graph.plot_feedback_by_group(fig, data, feedback, prior_skill, group_column, mapping, verbose=args.verbose)
            fig.suptitle('AB testing: feedback per group')
            analysis.savefig(args, fig, filename_prefix + 'feedback_per_group', prefix=prefix, resize=2)
        print "Group [motivation] processed"
    else:
        print "Group [motivation] skipped"

    if analysis.is_group(args, 'progress'):
        fig = plt.figure()
        graph.plot_user_ratio(fig, data, group_column, mapping, session_numbers=[1, 2], verbose=args.verbose)
        fig.suptitle('AB testing: Users with at least the given number of sessions')
        analysis.savefig(args, fig, filename_prefix + 'users_with_n_sessions', prefix=prefix)

        fig = plt.figure()
        graph.plot_user_ratio(fig, data, group_column, mapping, answer_numbers_min=[20, 30, 50], verbose=args.verbose)
        fig.suptitle('AB testing: Users with at least the given number of answers')
        analysis.savefig(args, fig, filename_prefix + 'users_with_n_answers', prefix=prefix)
        print "Group [progress] processed"
    else:
        print "Group [progress] skipped"

    if analysis.is_group(args, 'difference'):
        fig = plt.figure()
        graph.boxplot_prior_skill(fig, data, prior_skill, group_column, mapping, verbose=args.verbose)
        fig.suptitle('AB testing: Prior skill')
        analysis.savefig(args, fig, filename_prefix + 'prior_skill', prefix=prefix)

        print "Group [difference] processed"
    else:
        print "Group [difference] skipped"

    if analysis.is_group(args, 'text'):
        filename = analysis.get_destination(args, prefix) + '/' + filename_prefix + 'output.txt'
        with open(filename, 'w') as f:
            textstats.answers_per_user(f, data, group_column, mapping)
            textstats.answers_per_user_pvalues(f, data, group_column, mapping)
            textstats.user_ratio(f, data, group_column, mapping)
        print 'Saving', filename
        print "Group [text] processed"
    else:
        print "Group [text] skipped"


def main():
    parser = load_parser()
    args = parser.parse_args()

    prefix = '__'.join(sorted(args.interested_prefixes)) + '_'

    data = load_answers_to_ab_testing(args)
    data, mapping = decorator.ab_group(data, args.interested_prefixes)
    if args.buckets:
        data, mapping = abtesting.bucketing(data, 'ab_group', mapping, args.buckets)
    feedback = analysis.load_feedback(args, data)
    if analysis.is_any_group(args, ['motivation']):
        difficulty, prior_skill = analysis.load_difficulty_and_prior_skill(args, None)
        if difficulty is None:
            _, data_all = analysis.load_answers(args, all_needed=True)
            print 'Answers loaded (again)'
            difficulty, prior_skill = analysis.load_difficulty_and_prior_skill(args, data_all)
            data_all = None
        print 'Difficulty loaded'
    else:
        difficulty, prior_skill = None, None
    if args.interested_prefixes == ['recommendation_target_prob_adjustment_']:
        mapping['ab_group'] = 'Is target probability adjustment enabled?'
    elif args.interested_prefixes == ['recommendation_target_prob_']:
        mapping['ab_group'] = 'Target probability'
    elif sorted(args.interested_prefixes) == ['recommendation_by_', 'recommendation_options_']:
        revert_mapping = dict(map(lambda (x, y): (y, x), mapping.items()))
        mapping['ab_group'] = 'Recommendation algorithm'
        mapping[revert_mapping['additive_function__naive']] = 'score, naive'
        mapping[revert_mapping['additive_function__random']] = 'score, random'
        mapping[revert_mapping['random__naive']] = 'random, naive'
        mapping[revert_mapping['random__random']] = 'random, random'

    if len(data) == 0:
        print "There are no answers to analyze"
        return
    if args.split_maps:
        for map_name, map_data in data.groupby(args.split_maps):
            map_prefix = (map_name if isinstance(map_name, str) else '_'.join(map_name)) + '__'
            print "# Processing AB group"
            map_graphs(
                args, map_data, feedback, prior_skill, mapping, prefix,
                map_prefix,
                'ab_group')
    else:
        print "# Processing AB group"
        map_graphs(args, data, feedback, prior_skill, mapping, prefix, '', 'ab_group')


if __name__ == "__main__":
    main()
