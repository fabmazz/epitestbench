#!/bin/bash
#export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/home/fmazza/julia/lib/julia"
<<EOF

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


type_graph="i_bird"
seed=9
N=95
d=10
height=3
lambda=0.1
mu=0.
t_limit=15
p_edge=1
nsrc=1

scale=1.8
###
type_graph="BA"
seed=7
N=500
d=8
height=3
#lamb=0.035
lambda=0.03
mu=0.
t_limit=12
p_edge=1
nsrc=1
scale=2



type_graph="proximity"
seed=9
N=220
d=10
height=3
lambda=0.03
mu=0.
t_limit=16
p_edge=1
nsrc=1

type_graph="BA_dyn"
seed=7
N=250
d=8
height=3
#lambda=0.035
lambda=0.028
mu=0.
t_limit=16
p_edge=1
nsrc=1
scale=1.8
pr_sympt=0.3
n_test_rnd=7
tobs_min=8
min_ninf=5
node_drop_p=0.


EOF

type_graph="RRG_dyn"
seed=7
#N=200
N=1000
#d=12
d=16
height=3
lambda=0.032
#lambda=0.03
mu=0.
t_limit=16
#p_edge=1
p_edge=1
nsrc=1
scale=1.8

gamma=2e-3
small_lambda_limit=0
path_contacts="$(pwd)/results/work_15_contacts.npz"

p_source=-2

pr_sympt=0.
n_test_rnd=20
tobs_min=0
min_ninf=100
node_drop_p=0.

delay_test_p="0. 0.4 0.5 0.6"
## minimum time
init_name="to_${tobs_min}_ps0_inf${min_ninf}_"
#init_name="exp_"

#path_dir="$(pwd)/results/epijl/${type_graph}_${nsrc}src/N_${N}_${n_test_rnd}rnd_to${tobs_min}/"
path_dir="$(pwd)/results/gr/${type_graph}/epijl/N_${N}_${nsrc}src/${n_test_rnd}rnd_to${tobs_min}/"
#path_dir="$(pwd)/results/gr/${type_graph}/epijl/N_${N}_${nsrc}src_sc19/${n_test_rnd}rnd_to${tobs_min}/"

#path_dir="$(pwd)/results/epijl/${type_graph}_${nsrc}src/N_${N}_${n_test_rnd}rnd/lessobs/"

EXEC="python -u"

SCRIPT=" testbench/run_epi.py"

GEN_GRAPH="--type_graph $type_graph -N $N -d $d --height $height -T $t_limit --lambda $lambda --mu $mu --p_edge $p_edge --n_sources $nsrc --scale $scale"
EXTRA_GEN="--gamma $gamma --path_contacts $path_contacts --small_lambda_limit $small_lambda_limit --ninf_min $min_ninf --node_drop_p $node_drop_p"


EXTRA_FLAGS=" --init_name_file $init_name --path_dir $path_dir "
SPARSE_OBS="--sparse_obs --sparse_rnd_tests $n_test_rnd --pr_sympt $pr_sympt --delay_test_p $delay_test_p --sp_obs_new --sp_obs_min_t $tobs_min "

EPIFL="--p_source $p_source --max_iter 600 --eps_conv 1e-4 --seeds_range 109 110"

num_conf=1 #$((60-37))
st_conf=0

seed_st=0
nseed=2
seed_end=$(( $seed_st + $nseed - 1 ))

#echo $EXEC $SCRIPT
mkdir -p $path_dir
for seed in 2 #$(seq $seed_st $seed_end)
do
    #if [ $seed -eq 45 ]; then
    #    continue
    #fi
    echo $seed
    #n_conf=$(( $st_conf+$num_conf ))
    $EXEC  $SCRIPT $GEN_GRAPH $EXTRA_GEN --seed $seed $EXTRA_FLAGS $SPARSE_OBS $EPIFL --start_conf $st_conf --num_conf $num_conf
done