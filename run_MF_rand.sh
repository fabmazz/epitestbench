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

## 1 src SI (mu=0)-> lam=0.035
type_graph="RRG"
seed=7
#N=100
#d=10
#N=200
#d=15
N=200
d=13
#N=500
#d=34
height=3
#lamb=0.035
lambda=0.035
mu=0.
#t_limit=12
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

type_graph="RRG"
seed=7
N=180
#N=200
d=17
height=3
lambda=0.01
#lambda=0.03
mu=0.
t_limit=36
#p_edge=1
p_edge=1
nsrc=1
scale=1.8
p_gen=0
#p_gen=0.13
#p_gen=0.15

gamma=2e-3
small_lambda_limit=0
path_contacts="$(pwd)/results/work_15_contacts.npz"

#pr_sympt=0.2
#n_test_rnd=0
pr_sympt=0
n_test_rnd=2
tobs_min=0
min_ninf=15
node_drop_p=0.

delay_test_p="0. 0.4 0.5 0.6"


RRG

type_graph="RRG_dyn"
seed=7
N=200
d=12
height=3
#lamb=0.035
lambda=0.03
mu=0.
t_limit=16
p_edge=1
nsrc=1
scale=1.8

gamma=2e-3
small_lambda_limit=0
path_contacts="$(pwd)/results/work_15_contacts.npz"

p_source=-2
p_gen=0

pr_sympt=0.
n_test_rnd=4

delay_test_p="0. 0.4 0.5 0.6"
## minimum time
tobs_min=0
min_ninf=20
node_drop_p=0

p_source=1e-4

ranker=$1
tau=3
delta=8

#init_name="lastobs_tau${tau}_d${delta}_"
init_name="to_${tobs_min}_tau${tau}_d${delta}_nrnd_${n_test_rnd}_"
#init_name="to_${tobs_min}_tau${tau}_d${delta}_ps0_"


path_dir="$(pwd)/results/gr/${type_graph}/rankers/N_${N}_${nsrc}src/${n_test_rnd}rnd_to${tobs_min}" #_pgen_${p_gen}" #drop01
#path_dir="$(pwd)/results/gr/${type_graph}/rankers/N_${N}_${nsrc}src/sin_p_${pr_sympt}_to${tobs_min}_pgen_${p_gen}/" #drop01

SCRIPT="-u testbench/run_meanfield.py"

EPI_MIT_F="../../epidemic_mitigation/"

GEN_GRAPH="--type_graph $type_graph -N $N -d $d --height $height -T $t_limit --lambda $lambda --mu $mu --p_edge $p_edge --n_sources $nsrc --scale $scale"

EXTRA_GEN="--gamma $gamma --path_contacts $path_contacts --small_lambda_limit $small_lambda_limit --ninf_min $min_ninf --node_drop_p $node_drop_p --p_gen $p_gen"

EXTRA_FLAGS=" --init_name_file $init_name --path_dir $path_dir" # --sparse_obs_last"
SPARSE_OBS="--sparse_obs --sparse_rnd_tests $n_test_rnd --pr_sympt $pr_sympt --delay_test_p $delay_test_p --sp_obs_new " #--sp_obs_single
EXTRA_OBS=" --sp_obs_min_t $tobs_min " #--sp_obs_min_tinf 6"

MF_ARGS="--tau $tau --delta $delta"


#num_conf=100
num_conf=3
st_conf=0

mkdir -p $path_dir
##seed 
for seed in $(seq 0 110) #$(seq 0 100) 
#for l in 1
do
    echo $seed
    python $SCRIPT $GEN_GRAPH --seed $seed $EXTRA_FLAGS $SPARSE_OBS $EXTRA_OBS --start_conf $st_conf --num_conf $num_conf $MF_ARGS $EXTRA_GEN $SIB_PARS &
done