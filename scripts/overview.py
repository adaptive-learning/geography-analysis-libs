import matplotlib.pyplot as plt
import proso.geography.graph as graph
import proso.geography.user as user
import proso.geography.analysis as analysis


def main():
    parser = analysis.parser_init()
    parser = analysis.parser_group(parser,
        ['time', 'session', 'recommendation', 'knowledge', 'motivation'])
    args = parser.parse_args()
    data = analysis.load_answers(args)
    if analysis.is_any_group(args, ['recommendation', 'knowledge', 'motivation']):
        difficulty = analysis.load_difficulty(args, data)
    if analysis.is_any_group(args, ['recommendation', 'motivation']):
        prior_skill = analysis.load_prior_skill(args, data, difficulty)
    if analysis.is_group(args, 'time'):
        fig = plt.figure()
        graph.plot_answers_per_week(fig, data)
        fig.suptitle('Average number of answers per user')
        analysis.savefig(args, fig, 'answers_per_week')
        fig = plt.figure()
        graph.plot_success_per_week(fig, data)
        analysis.savefig(args, fig, 'success_per_week')
    if analysis.is_group(args, 'session'):
        fig = plt.figure()
        graph.plot_session_length(fig, data)
        fig.suptitle('Session length')
        analysis.savefig(args, fig, 'session_length')
        fig = plt.figure()
        graph.plot_session_success(fig, data)
        analysis.savefig(args, fig, 'session_success')
    if analysis.is_group(args, 'recommendation'):
        fig = plt.figure()
        graph.hist_rolling_success(fig, data, prior_skill)
        analysis.savefig(args, fig, 'rolling_success_hist')
        fig = plt.figure()
        graph.plot_stay_on_rolling_success(fig, data, prior_skill)
        analysis.savefig(args, fig, 'stay_on_rolling_success')
    if analysis.is_group(args, 'knowledge'):
        fig = plt.figure()
        graph.plot_session_prior_skill(fig, data, difficulty)
        analysis.savefig(args, fig, 'session_prior_skill')
    if analysis.is_group(args, 'motivation'):
        fig = plt.figure()
        graph.plot_first_session_vs_total(fig, data)
        analysis.savefig(args, fig, 'first_session_vs_total')
        fig = plt.figure()
        graph.plot_first_session_vs_session_number(fig, data)
        analysis.savefig(args, fig, 'first_session_vs_session')
        fig = plt.figure()
        graph.plot_answers_vs_prior_skill(fig, data, prior_skill)
        analysis.savefig(args, fig, 'answers_vs_prior_skill')


if __name__ == "__main__":
    main()
