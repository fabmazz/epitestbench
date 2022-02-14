#!/bin/bash
<<RRG


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


type_graph="i_bird"
N=330
d=10
height=3
lambda=0.1
mu=0.
t_limit=15
p_edge=1
nsrc=1
seed=8

scale=1.8

gamma=6e-5
small_lambda_limit=100
path_contacts="$(pwd)/testbench/data/i_bird_contacts.npz"


type_graph="data_deltas"
N=220
d=10
height=3
lambda=0.2
mu=0.
t_limit=15
p_edge=1
nsrc=1
seed=7

scale=1.8

gamma=3e-3
small_lambda_limit=0
path_contacts="$(pwd)/results/work_15_contacts.npz"

type_graph="i_bird"
N=100
d=10
height=3
lambda=0.03
mu=0.
t_limit=12
p_edge=1
## 1 src last obs -> seed 6
#seed=4
#nsrc=2
seed=6
nsrc=1
scale=2

gamma=1e-3
small_lambda_limit=0
path_contacts="$(pwd)/testbench/data/work_13_contacts.npz"
RRG

type_graph="data_gamma"
N=2000
d=10
height=3
lambda=0.04
mu=0.
t_limit=16
p_edge=1
nsrc=1
seed=8

scale=1.8

gamma=0.038
small_lambda_limit=0
path_contacts="testbench/data/openABM_2k_contacts.npz"

p_source=-2

pr_sympt=0.
n_test_rnd=20
delay_test_p="0. 0.4 0.5 0.6"

p_source=1e-4


SCRIPT="-u testbench/run_risk_estim.py"

EPI_MIT_F="../../epidemic_mitigation/"
ranker=$1
tau=2
delta=8


#init_name="${n_test_rnd}rnd_psym02_tau${tau}_d${delta}_"
tobs_min=0
min_ninf=150


#init_name="lastobs_tau${tau}_d${delta}_"
init_name="to_${tobs_min}_tau${tau}_d${delta}_ps03_"

path_dir="$(pwd)/results/gr/${type_graph}/rankers/N_${N}_${nsrc}src/${n_test_rnd}rnd_to${tobs_min}"


GEN_GRAPH="--type_graph $type_graph -N $N -d $d --height $height -T $t_limit --lambda $lambda --mu $mu --p_edge $p_edge --n_sources $nsrc --scale $scale"

EXTRA_GEN="--gamma $gamma --path_contacts $path_contacts --small_lambda_limit $small_lambda_limit --ninf_min $min_ninf"

EXTRA_FLAGS=" --init_name_file $init_name --path_dir $path_dir" # --sparse_obs_last"
SPARSE_OBS="--sparse_obs --sparse_rnd_tests $n_test_rnd --pr_sympt $pr_sympt --delay_test_p $delay_test_p --sp_obs_new"
EXTRA_OBS=" --sp_obs_min_t $tobs_min " #--sp_obs_min_tinf 6"

EXPER="--ranker $ranker --epi_mit_path $EPI_MIT_F --tau $tau --delta $delta"

SIB_PARS="--p_source 1e-4 --sib_maxit 120 --p_sus 0.5 --nthreads 8"

#num_conf=100
num_conf=110
st_conf=90

mkdir -p $path_dir
##seed 
for seed in $seed # $(seq 0 100) #$(seq 0 100) 
#for l in 1
do
    echo $seed
    python $SCRIPT $GEN_GRAPH --seed $seed $EXTRA_FLAGS $SPARSE_OBS $EXTRA_OBS --start_conf $st_conf --num_conf $num_conf $EXPER $EXTRA_GEN $SIB_PARS
done