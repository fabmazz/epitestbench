#!/bin/bash
<<RRG
## 1 src SI (mu=0)-> lam=0.035
type_graph="proximity"
seed=9
N=60
d=10
height=3
lambda=0.035
mu=0.
t_limit=15
p_edge=1
nsrc=1

scale=1.8

gamma=1e-3
small_lambda_limit=0
path_contacts="testbench/data/work_13_contacts.npz"


RRG

## 1 src SI (mu=0)-> lam=0.035
type_graph="RRG"
seed=7
#N=100
#d=10
#N=200
#d=15
N=1000
d=20
height=3
lambda=0.035
mu=0.
t_limit=15
p_edge=1
nsrc=1
scale=2

gamma=1e-3
small_lambda_limit=0
path_contacts="testbench/data/work_13_contacts.npz"

path_dir="$(pwd)/results/sib/${type_graph}_${nsrc}src/N_${N}"

p_source=1e-4
sib_it=1000


SCRIPT="-u testbench/run_sib.py"



EPI_MIT_F="../../epidemic_mitigation/"
ranker=$1
tau=4
delta=10

#sparse observ
pr_sympt=0.2
#n_test_rnd=3
n_test_rnd=1
delay_test_p="0. 0.1 0.5 0.6"

init_name="${n_test_rnd}rnd_pr_02_"
#init_name="lastobs_tau${tau}_d${delta}_"

GEN_GRAPH="--type_graph $type_graph -N $N -d $d --height $height -T $t_limit --lambda $lambda --mu $mu --p_edge $p_edge --n_sources $nsrc --scale $scale"

EXTRA_GEN="--gamma $gamma --path_contacts $path_contacts --small_lambda_limit $small_lambda_limit"

EXTRA_FLAGS=" --init_name_file $init_name --path_dir $path_dir" # --sparse_obs_last"
SPARSE_OBS="--sparse_obs --sparse_rnd_tests $n_test_rnd --pr_sympt $pr_sympt --delay_test_p $delay_test_p"

EXPER="--ranker $ranker --epi_mit_path $EPI_MIT_F --tau $tau --delta $delta"

SIB_PARS="--p_source $p_source --maxit $sib_it --p_sus 0.5  --sib_tol 1e-6  --nthreads 20"

num_conf=1
st_conf=0

mkdir -p $path_dir
for seed in $(seq 0 50)
#for l in 1
do
    echo $seed
    python $SCRIPT $GEN_GRAPH --seed $seed $EXTRA_FLAGS $SPARSE_OBS --start_conf $st_conf --num_conf $num_conf $SIB_PARS $EXTRA_GEN
done