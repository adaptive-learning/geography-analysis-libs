import session
import decorator
import user
import overtime
import success
import textstats
import numpy
import scipy.stats
import math
import matplotlib.pyplot as plt

FEEDBACK_MAPPING = {
    1: 'Easy',
    2: 'Medium',
    3: 'Hard'
}


def boxplot_prior_skill(figure, answers, prior_skill, group_column, group_name_mapping=None, verbose=False):
    ax = figure.add_subplot(111)
    to_plot = []
    group_names = []
    for group_name, group_data in answers.groupby(group_column):
        users = group_data['user'].unique()
        to_plot.append(map(lambda u: prior_skill[u], users))
        group_names.append(group_name_mapping[group_name] if group_name_mapping else group_name)
    ax.set_ylabel('Prior Skill')
    _boxplot(ax, to_plot, group_names, name='Prior Skill', verbose=verbose)
    figure.tight_layout()


def boxplot_feedback_vs_number_of_answers(figure, feedback, answers, verbose=False):
    ax = figure.add_subplot(111)
    first_feedback = (feedback.sort('id').
        drop_duplicates('user').
        groupby('user').
        apply(lambda x: x['value'].mean()).to_dict())
    labels = []
    to_plot = []
    answers = answers[answers['user'].isin(first_feedback.keys())]
    answers['temp_group'] = answers['user'].apply(lambda u: first_feedback[u])
    for group_name, group_data in answers.groupby('temp_group'):
        number = user.answers_per_user(group_data)
        to_plot.append(number.values())
        labels.append('%s (%s)' % (FEEDBACK_MAPPING[group_name], len(number)))
    del answers['temp_group']
    ax.set_yscale('log')
    ax.set_ylabel('Number of Answers')
    ax.set_xlabel('First Feedback')
    _boxplot(ax, to_plot, labels, name='Feedback vs Number of Answers', verbose=verbose)
    figure.tight_layout()


def plot_feedback_by_success(figure, feedback, answers, prior_skill, verbose=False):
    feedback = decorator.success_before(feedback, answers)
    ax = figure.add_subplot(111)
    labels = []
    easy = []
    medium = []
    hard = []
    for group_name, group_data in feedback.groupby('success_before'):
        if len(group_data) <= 50:
            continue
        labels.append(group_name)
        ratios = group_data.groupby('value').apply(
            lambda g: float(len(g)) / len(group_data)).to_dict()
        easy.append(ratios.get(1, 0))
        medium.append(ratios.get(2, 0))
        hard.append(ratios.get(3, 0))
    _plot(ax, labels, ['Easy', 'Medium', 'Hard'], True, easy, medium, hard)
    ax.set_xlabel("User's Success before Rating (%)")
    ax.set_ylabel("Feedback Ratio")
    ax.set_ylim(0.0, 1.0)
    ax.set_title("Explicit Feedback")
    figure.tight_layout()


def plot_feedback_by_group(figure, answers, feedback, prior_skill, group_column, group_name_mapping=None, verbose=False):
    ax = figure.add_subplot(111)
    group_names = []
    easy = []
    medium = []
    hard = []
    for group_name, group_data in answers.groupby(group_column):
        users = group_data['user'].unique()
        values = feedback[feedback['user'].isin(users)]
        ratios = values.groupby('value').apply(lambda g: float(len(g)) / len(values)).to_dict()
        easy.append(ratios.get(1, 0))
        medium.append(ratios.get(2, 0))
        hard.append(ratios.get(3, 0))
        group_names.append(group_name_mapping[group_name] if group_name_mapping else group_name)
    _plot(ax, group_names, ['Easy', 'Medium', 'Hard'], True, easy, medium, hard)
    ax.set_xlabel(group_column if not group_name_mapping else group_name_mapping.get(group_column, group_column))
    ax.set_ylabel('Feedback Ratio')
    ax.set_ylim(0.0, 1.0)
    ax.set_title('Explicit Feedback')
    figure.tight_layout()


