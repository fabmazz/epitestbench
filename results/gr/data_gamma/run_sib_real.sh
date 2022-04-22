#!/bin/bash
<<RRG

type_graph="proximity"
seed=9
N=200
d=10
height=3
lambda=0.035
mu=0.
t_limit=15
p_edge=1
nsrc=1

type_graph="RRG_dyn"
seed=7
N=200
#d=12
d=14
height=3
lambda=0.035
#lambda=0.03
mu=0.
t_limit=16
#p_edge=1
p_edge=0.7
nsrc=1
scale=1.8

## 1 src SI (mu=0)-> lam=0.035
type_graph="RRG"
seed=7
#N=100
#d=10
#N=200
#d=15
N=200
d=13
height=3
lambda=0.035
mu=0.
t_limit=15
p_edge=1
nsrc=1
scale=2


type_graph="TREE"
seed=7
N=10
d=7
height=4
#lamb=0.035
lambda=0.35
mu=0.
t_limit=13
p_edge=1
nsrc=1
scale=2

type_graph="BA"
seed=7
N=500
d=8
height=3
#lamb=0.035
lambda=0.025
mu=0.
t_limit=16
p_edge=1
nsrc=1
scale=2
scale=1.8

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
path_contacts="$(pwd)/results/work_15_contacts.npz"

type_graph="proximity"
seed=9
N=220
d=10epitestbench
height=3
lambda=0.03
mu=0.
t_limit=16
p_edge=1
nsrc=1

scale=1.9


RRG

type_graph="data_gamma"
N=328
d=10
height=3
lambda=0.04
mu=0.
t_limit=18
#t_limit=54 # 36
#t_limit=30
p_edge=1
nsrc=1
seed=8
#seed=7

scale=1.8

gamma=7e-4
small_lambda_limit=0
#path_contacts="testbench/data/openABM_2k_contacts.npz"
path_contacts="testbench/data/cts_thiers13_6hrsb.npz"
#path_contacts="testbench/data/cts_thiers13_3hrsb.npz"
#path_contacts="testbench/data/cts_thiers13_2hrsb.npz"
#path_contacts="testbench/data/cts_thiers_2hrs_0pause.npz"

p_source=-2

pr_sympt=0
n_test_rnd=4
delay_test_p="0. 0.4 0.5 0.6"

tobs_min=0
min_ninf=30

node_drop_p=0
p_gen=0

init_name="to_${tobs_min}_ps${pr_sympt}_"
#init_name="lastobs_tau${tau}_d${delta}_"

#path_dir="$(pwd)/results/sib/${type_graph}_${nsrc}src/N_${N}_${n_test_rnd}rnd_to${tobs_min}"
path_dir="$(pwd)/results/gr/${type_graph}/sib/N_${N}_T_${t_limit}_${nsrc}src/${n_test_rnd}rnd_to${tobs_min}"

SCRIPT="-u testbench/run_sib.py"

GEN_GRAPH="--type_graph $type_graph -N $N -d $d --height $height -T $t_limit --lambda $lambda --mu $mu --p_edge $p_edge --n_sources $nsrc --scale $scale"

EXTRA_GEN="--gamma $gamma --path_contacts $path_contacts --small_lambda_limit $small_lambda_limit --ninf_min $min_ninf --node_drop_p $node_drop_p"

EXTRA_FLAGS=" --init_name_file $init_name --path_dir $path_dir" # --sparse_obs_last"
SPARSE_OBS="--sparse_obs --sparse_rnd_tests $n_test_rnd --pr_sympt $pr_sympt --delay_test_p $delay_test_p"
EXTRA_OBS="--sp_obs_new --sp_obs_min_t $tobs_min " #--sp_obs_min_tinf 6"

EXPER="--ranker $ranker --epi_mit_path $EPI_MIT_F --tau $tau --delta $delta"

SIB_PARS="--p_source $p_source --maxit 600 --p_sus 0.5  --sib_tol 1e-6  --nthreads 34"

num_conf=75 #100
st_conf=75

mkdir -p $path_dir
for seed in $seed #$(seq 18 100) #$(seq 0 100)
#for l in 1
do
    echo $seed
    python $SCRIPT $GEN_GRAPH --seed $seed $EXTRA_FLAGS $SPARSE_OBS $EXTRA_OBS --start_conf $st_conf --num_conf $num_conf $SIB_PARS $EXTRA_GEN 
done
