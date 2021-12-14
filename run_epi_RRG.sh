#!/bin/bash

## 1 src SI (mu=0)-> lam=0.035
type_graph="RRG"
seed=7
N=100
d=10
height=3
lambda=0.035
mu=0.
t_limit=15
p_edge=1
nsrc=1


path_dir="$(pwd)/results/${type_graph}"

p_source=1e-2




SCRIPT="-u testbench/run_epi.py"

pr_sympt=0.5
#n_test_rnd=3
n_test_rnd=1
delay_test_p="0. 0.4 0.5 0.6"

init_name="exp_"


GEN_GRAPH="--type_graph $type_graph -N $N -d $d --height $height -T $t_limit --lambda $lambda --mu $mu --p_edge $p_edge --n_sources $nsrc"

EXTRA_FLAGS=" --init_name_file $init_name --path_dir $path_dir "
SPARSE_OBS="--sparse_obs --sparse_rnd_tests $n_test_rnd --pr_sympt $pr_sympt --delay_test_p $delay_test_p --sparse_obs_last"

EPIFL="--p_source $p_source --max_iter 1000 --eps_conv 1e-10"

num_conf=10
st_conf=8

echo "NUM SAMPLES $num_samples"

seed_st=0
nseed=1
seed_end=$(( $seed_st + $nseed - 1 ))


mkdir -p $path_dir
for seed in $(seq $seed_st $seed_end)
do
    #if [ $seed -eq 45 ]; then
    #    continue
    #fi
    echo $seed
    #n_conf=$(( $st_conf+$num_conf ))
    python $SCRIPT $GEN_GRAPH --seed $seed $EXTRA_FLAGS $SPARSE_OBS $EPIFL --start_conf $st_conf --num_conf $num_conf
done