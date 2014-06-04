import matplotlib.pyplot as plt
import proso.geography.graph as graph
import proso.geography.user as user
import proso.geography.analysis as analysis


def main():
    parser = analysis.parser_init()
    parser = analysis.parser_group(parser, ['time', 'session', 'recommendation', 'knowledge'])
    args = parser.parse_args()
    data = analysis.load_answers(args)
    if analysis.is_any_group(args, ['recommendation', 'knowledge']):
        difficulty = analysis.load_difficulty(args, data)
    if analysis.is_any_group(args, ['recommendation']):
        prior_skill = analysis.load_prior_skill(args, data, difficulty)
    if analysis.is_group(args, 'time'):
        fig = plt.figure()
        graph.plot_answers_per_week(fig, data)
        fig.suptitle('Average number of answers per user')
        fig.savefig(args.destination + '/answers_per_week.' + args.output)
        fig = plt.figure()
        graph.plot_success_per_week(fig, data)
        fig.savefig(args.destination + '/success_per_week.' + args.output)
    if analysis.is_group(args, 'session'):
        fig = plt.figure()
        graph.plot_session_length(fig, data)
        fig.suptitle('Session length')
        fig.savefig(args.destination + '/session_length.' + args.output)
        fig = plt.figure()
        graph.plot_session_success(fig, data)
        fig.savefig(args.destination + '/session_success.' + args.output)
    if analysis.is_group(args, 'recommendation'):
        fig = plt.figure()
        graph.plot_stay_on_rolling_success(fig, data, prior_skill)
        fig.savefig(args.destination + '/stay_on_success.' + args.output)
    if analysis.is_group(args, 'knowledge'):
        fig = plt.figure()
        graph.plot_session_prior_skill(fig, data, difficulty)
        fig.savefig(args.destination + '/session_prior_skill.' + args.output)


if __name__ == "__main__":
    main()
