from prettytable import PrettyTable
import proso.geography.user as user
import numpy


def answers_per_user(output, answers, group_column, group_name_mapping=None):
    output.write("----------------------------------------------------------------------\n")
    output.write("  Answers per User                                                    \n")
    output.write("----------------------------------------------------------------------\n")

    table = PrettyTable([
        'Group', 'Size', 'Mean', "Std.", "Log Mean", 'Median', '25 Perc.', '75 Perc.'])
    table.align['Group'] = 'l'
    for group_name, group_data in answers.groupby(group_column):
        numbers = user.answers_per_user(group_data).values()
        table.add_row([
            group_name if group_name_mapping is None else group_name_mapping[group_name],
            len(numbers),
            numpy.round(numpy.mean(numbers), 2),
            numpy.round(numpy.std(numbers), 2),
            numpy.round(2 ** numpy.mean(numpy.log2(numbers)), 2),
            numpy.median(numbers),
            numpy.round(numpy.percentile(numbers, 25), 2),
            numpy.round(numpy.percentile(numbers, 75), 2)])
    output.write(table.get_string(sortby="Group"))
    output.write("\n")


def user_ratio(output, answers, group_column, group_name_mapping=None):
    output.write("----------------------------------------------------------------------\n")
    output.write("  User Ratios                                                         \n")
    output.write("----------------------------------------------------------------------\n")

    table = PrettyTable(['Group', '20 answers', "50 answers", "100 answers", '2 sessions'])
    table.align['Group'] = 'l'
    for group_name, group_data in answers.groupby(group_column):
        table.add_row([
            group_name if group_name_mapping is None else group_name_mapping[group_name],
            numpy.round(user.user_ratio(group_data, answer_number_min=20), 2),
            numpy.round(user.user_ratio(group_data, answer_number_min=50), 2),
            numpy.round(user.user_ratio(group_data, answer_number_min=100), 2),
            numpy.round(user.user_ratio(group_data, session_number=2), 2)])
    output.write(table.get_string(sortby="Group"))
    output.write("\n")
