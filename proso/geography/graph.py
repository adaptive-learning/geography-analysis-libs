import session
import decorator
import user


def boxplot_answers_per_user(figure, answers, group_column):
    ax = figure.add_subplot(111)
    labels = []
    to_plot = []
    for group_name, group_data in answers.groupby(group_column):
        number = user.answers_per_user(group_data)
        to_plot.append(number.values())
        labels.append(group_name)
    ax.boxplot(to_plot)
    ax.set_yscale('log')
    ax.set_xticklabels(labels)
    ax.set_xlabel(group_column)
    ax.set_ylabel('number of answers')


def plot_answers_per_day(figure, answers):
    ax1 = figure.add_subplot(111)
    to_plot = sorted(user.answers_per_day(answers).items())
    ax1.plot(zip(*to_plot)[0], zip(*to_plot)[1], 'b-')
    ax1.set_xlabel('day')
    ax1.set_ylabel('average number of answers per user', color='b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    to_plot = sorted(user.users_per_day(answers).items())
    ax2 = ax1.twinx()
    ax2.set_ylabel('number of users', color='r')
    ax2.plot(zip(*to_plot)[0], zip(*to_plot)[1], 'r--', linewidth=1)
    for tl in ax2.get_yticklabels():
        tl.set_color('r')


def plot_session_length(figure, answers):
    if 'session_number' in answers:
        data = answers
    else:
        data = decorator.session_number(answers)
    length = session.session_length(data)
    hist = session.session_users(data)
    ax1 = figure.add_subplot(111)
    ax1.plot(zip(*length.items())[0], zip(*length.items())[1], 'b-')
    ax1.set_xlabel('session number')
    ax1.set_ylabel('session length', color='b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    ax2 = ax1.twinx()
    ax2.set_yscale('log')
    ax2.set_ylabel('number of users', color='r')
    ax2.plot(zip(*hist.items())[0], zip(*hist.items())[1], 'r-.', linewidth=2)
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