def plot_maps_success_vs_number_of_answers(figure, answers, verbose=False):
    groups = answers.groupby(['place_map_code', 'place_asked_type']).apply(lambda d: (sum(d['place_asked'] == d['place_answered']), len(d))).to_dict()
    ax = figure.add_subplot(111)
    for (map_code, place_type), (correct, number) in groups.iteritems():
        success = float(correct) / number
        ax.plot(number, success, 'o', color='black')
        ax.annotate("%s: %s" % (map_code, place_type), (number, success))
    ax.set_xlabel("Total Number of Answers")
    ax.set_xscale('log')
    ax.set_ylabel("Success")


def plot_answers_vs_prior_skill(figure, answers, prior_skill, verbose=False):
    answers = decorator.session_number(answers)
    ax = figure.add_subplot(111)
    total = user.answers_per_user(answers)
    users = answers['user'].unique()
    vals = lambda x: [x[i] for i in users]
    total, prior_skill = zip(*sorted(zip(vals(total), vals(prior_skill))))
    ax.plot(total, prior_skill, 'o', alpha=0.3, linewidth=0, color='black')
    ax.set_xlabel('number of answer at all')
    ax.set_ylabel('prior skill')
    ax.set_xscale('log')


def plot_first_session_vs_total(figure, answers, verbose=False):
    answers = decorator.session_number(answers)
    ax = figure.add_subplot(111)
    total = user.answers_per_user(answers)
    total_first = user.answers_per_user(answers[answers['session_number'] == 0])
    users = answers['user'].unique()
    vals = lambda x: [x.get(i, 0) for i in users]
    pairs = map(lambda (x, y): (x, y - x), sorted(zip(vals(total_first), vals(total))))
    total_first, total = zip(*pairs)
    ax.plot(total_first, total, 'o', alpha=0.3, linewidth=0, color='black')
    ax.set_xlabel('number of answers in the first session')
    ax.set_ylabel('number of answer at all')
    ax.set_xscale('log')
    ax.set_yscale('log')


def plot_first_session_vs_session_number(figure, answers, verbose=False):
    answers = decorator.session_number(answers)
    ax = figure.add_subplot(111)
    ses = user.session_per_user(answers)
    total_first = user.answers_per_user(answers[answers['session_number'] == 0])
    users = answers['user'].unique()
    vals = lambda x: [x.get(i, 0) for i in users]
    total_first, ses = zip(*sorted(zip(vals(total_first), vals(ses))))
    ax.plot(total_first, ses, 'o', alpha=0.3, linewidth=0, color='black')
    ax.set_xlabel('number of answers in the first session')
    ax.set_ylabel('maximal session number')
    ax.set_xscale('log')


def plot_user_ratio(figure, answers, group_column, group_name_mapping=None, answer_numbers_min=None, session_numbers=None, verbose=False):
    ax = figure.add_subplot(111)
    group_names = []
    to_plots = []
    labels = None
    for group_name, group_data in answers.groupby(group_column):
        to_plot = []
        current_labels = []
        if answer_numbers_min is not None:
            for num in answer_numbers_min:
                filtered_users, all_users = user.user_ratio(group_data, answer_number_min=num)
                to_plot.append(filtered_users / float(all_users))
                current_labels.append(str(num) + ' answers')
        else:
            for num in session_numbers:
                filtered_users, all_users = user.user_ratio(
                    group_data,
                    session_number=num)
                to_plot.append(filtered_users / float(all_users))
                current_labels.append(str(num + 1) + ' sessions')
        labels = current_labels
        to_plots.append(to_plot)
        group_names.append(group_name_mapping[group_name] if group_name_mapping else group_name)
    to_plots = map(list, zip(*to_plots))
    _plot(ax, group_names, labels, True, *to_plots)
    ax.set_xlabel(group_column if not group_name_mapping else group_name_mapping.get(group_column, group_column))
    ax.set_ylabel('Ratio of Users')


def boxplot_time_gap(figure, answers, group_column, group_name_mapping=None, verbose=False):
    ax = figure.add_subplot(111)
    labels = []
    to_plot = []
    for group_name, group_data in answers.groupby(group_column):
        gaps = filter(
            numpy.isfinite,
            numpy.log([g for gs in overtime.time_gap(group_data).values() for g in gs]))
        to_plot.append(gaps)
        labels.append(
            str(group_name_mapping[group_name] if group_name_mapping else group_name) + '\n(' + str(len(gaps)) + ')')
    ax.set_xlabel(group_column)
    ax.set_ylabel('time gap (seconds, log)')
    _boxplot(ax, to_plot, labels, name='Time Gap', verbose=verbose)


