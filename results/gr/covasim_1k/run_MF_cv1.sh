#!/bin/bash

type_graph="data"
#N=2000
N=1000
d=10
height=3
lambda=0.5
mu=0.
t_limit=24
p_edge=1
nsrc=2
seed=8

scale=1.8

gamma=0.038
small_lambda_limit=0
path_contacts="testbench/data/covasim_1k_seattle_t30.npz"
#path_contacts="testbench/data/cts"

min_ninf=150
max_ninf=750

p_source=-2

pr_sympt=0.
n_test_rnd=8
delay_test_p="0. 0.4 0.5 0.6"

tobs_min=0
node_drop_p=0
p_gen=0
p_source=1e-4

ranker=$1
tau=4
delta=10

#init_name="lastobs_tau${tau}_d${delta}_"
#init_name="to_${tobs_min}_tau${tau}_d${delta}_nrnd_${n_test_rnd}_"
init_name="to_${tobs_min}_tau${tau}_d${delta}_psym0_"


path_dir="$(pwd)/MF/N_${N}_${nsrc}src/${n_test_rnd}rnd_to${tobs_min}/"


SCRIPT="-u testbench/run_meanfield.py"

EPI_MIT_F="../../epidemic_mitigation/"


GEN_GRAPH="--type_graph $type_graph -N $N -d $d --height $height -T $t_limit --lambda $lambda --mu $mu --p_edge $p_edge --n_sources $nsrc --scale $scale"
EXTRA_GEN="--gamma $gamma --path_contacts $path_contacts --small_lambda_limit $small_lambda_limit --ninf_min $min_ninf --ninf_max $max_ninf"


EXTRA_FLAGS=" --init_name_file $init_name --path_dir $path_dir "
SPARSE_OBS="--sparse_obs --sparse_rnd_tests $n_test_rnd --pr_sympt $pr_sympt --delay_test_p $delay_test_p --sp_obs_min_t $tobs_min --sp_obs_new "

MF_ARGS="--tau $tau --delta $delta"

## GO BACK TO ROOT FOLDER
cd ../../..

#num_conf=100
num_conf=100
st_conf=0

mkdir -p $path_dir
##seed 
#for seed in $(seq 0 110) #$(seq 0 100) 
for l in 1
do
    echo $seed
    python $SCRIPT $GEN_GRAPH --seed $seed $EXTRA_FLAGS $SPARSE_OBS $EXTRA_OBS --start_conf $st_conf --num_conf $num_conf $MF_ARGS $EXTRA_GEN $SIB_PARS
done