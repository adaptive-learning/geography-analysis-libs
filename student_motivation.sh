#!/bin/bash

DATA_VERSION=2015-01-04
DATA_DIR=data-${DATA_VERSION}
DEST_DIR=dest-${DATA_VERSION}
DEST_SIMPLIFIED_DIR=${DEST_DIR}-simplified

MIN_DATE=2014-11-12_20:00:00
ANSWERS_PER_USER=10
PLACE_ASKED_TYPE=state
MAP_TYPE="continent world"

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
    --data-dir ${DATA_DIR} \
    --drop-classrooms \
    --drop-users \
    --answers-per-user ${ANSWERS_PER_USER} \
    --storage pkl \
    --drop-tests \
    --min-date ${MIN_DATE} \
    --groups motivation \
    --verbose > ${DEST_SIMPLIFIED_DIR}/overview.txt;

LOCAL_DEST_DIR=`get_directory`;
cp ${LOCAL_DEST_DIR}/feedback_by_success.png ${DEST_SIMPLIFIED_DIR}/feedback_by_success_overview.png
cp ${LOCAL_DEST_DIR}/feedback_vs_answers.png ${DEST_SIMPLIFIED_DIR}/feedback_vs_answers_overview.png

python scripts/ab_testing.py \
    -d ${DEST_DIR} \
    --data-dir ${DATA_DIR} \
    --interested-prefixes recommendation_by_ recommendation_options_ \
    --drop-classrooms \
    --drop-users \
    --answers-per-user ${ANSWERS_PER_USER} \
    --storage pkl \
    --drop-tests \
    --place-asked-type ${PLACE_ASKED_TYPE} \
    --groups motivation progress difference \
    --map-type ${MAP_TYPE} \
    --verbose > $DEST_SIMPLIFIED_DIR/experiment_1.txt;

LOCAL_DEST_DIR=`get_directory`;
cp ${LOCAL_DEST_DIR}/ab_group_answers_per_user_boxplot.png ${DEST_SIMPLIFIED_DIR}/answers_algorithm.png
cp ${LOCAL_DEST_DIR}/ab_group_prior_skill.png ${DEST_SIMPLIFIED_DIR}/prior_skill_algorithm.png

python scripts/ab_testing.py \
    -d ${DEST_DIR} \
    --data-dir ${DATA_DIR} \
    --interested-prefixes recommendation_target_prob_adjustment_ \
    --drop-classrooms \
    --drop-users \
    --answers-per-user ${ANSWERS_PER_USER} \
    --min-date ${MIN_DATE} \
    --storage pkl \
    --drop-tests \
    --place-asked-type ${PLACE_ASKED_TYPE} \
    --groups motivation progress difference \
    --map-type ${MAP_TYPE} \
    --verbose > ${DEST_SIMPLIFIED_DIR}/experiment_2.txt;

LOCAL_DEST_DIR=`get_directory`;
cp ${LOCAL_DEST_DIR}/ab_group_answers_per_user_boxplot.png ${DEST_SIMPLIFIED_DIR}/answers_adjustment.png
cp ${LOCAL_DEST_DIR}/ab_group_prior_skill.png ${DEST_SIMPLIFIED_DIR}/prior_skill_adjustment.png
cp ${LOCAL_DEST_DIR}/ab_group_feedback_per_group.png ${DEST_SIMPLIFIED_DIR}/feedback_adjustment.png

python scripts/ab_testing.py \
    -d ${DEST_DIR} \
    --data-dir ${DATA_DIR} \
    --interested-prefixes recommendation_target_prob_ \
    --drop-classrooms \
    --drop-users \
    --answers-per-user ${ANSWERS_PER_USER} \
    --min-date ${MIN_DATE} \
    --storage pkl \
    --drop-tests \
    --place-asked-type ${PLACE_ASKED_TYPE} \
    --groups motivation progress difference \
    --buckets 5 \
    --map-type ${MAP_TYPE} \
    --verbose > ${DEST_SIMPLIFIED_DIR}/experiment_3.txt;
    LOCAL_DEST_DIR=`get_directory`;
    cp ${LOCAL_DEST_DIR}/ab_group_answers_per_user_boxplot.png ${DEST_SIMPLIFIED_DIR}/answers_target_prob.png
    cp ${LOCAL_DEST_DIR}/ab_group_prior_skill.png ${DEST_SIMPLIFIED_DIR}/prior_skill_target_prob_adjustment.png
    cp ${LOCAL_DEST_DIR}/ab_group_feedback_per_group.png ${DEST_SIMPLIFIED_DIR}/feedback_target_prob.png

for SWITCHER in false true; do
    python scripts/ab_testing.py \
        -d ${DEST_DIR} \
        --data-dir ${DATA_DIR} \
        --interested-prefixes recommendation_target_prob_ \
        --drop-classrooms \
        --drop-users \
        --answers-per-user ${ANSWERS_PER_USER} \
        --min-date ${MIN_DATE} \
        --storage pkl \
        --drop-tests \
        --place-asked-type ${PLACE_ASKED_TYPE} \
        --filter-abvalue recommendation_target_prob_adjustment_${SWITCHER} \
        --groups motivation progress difference \
        --buckets 5 \
        --map-type ${MAP_TYPE} \
        --verbose > ${DEST_SIMPLIFIED_DIR}/experiment_3_adjustment_${SWITCHER}.txt;
        LOCAL_DEST_DIR=`get_directory`;
        cp ${LOCAL_DEST_DIR}/ab_group_answers_per_user_boxplot.png ${DEST_SIMPLIFIED_DIR}/answers_target_prob_adjustment_${SWITCHER}.png
        cp ${LOCAL_DEST_DIR}/ab_group_prior_skill.png ${DEST_SIMPLIFIED_DIR}/prior_skill_target_prob_adjustment_${SWITCHER}.png
        cp ${LOCAL_DEST_DIR}/ab_group_feedback_per_group.png ${DEST_SIMPLIFIED_DIR}/feedback_target_prob_adjustment_${SWITCHER}.png
done;