def boxplot_number_of_options(figure, answers, group_column, group_name_mapping=None, verbose=False):
    ax = figure.add_subplot(111)
    labels = []
    to_plot = []
    for group_name, group_data in answers.groupby(group_column):
        opts = group_data['options'].map(lambda options: len(options))
        to_plot.append(opts)
        labels.append(
            str(group_name_mapping[group_name] if group_name_mapping else group_name) + '\n(' + str(len(opts)) + ')')
    _boxplot(ax, to_plot, labels, name='Number of Options', verbose=verbose)


def boxplot_maps_per_user(figure, answers, group_column, group_name_mapping=None, verbose=False):
    ax = figure.add_subplot(111)
    labels = []
    to_plot = []
    for group_name, group_data in answers.groupby(group_column):
        m = user.maps_per_user(group_data).values()
        to_plot.append(m)
        labels.append(
            str(group_name_mapping[group_name] if group_name_mapping else group_name) + '\n(' + str(len(m)) + ')')
    _boxplot(ax, to_plot, labels, name='Number of Maps per User', verbose=verbose)


def boxplot_success_per_user(figure, answers, group_column, group_name_mapping=None, verbose=False):
    ax = figure.add_subplot(111)
    labels = []
    to_plot = []
    for group_name, group_data in answers.groupby(group_column):
        s = success.success_per_user(group_data).values()
        to_plot.append(s)
        labels.append(
            str(group_name_mapping[group_name] if group_name_mapping else group_name) + '\n(' + str(len(s)) + ')')
    _boxplot(ax, to_plot, labels, name='Success per User', verbose=verbose)


def boxplot_answers_per_user(figure, answers, prior_skill, group_column, group_name_mapping=None, verbose=False):
    ax = figure.add_subplot(111)
    labels = []
    to_plot = []
    for group_name, group_data in answers.groupby(group_column):
        number = user.answers_per_user(group_data)
        to_plot.append(number.values())
        labels.append(
            str(group_name_mapping[group_name] if group_name_mapping else group_name) + '\n(' + str(len(number)) + ')')
    ax.set_yscale('log')
    ax.set_xlabel(group_name_mapping.get(group_column, group_column) if group_name_mapping else group_column)
    ax.set_ylabel('Number of Answers')
    ax.set_title('Implicit Feedback')
    _boxplot(ax, to_plot, labels, name='Answers per User', verbose=verbose)
    figure.tight_layout()


def hist_answers_per_place_user(figure, answers, group_column, group_name_mapping=None, verbose=False):
    ax = figure.add_subplot(111)
    to_plots = []
    group_names = []
    for group_name, group_data in answers.groupby(group_column):
        to_plots.append(numpy.log10(user.answers_pers_place_user(group_data)))
        group_names.append(group_name)
    if group_name_mapping:
        group_names = [group_name_mapping[group_name] for group_name in group_names]
    else:
        group_names = map(str, group_names)
    group_names, to_plots = zip(*sorted(zip(group_names, to_plots)))
    ax.hist(
        to_plots,
        label=[group_name + ' (' + str(len(to_plot)) + ')' for group_name, to_plot in zip(group_names, to_plots)],
        normed=True,
        )
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.set_xlabel("Number of Answers per Place (log)")
    ax.set_ylabel("Number of Users (normed)")
    figure.tight_layout()


def hist_maps_per_user(figure, answers, group_column, group_name_mapping=None, verbose=False):
    ax = figure.add_subplot(111)
    to_plots = []
    group_names = []
    for group_name, group_data in answers.groupby(group_column):
        to_plots.append(user.maps_per_user(group_data).values())
        group_names.append(group_name)
    if group_name_mapping:
        group_names = [group_name_mapping[group_name] for group_name in group_names]
    else:
        group_names = map(str, group_names)
    group_names, to_plots = zip(*sorted(zip(group_names, to_plots)))
    ax.hist(
        to_plots,
        label=[group_name + ' (' + str(len(to_plot)) + ')' for group_name, to_plot in zip(group_names, to_plots)],
        normed=True,
        )
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.set_xlabel("Number of Maps")
    ax.set_ylabel("Number of Users (normed)")
    figure.tight_layout()


