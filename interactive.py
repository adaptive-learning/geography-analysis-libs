from os import path, makedirs, removedirs
import proso.geography.abtesting as abtesting
import proso.geography.answers as answers
import proso.geography.decorator as decorator
import proso.geography.overtime as overtime
import proso.geography.session as session
import proso.geography.success as success
import proso.geography.user as user

DEST_DIR = './dest-interactive'
DATA_DIR = './data'

def reset_dest():
    if path.exists(DEST_DIR):
        removedirs(DEST_DIR)
    makedirs(DEST)

data = answers.from_csv(
    answer_csv=DATA_DIR + '/geography.answer.csv',
    answer_options_csv=DATA_DIR + '/geography.answer_options.csv',
    answer_ab_values_csv=DATA_DIR + '/geography.answer_ab_values.csv',
    ab_value_csv=DATA_DIR + '/geography.ab_value.csv')


