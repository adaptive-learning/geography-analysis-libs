import session
import decorator
import user
import overtime
import success
import numpy
import scipy.stats


def boxplot_answers_per_user(figure, answers, group_column):
    ax = figure.add_subplot(111)
    labels = []
    to_plot = []
    for group_name, group_data in answers.groupby(group_column):
        number = user.answers_per_user(group_data)
        to_plot.append(number.values())
        labels.append(group_name + '\n(' + str(len(number)) + ')')
    if len(to_plot) == 2:
        tstat, pvalue = scipy.stats.ttest_ind(numpy.log(to_plot[0]), numpy.log(to_plot[1]))
        pvalue = str(int(100 * pvalue if pvalue else 0) / 100.0)
        figure.text(
            0.8, 0.8,
            'p-value: ' + str(pvalue),
            horizontalalignment='center', verticalalignment='baseline')
    ax.boxplot(to_plot)
    ax.set_yscale('log')
    ax.set_xticklabels(labels)
    ax.set_xlabel(group_column)
    ax.set_ylabel('number of answers')


def boxplot_success_diff(figure, answers, group_column, session_number_first, session_number_second):
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
    if len(to_plot) == 2:
        tstat, pvalue = scipy.stats.ttest_ind(to_plot[0], to_plot[1])
        pvalue = str(int(100 * pvalue if pvalue else 0) / 100.0)
        figure.text(
            0.8, 0.8,
            'p-value: ' + str(pvalue),
            horizontalalignment='center', verticalalignment='baseline')
    ax.boxplot(to_plot)
    ax.set_xticklabels(labels)
    ax.set_xlabel(group_column)
    ax.set_ylabel('relative success difference')


def boxplot_prior_skill_diff(figure, answers, difficulty, group_column, session_number_first, session_number_second):
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
    ax.boxplot(to_plot)
    ax.set_yscale('log')
    ax.set_xticklabels(labels)
    ax.set_xlabel(group_column)
    ax.set_ylabel('relative difference between prior skills')


def plot_answers_per_day(figure, answers):
    ax1 = figure.add_subplot(111)
    to_plot = sorted(overtime.answers_per_day(answers).items())
    ax1.plot(zip(*to_plot)[0], zip(*to_plot)[1], 'b-')
    ax1.set_xlabel('day')
    ax1.set_ylabel('average number of answers per user', color='b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    to_plot = sorted(overtime.users_per_day(answers).items())
    ax2 = ax1.twinx()
    ax2.set_ylabel('number of users', color='r')
    ax2.plot(zip(*to_plot)[0], zip(*to_plot)[1], 'r--', linewidth=1)
    for tl in ax2.get_yticklabels():
        tl.set_color('r')


def plot_stay_on_rolling_success(figure, answers, prior_skill):
    limits = numpy.percentile(prior_skill.values(), [25, 75])
    answers_low = answers[
        answers['user'].apply(lambda user: prior_skill[user] < limits[0])]
    answers_medium = answers[
        answers['user'].apply(
            lambda user: prior_skill[user] >= limits[0] and prior_skill[user] < limits[1])]
    answers_high = answers[
        answers['user'].apply(lambda user: prior_skill[user] >= limits[1])]
    stay_all = sorted(success.stay_on_rolling_success(answers).items())
    stay_low = sorted(success.stay_on_rolling_success(answers_low).items())
    stay_medium = sorted(success.stay_on_rolling_success(answers_medium).items())
    stay_high = sorted(success.stay_on_rolling_success(answers_high).items())
    ax = figure.add_subplot(111)
    ax.plot(zip(*stay_all)[0], zip(*stay_all)[1], label='all users')
    ax.plot(zip(*stay_low)[0], zip(*stay_low)[1], label='low skill')
    ax.plot(zip(*stay_medium)[0], zip(*stay_medium)[1], label='medium skill')
    ax.plot(zip(*stay_high)[0], zip(*stay_high)[1], label='high skill')
    ax.set_xlabel('rolling success rate (last 10 answers)')
    ax.set_ylabel('probability of staying')
    ax.set_ylim(0.8, 1.0)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc="lower left")


def plot_session_length(figure, answers):
    if 'session_number' in answers:
        data = answers
    else:
        data = decorator.session_number(answers)
    length = session.session_length(data)
    ax1 = figure.add_subplot(111)
    ax1.plot(zip(*length.items())[0], zip(*length.items())[1], 'b-')
    ax1.set_xlabel('session number')
    ax1.set_ylabel('session length', color='b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    session_limit = max([session_number if portion >= 0.01 else 0
        for session_number, portion in session.session_user_portion(answers).items()])
    users_for_limit = data[data['session_number'] == session_limit]['user'].values
    data_for_limit = data[data['user'].isin(users_for_limit)]
    data_for_limit = data_for_limit[data_for_limit['session_number'] <= session_limit]
    for_limit_length = session.session_length(data_for_limit)
    ax1.plot(
        zip(*for_limit_length.items())[0],
        zip(*for_limit_length.items())[1], 'b--')

    hist = session.session_users(data)
    ax2 = ax1.twinx()
    ax2.set_yscale('log')
    ax2.set_ylabel('number of users', color='r')
    ax2.plot(zip(*hist.items())[0], zip(*hist.items())[1], 'r-.', linewidth=2)
    for tl in ax2.get_yticklabels():
        tl.set_color('r')


def plot_session_prior_skill(figure, answers, difficulty):
    if 'session_number' in answers:
        data = answers
    else:
        data = decorator.session_number(answers)
    prior_skill = session.session_prior_skill(data, difficulty)
    hist = session.session_users(data)
    ax1 = figure.add_subplot(111)
    ax1.plot(zip(*prior_skill.items())[0], zip(*prior_skill.items())[1], 'b-')
    ax1.set_xlabel('session number')
    ax1.set_ylabel('average prior skill', color='b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    ax2 = ax1.twinx()
    ax2.set_yscale('log')
    ax2.set_ylabel('number of users', color='r')
    ax2.plot(zip(*hist.items())[0], zip(*hist.items())[1], 'r-.', linewidth=2)
    for tl in ax2.get_yticklabels():
        tl.set_color('r')


def plot_session_success(figure, answers):
    if 'session_number' in answers:
        data = answers
    else:
        data = decorator.session_number(answers)
    success = session.session_success(data)
    hist = session.session_users(data)
    ax1 = figure.add_subplot(111)
    ax1.plot(zip(*success.items())[0], zip(*success.items())[1], 'b-')
    ax1.set_xlabel('session number')
    ax1.set_ylabel('success rate', color='b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    ax2 = ax1.twinx()
    ax2.set_yscale('log')
    ax2.set_ylabel('number of users', color='r')
    ax2.plot(zip(*hist.items())[0], zip(*hist.items())[1], 'r-.', linewidth=2)
    for tl in ax2.get_yticklabels():
        tl.set_color('r')


def plot_success_per_week(figure, answers):
    ax = figure.add_subplot(111)
    globally = sorted(overtime.success_per_week(answers).items())
    by_user = sorted(overtime.success_by_user_per_week(answers).items())
    xs = range(len(by_user))
    ax.plot(xs, zip(*globally)[1], 'b-o', label='mean success rate')
    ax.plot(xs, zip(*by_user)[1], 'r-v', label='mean success rate by user')
    ax.set_xlabel('week from project start')
    ax.set_ylabel('success rate')
    ax.legend()