def hist_answers_per_user(figure, answers, group_column, group_name_mapping=None, verbose=False):
    ax = figure.add_subplot(111)
    to_plots = []
    group_names = []
    for group_name, group_data in answers.groupby(group_column):
        to_plots.append(numpy.log10(user.answers_per_user(group_data).values()))
        group_names.append(group_name)
    if group_name_mapping:
        group_names = [group_name_mapping[group_name] for group_name in group_names]
    else:
        group_names = map(str, group_names)
    group_names, to_plots = zip(*sorted(zip(group_names, to_plots), key=lambda x: x[0]))
    ax.hist(
        to_plots,
        label=[group_name + ' (' + str(len(to_plot)) + ')' for group_name, to_plot in zip(group_names, to_plots)],
        normed=True,
        )
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.set_xlabel("Number of Answers (log)")
    ax.set_ylabel("Number of Users (normed)")
    figure.tight_layout()


def hist_rolling_success(figure, answers, prior_skill, verbose=False):
    [answers_low, answers_medium, answers_high] = _split_data_by_skill(
        answers, prior_skill, [25, 75])
    ax = figure.add_subplot(111)
    ax.hist(
        [
            zip(*success.rolling_success_per_user(answers_low).values())[0],
            zip(*success.rolling_success_per_user(answers_medium).values())[0],
            zip(*success.rolling_success_per_user(answers_high).values())[0]
        ],
        label=['Users with Low Skill', 'Users with Medium Skill', 'Users with High Skill'],
        bins=10,
        normed=True)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    figure.tight_layout()


def boxplot_success_diff(figure, answers, group_column, session_number_first, session_number_second, verbose=False):
    ax = figure.add_subplot(111)
    labels = []
    to_plot = []
    for group_name, group_data in answers.groupby(group_column):
        diffs = session.session_success_diffs(
            group_data,
            session_number_first,
            session_number_second)
        to_plot.append(diffs)
        labels.append(group_name + '\n(' + str(len(diffs)) + ')')
    _boxplot(ax, to_plot, labels, name='Success Difference', verbose=verbose)
    ax.set_xlabel(group_column)
    ax.set_ylabel('relative success difference')


def boxplot_prior_skill_diff(figure, answers, difficulty, group_column, session_number_first, session_number_second, verbose=False):
    ax = figure.add_subplot(111)
    labels = []
    to_plot = []
    for group_name, group_data in answers.groupby(group_column):
        diffs = session.session_prior_skill_diffs(
            group_data,
            difficulty,
            session_number_first,
            session_number_second)
        to_plot.append(diffs)
        labels.append(group_name + '\n(' + str(len(diffs)) + ')')
    _boxplot(ax, to_plot, labels, name='Prior Skill Difference', verbose=verbose)
    ax.set_yscale('log')
    ax.set_xlabel(group_column)
    ax.set_ylabel('relative difference between prior skills')


