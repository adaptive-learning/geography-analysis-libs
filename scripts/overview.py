import matplotlib.pyplot as plt
import proso.geography.graph as graph
import proso.geography.user as user
import proso.geography.analysis as analysis
import gc


def main():
    parser = analysis.parser_init()
    parser = analysis.parser_group(parser,
        ['time', 'session', 'recommendation', 'knowledge', 'motivation'])
    args = parser.parse_args()
    data, data_all = analysis.load_answers(args, all_needed=False)
    feedback = analysis.load_feedback(args, data)
    print 'Answers loaded'
    if analysis.is_any_group(args, ['recommendation', 'knowledge']):
        difficulty, prior_skill = analysis.load_difficulty_and_prior_skill(args, data_all)
        if difficulty is None:
            data, data_all = analysis.load_answers(args, all_needed=True)
            print 'Answers loaded (again)'
            difficulty, prior_skill = analysis.load_difficulty_and_prior_skill(args, data_all)
        print 'Difficulty loaded'
    data_all = None
    if analysis.is_group(args, 'time'):
        fig = plt.figure()
        graph.plot_answers_per_week(fig, data)
        fig.suptitle('Average number of answers per user')
        analysis.savefig(args, fig, 'answers_per_week')
        fig = plt.figure()
        graph.plot_success_per_week(fig, data)
        analysis.savefig(args, fig, 'success_per_week')
        print "Group [time] processed"
        gc.collect()
    else:
        print "Group [time] skipped"
    if analysis.is_group(args, 'session'):
        fig = plt.figure()
        graph.plot_session_length(fig, data)
        fig.suptitle('Session length')
        analysis.savefig(args, fig, 'session_length')
        fig = plt.figure()
        graph.plot_session_success(fig, data)
        analysis.savefig(args, fig, 'session_success')
        print "Group [session] processed"
        gc.collect()
    else:
        print "Group [session] skipped"
    if analysis.is_group(args, 'recommendation'):
        fig = plt.figure()
        graph.hist_rolling_success(fig, data, prior_skill)
        analysis.savefig(args, fig, 'rolling_success_hist')
        fig = plt.figure()
        graph.plot_stay_on_rolling_success(fig, data, prior_skill)
        analysis.savefig(args, fig, 'stay_on_rolling_success')
        print "Group [recommendation] processed"
        gc.collect()
    else:
        print "Group [recommendation] skipped"
    if analysis.is_group(args, 'knowledge'):
        fig = plt.figure()
        graph.plot_session_prior_skill(fig, data, difficulty)
        analysis.savefig(args, fig, 'session_prior_skill')
        print "Group [knowledge] processed"
        gc.collect()
    else:
        print "Group [knowledge] skipped"
    if analysis.is_group(args, 'motivation'):
        fig = plt.figure()
        graph.plot_maps_success_vs_number_of_answers(fig, data)
        analysis.savefig(args, fig, 'success_vs_number_of_answers')
        fig = plt.figure()
        graph.plot_first_session_vs_total(fig, data)
        analysis.savefig(args, fig, 'first_session_vs_total')
        fig = plt.figure()
        graph.plot_feedback_by_success(fig, feedback, data)
        analysis.savefig(args, fig, 'feedback_by_success')
        print "Group [motivation] processed"
        gc.collect()
    else:
        print "Group [motivation] skipped"


if __name__ == "__main__":
    main()
