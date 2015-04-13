#!/bin/bash

DATA_VERSION=2015-01-04
DATA_DIR=data-${DATA_VERSION}
DEST_DIR=dest-${DATA_VERSION}
DEST_SIMPLIFIED_DIR=${DEST_DIR}-simplified

MIN_DATE=2014-11-12_20:00:00
ANSWERS_PER_USER=10
PLACE_ASKED_TYPE=state
MAP_TYPE="continent world"
CLASSROOM_SIZE=5
OUTPUT=svg

function get_directory() {
    LOCAL_DEST=`ls ${DEST_DIR} | grep '^apu\|^recommendation'`;
    mv ${DEST_DIR}/${LOCAL_DEST} ${DEST_DIR}/_${LOCAL_DEST};
    echo ${DEST_DIR}/_${LOCAL_DEST};
}

make install;

rm -rf ${DEST_SIMPLIFIED_DIR} && mkdir ${DEST_SIMPLIFIED_DIR}

set -x
set -e

python scripts/overview.py \
    -d ${DEST_DIR} \
    -o svg \
    --data-dir ${DATA_DIR} \
    --drop-classrooms ${CLASSROOM_SIZE} \
    --drop-users \
    --answers-per-user ${ANSWERS_PER_USER} \
    --storage pkl \
    --drop-tests \
    --min-date ${MIN_DATE} \
    --groups motivation \
    --verbose > ${DEST_SIMPLIFIED_DIR}/overview.txt;

LOCAL_DEST_DIR=`get_directory`;
cp ${LOCAL_DEST_DIR}/feedback_by_success.${OUTPUT} ${DEST_SIMPLIFIED_DIR}/feedback_by_success_overview.${OUTPUT}
cp ${LOCAL_DEST_DIR}/feedback_vs_answers.${OUTPUT} ${DEST_SIMPLIFIED_DIR}/feedback_vs_answers_overview.${OUTPUT}

python scripts/overview.py \
    -d ${DEST_DIR} \
    -o svg \
    --data-dir ${DATA_DIR} \
    --only-classrooms ${CLASSROOM_SIZE} \
    --drop-users \
    --answers-per-user ${ANSWERS_PER_USER} \
    --storage pkl \
    --drop-tests \
    --min-date ${MIN_DATE} \
    --groups motivation \
    --verbose > ${DEST_SIMPLIFIED_DIR}/overview-classroom.txt;

LOCAL_DEST_DIR=`get_directory`;
cp ${LOCAL_DEST_DIR}/feedback_by_success.${OUTPUT} ${DEST_SIMPLIFIED_DIR}/feedback_by_success_overview__classrooms.${OUTPUT}
cp ${LOCAL_DEST_DIR}/feedback_vs_answers.${OUTPUT} ${DEST_SIMPLIFIED_DIR}/feedback_vs_answers_overview__classrooms.${OUTPUT}

python scripts/ab_testing.py \
    -d ${DEST_DIR} \
    -o svg \
    --data-dir ${DATA_DIR} \
    --interested-prefixes recommendation_by_ recommendation_options_ \
    --drop-classrooms ${CLASSROOM_SIZE} \
    --drop-users \
    --answers-per-user ${ANSWERS_PER_USER} \
    --storage pkl \
    --drop-tests \
    --place-asked-type ${PLACE_ASKED_TYPE} \
    --map-type ${MAP_TYPE} \
    --groups motivation progress \
    --verbose > $DEST_SIMPLIFIED_DIR/experiment_1.txt;

LOCAL_DEST_DIR=`get_directory`;
cp ${LOCAL_DEST_DIR}/ab_group_answers_per_user_boxplot.${OUTPUT} ${DEST_SIMPLIFIED_DIR}/answers_algorithm.${OUTPUT}
cp ${LOCAL_DEST_DIR}/ab_group_success_per_user.${OUTPUT} ${DEST_SIMPLIFIED_DIR}/success_algorithm.${OUTPUT}