def plot_answers_per_week(figure, answers, verbose=False):
    ax1 = figure.add_subplot(111)
    to_plot = sorted(overtime.answers_per_week(answers).items())
    xs = range(len(to_plot))
    ax1.plot(xs, zip(*to_plot)[1], 'b-o')
    ax1.set_xlabel('week from project start')
    ax1.set_ylabel('average number of answers per user', color='b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    to_plot = sorted(overtime.users_per_week(answers).items())
    xs = range(len(to_plot))
    ax2 = ax1.twinx()
    ax2.set_ylabel('number of users', color='r')
    ax2.plot(xs, zip(*to_plot)[1], 'r-v', linewidth=1)
    for tl in ax2.get_yticklabels():
        tl.set_color('r')


def plot_stay_on_rolling_success(figure, answers, prior_skill, verbose=False):
    [answers_low, answers_medium, answers_high] = _split_data_by_skill(
        answers, prior_skill, [25, 75])
    stay_all = sorted(success.stay_on_rolling_success(answers).items())
    stay_low = sorted(success.stay_on_rolling_success(answers_low).items())
    stay_medium = sorted(success.stay_on_rolling_success(answers_medium).items())
    stay_high = sorted(success.stay_on_rolling_success(answers_high).items())
    to_plot = {
        'All Users': stay_all,
        'Users with Low Skill': stay_low,
        'Users with Medium Skill': stay_medium,
        'Users with High Skill': stay_high
    }
    i = 1
    for title, data in to_plot.items():
        _to_errorbar = map(lambda (rolling_success, (m, std, _n)): (rolling_success, (m, std)), data)
        _samples_num = map(lambda (rolling_success, (_m, _std, n)): (rolling_success, n), data)
        ax1 = figure.add_subplot(2, 2, i)
        _plot_errorbar(ax1, _to_errorbar)
        ax1.set_title(title)
        ax1.set_xlabel('rolling success rate (last 10 answers)')
        ax1.set_ylabel('probability of staying')
        ax1.set_ylim(0, 1.0)
        ax2 = ax1.twinx()
        ax2.set_yscale('log')
        ax2.set_ylabel('number of samples')
        ax2.plot(
            zip(*_samples_num)[0],
            zip(*_samples_num)[1],
            'r:')
        for tl in ax2.get_yticklabels():
            tl.set_color('r')
        i += 1
    figure.tight_layout()


def plot_session_length(figure, answers, portion_min=0.01, verbose=False):
    if 'session_number' in answers:
        data = answers
    else:
        data = decorator.session_number(answers)
    session_limit = max([session_number if portion >= portion_min else 0
        for session_number, portion in session.session_user_portion(answers).items()])
    data = data[data['session_number'] <= session_limit]

    length = session.session_length(data).items()
    ax1 = figure.add_subplot(111)
    ax1.plot(zip(*length)[0], zip(*length)[1], 'b-')
    ax1.set_xlabel('session number')
    ax1.set_ylabel('session length', color='b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    users_for_limit = data[data['session_number'] == session_limit]['user'].values
    data_for_limit = data[data['user'].isin(users_for_limit)]
    data_for_limit = data_for_limit[data_for_limit['session_number'] <= session_limit]
    for_limit_length = session.session_length(data_for_limit)
    ax1.plot(
        zip(*for_limit_length.items())[0],
        zip(*for_limit_length.items())[1], 'b--')

    hist = session.session_users(data).items()
    ax2 = ax1.twinx()
    ax2.set_yscale('log')
    ax2.set_ylabel('number of users', color='r')
    ax2.plot(zip(*hist)[0], zip(*hist)[1], 'r-.', linewidth=2)
    for tl in ax2.get_yticklabels():
        tl.set_color('r')


def plot_session_prior_skill(figure, answers, difficulty, portion_min=0.01, verbose=False):
    if 'session_number' in answers:
        data = answers
    else:
        data = decorator.session_number(answers)
    session_limit = max([session_number if portion >= portion_min else 0
        for session_number, portion in session.session_user_portion(answers).items()])
    data = data[data['session_number'] <= session_limit]

    prior_skill = session.session_prior_skill(data, difficulty).items()
    hist = session.session_users(data).items()
    ax1 = figure.add_subplot(111)
    ax1.plot(zip(*prior_skill)[0], zip(*prior_skill)[1], 'b-')
    ax1.set_xlabel('session number')
    ax1.set_ylabel('average prior skill', color='b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    ax2 = ax1.twinx()
    ax2.set_yscale('log')
    ax2.set_ylabel('number of users', color='r')
    ax2.plot(zip(*hist)[0], zip(*hist)[1], 'r-.', linewidth=2)
    for tl in ax2.get_yticklabels():
        tl.set_color('r')


def plot_session_success(figure, answers, portion_min=0.01, verbose=False):
    if 'session_number' in answers:
        data = answers
    else:
        data = decorator.session_number(answers)
    session_limit = max([session_number if portion >= portion_min else 0
        for session_number, portion in session.session_user_portion(answers).items()])
    data = data[data['session_number'] <= session_limit]

    success = session.session_success(data).items()
    hist = session.session_users(data).items()
    ax1 = figure.add_subplot(111)
    ax1.plot(zip(*success)[0], zip(*success)[1], 'b-')
    ax1.set_xlabel('session number')
    ax1.set_ylabel('success rate', color='b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    ax2 = ax1.twinx()
    ax2.set_yscale('log')
    ax2.set_ylabel('number of users', color='r')
    ax2.plot(zip(*hist)[0], zip(*hist)[1], 'r-.', linewidth=2)
    for tl in ax2.get_yticklabels():
        tl.set_color('r')


def plot_success_per_week(figure, answers, verbose=False):
    ax = figure.add_subplot(111)
    globally = sorted(overtime.success_per_week(answers).items())
    by_user = sorted(overtime.success_by_user_per_week(answers).items())
    xs = range(len(by_user))
    ax.plot(xs, zip(*globally)[1], 'b-o', label='mean success rate')
    ax.plot(xs, zip(*by_user)[1], 'r-v', label='mean success rate by user')
    ax.set_xlabel('week from project start')
    ax.set_ylabel('success rate')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))


def _plot(ax, labels, data_labels, show_legend, *args):
    markers = 'osvDdp'
    if data_labels is None:
        data_labels = [None for i in args]
    zipped = zip(*sorted(zip(labels, *args)))
    xs = range(len(labels))
    ax.set_xticks(xs)
    for i in range(1, len(zipped)):
        ax.plot(xs, zipped[i], '-%s' % markers[i - 1], label=data_labels[i - 1])
    ax.set_xticklabels(zipped[0])
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
    ax.set_axisbelow(True)
    for label in ax.get_xticklabels():
        label.set_rotation(10)
    if show_legend:
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))


