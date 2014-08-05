import datetime
from os import path
import matplotlib.pyplot as plt
import proso.geography.graph as graph
import proso.geography.user as user
import proso.geography.analysis as analysis
import proso.geography.answers as answer
import proso.geography.decorator as decorator

CSRF_HOTFIX = datetime.datetime(year=2014, month=4, day=25, hour=23)


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
        data = answer.apply_filter(data_all, lambda d: d['inserted'] > CSRF_HOTFIX)
        data['interested_ab_values'] = (data['ab_values'].
            apply(lambda values: '__'.join(sorted([v for v in values if any([v.startswith(p) for p in args.interested_prefixes])]))))
        data = answer.apply_filter(data, lambda d: len([v for v in d['ab_values'] if any([v.startswith(p) for p in args.interested_prefixes])]) == len(args.interested_prefixes))
        data.to_csv(filename, index=False)
        return data


def decorete_ab_group(args, data):
    uniques = data['interested_ab_values'].unique()
    mapping = dict(zip(
        range(len(uniques)),
        map(lambda x: drop_prefixes(x, args.interested_prefixes), uniques)))
    mapping_reverse = dict(zip(
        uniques,
        range(len(uniques))))
    data['ab_group'] = data['interested_ab_values'].apply(lambda x: mapping_reverse[x])
    return data, mapping


def drop_prefixes(name, prefixes):
    for prefix in prefixes:
        name = name.replace(prefix, "")
    return name


def main():
    parser = load_parser()
    args = parser.parse_args()
    data = load_answers_to_ab_testing(args)
    data, mapping = decorete_ab_group(args, data)

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


if __name__ == "__main__":
    main()