python scripts/ab_testing.py \
    -d ${DEST_DIR} \
    -o svg \
    --data-dir ${DATA_DIR} \
    --interested-prefixes recommendation_target_prob_adjustment_ \
    --drop-classrooms ${CLASSROOM_SIZE} \
    --drop-users \
    --answers-per-user ${ANSWERS_PER_USER} \
    --min-date ${MIN_DATE} \
    --storage pkl \
    --drop-tests \
    --place-asked-type ${PLACE_ASKED_TYPE} \
    --map-type ${MAP_TYPE} \
    --groups motivation progress \
    --verbose > ${DEST_SIMPLIFIED_DIR}/experiment_2.txt;

LOCAL_DEST_DIR=`get_directory`;
cp ${LOCAL_DEST_DIR}/ab_group_answers_per_user_boxplot.${OUTPUT} ${DEST_SIMPLIFIED_DIR}/answers_adjustment.${OUTPUT}
cp ${LOCAL_DEST_DIR}/ab_group_success_per_user.${OUTPUT} ${DEST_SIMPLIFIED_DIR}/success_adjustment.${OUTPUT}
cp ${LOCAL_DEST_DIR}/ab_group_feedback_per_group.${OUTPUT} ${DEST_SIMPLIFIED_DIR}/feedback_adjustment.${OUTPUT}

python scripts/ab_testing.py \
    -d ${DEST_DIR} \
    -o svg \
    --data-dir ${DATA_DIR} \
    --interested-prefixes recommendation_target_prob_ \
    --drop-classrooms ${CLASSROOM_SIZE} \
    --drop-users \
    --answers-per-user ${ANSWERS_PER_USER} \
    --min-date ${MIN_DATE} \
    --storage pkl \
    --drop-tests \
    --place-asked-type ${PLACE_ASKED_TYPE} \
    --map-type ${MAP_TYPE} \
    --buckets 5 \
    --groups motivation progress \
    --verbose > ${DEST_SIMPLIFIED_DIR}/experiment_3.txt;
    LOCAL_DEST_DIR=`get_directory`;
    cp ${LOCAL_DEST_DIR}/ab_group_answers_per_user_boxplot.${OUTPUT} ${DEST_SIMPLIFIED_DIR}/answers_target_prob.${OUTPUT}
    cp ${LOCAL_DEST_DIR}/ab_group_success_per_user.${OUTPUT} ${DEST_SIMPLIFIED_DIR}/success_target_prob.${OUTPUT}
    cp ${LOCAL_DEST_DIR}/ab_group_feedback_per_group.${OUTPUT} ${DEST_SIMPLIFIED_DIR}/feedback_target_prob.${OUTPUT}

for SWITCHER in false true; do
    python scripts/ab_testing.py \
        -d ${DEST_DIR} \
        -o svg \
        --data-dir ${DATA_DIR} \
        --interested-prefixes recommendation_target_prob_ \
        --drop-classrooms ${CLASSROOM_SIZE} \
        --drop-users \
        --answers-per-user ${ANSWERS_PER_USER} \
        --min-date ${MIN_DATE} \
        --storage pkl \
        --drop-tests \
        --place-asked-type ${PLACE_ASKED_TYPE} \
        --map-type ${MAP_TYPE} \
        --buckets 5 \
        --filter-abvalue recommendation_target_prob_adjustment_${SWITCHER} \
        --groups motivation progress \
        --verbose > ${DEST_SIMPLIFIED_DIR}/experiment_3_adjustment_${SWITCHER}.txt;
        LOCAL_DEST_DIR=`get_directory`;
        cp ${LOCAL_DEST_DIR}/ab_group_answers_per_user_boxplot.${OUTPUT} ${DEST_SIMPLIFIED_DIR}/answers_target_prob_adjustment_${SWITCHER}.${OUTPUT}
        cp ${LOCAL_DEST_DIR}/ab_group_success_per_user.${OUTPUT} ${DEST_SIMPLIFIED_DIR}/success_target_prob_adjustment_${SWITCHER}.${OUTPUT}
        cp ${LOCAL_DEST_DIR}/ab_group_feedback_per_group.${OUTPUT} ${DEST_SIMPLIFIED_DIR}/feedback_target_prob_adjustment_${SWITCHER}.${OUTPUT}
done;