def _boxplot(ax, to_plot, labels, name=None, verbose=False):
    if len(to_plot) == 2:
        tstat, pvalue = scipy.stats.ttest_ind(numpy.log(to_plot[0]), numpy.log(to_plot[1]))
        pvalue = str(int(100 * pvalue if not math.isnan(pvalue) else 0) / 100.0)
    means = []
    medians = []
    stds = []
    minimum = None
    for i in to_plot:
        means.append(numpy.mean(i))
        stds.append(numpy.std(i))
        medians.append(numpy.median(i))
        if len(i) == 0:
            continue
        if minimum is None:
            minimum = min(i)
        else:
            minimum = min(min(i), minimum)
    labels, to_plot, means, medians, stds = zip(*sorted(
        zip(labels, to_plot, means, medians, stds)))
    bp = ax.boxplot(to_plot, patch_artist=True, notch=True)
    plt.setp(bp['boxes'], color='black')
    plt.setp(bp['whiskers'], color='black')
    plt.setp(bp['fliers'], color='red', marker='+')
    for patch in bp['boxes']:
        patch.set_facecolor('royalblue')
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
    ax.set_axisbelow(True)
    for i, m in zip(range(len(means)), means):
        ax.plot(i + 1, m, 'o', color='black')
        ax.annotate(str(numpy.round(m, 2)), (i + 1 + min(max(len(to_plot) * 0.05, 0.5), 0.1), m))
    for i, m in zip(range(len(medians)), medians):
        ax.annotate(str(numpy.round(m, 2)), (i + 1 + min(max(len(to_plot) * 0.05, 0.5), 0.1), m))
    if len(to_plot) == 2 and minimum is not None:
        ax.text(
            1.5, (medians[0] - minimum) / 2.0 + minimum,
            'p-value: ' + str(pvalue),
            horizontalalignment='center', verticalalignment='center',
            fontweight='bold')
    ax.set_xticklabels(labels)
    for label in ax.get_xticklabels():
        label.set_rotation(10)
    if verbose:
        textstats.pvalues(to_plot, labels, name)


def _plot_errorbar(plt, data, **argw):
    """
        Args:
            plt (matplotlib.axes.Axes):
                handler for matplotlib
            data (dict):
                xs -> (mean, standar deviation)
    """
    plt.errorbar(
        zip(*data)[0],
        zip(*(zip(*data)[1]))[0],
        yerr=zip(*(zip(*data)[1]))[1],
        **argw)


def _split_data_by_skill(answers, prior_skill, percentiles):
    limits = numpy.percentile(prior_skill.values(), percentiles)
    result = []
    for minimum, maximum in zip([None] + limits, limits + [None]):
        result.append(answers[answers['user'].apply(
            lambda user: (minimum is None or prior_skill[user] > minimum) and (maximum is None or prior_skill[user] <= maximum))])
    return result
