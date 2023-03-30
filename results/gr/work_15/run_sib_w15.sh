#!/bin/bash

type_graph="data_deltas"
N=219
d=10
height=3
lambda=0.1
mu=0.
t_limit=15
p_edge=1
nsrc=1
seed=7
scale=1.8
gamma=2e-3
small_lambda_limit=0
path_contacts="testbench/data/work_15_contacts.npz"
#path_contacts="testbench/data/cts"

min_ninf=1
max_ninf=2000

p_source=-2

pr_sympt=0.3
n_test_rnd=3
delay_test_p="0. 0.4 0.5 0.6"

tobs_min=0
node_drop_p=0

EXEC="python -u"

SCRIPT=" testbench/run_sib.py"


init_name="to_${tobs_min}_psym03_"
#init_name="lastobs_tau${tau}_d${delta}_"

#path_dir="$(pwd)/results/sib/${type_graph}_${nsrc}src/N_${N}_${n_test_rnd}rnd_to${tobs_min}"
path_dir="$(pwd)/sib/N_${N}_${nsrc}src/${n_test_rnd}rnd_to${tobs_min}"


GEN_GRAPH="--type_graph $type_graph -N $N -d $d --height $height -T $t_limit --lambda $lambda --mu $mu --p_edge $p_edge --n_sources $nsrc --scale $scale"

EXTRA_GEN="--gamma $gamma --path_contacts $path_contacts --small_lambda_limit $small_lambda_limit --ninf_min $min_ninf --ninf_max $max_ninf --node_drop_p $node_drop_p"

EXTRA_FLAGS=" --init_name_file $init_name --path_dir $path_dir" # --sparse_obs_last"
SPARSE_OBS="--sparse_obs --sparse_rnd_tests $n_test_rnd --pr_sympt $pr_sympt --delay_test_p $delay_test_p"
EXTRA_OBS="--sp_obs_new --sp_obs_min_t $tobs_min " #--sp_obs_min_tinf 6"

SIB_PARS="--p_source $p_source --maxit 1000 --p_sus 0.5  --sib_tol 1e-6  --nthreads 40"

## GO BACK TO ROOT FOLDER
cd ../../..


num_conf=20
st_conf=0

mkdir -p $path_dir
for seed in $seed #$(seq 0 100)
#for l in 1
do
    echo $seed
    python $SCRIPT $GEN_GRAPH --seed $seed $EXTRA_FLAGS $SPARSE_OBS --start_conf $st_conf --num_conf $num_conf $SIB_PARS $EXTRA_GEN $EXTRA_OBS
done
