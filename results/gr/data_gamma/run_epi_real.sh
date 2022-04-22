#!/bin/bash
#export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/home/fmazza/julia/lib/julia"
<<EOF

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

EOF

type_graph="data_gamma"
N=328
d=10
height=3
lambda=0.04
mu=0.
#t_limit=18
#t_limit=54 # 36
t_limit=30
p_edge=1
nsrc=1
#seed=8
seed=7

scale=1.8

gamma=7e-4
small_lambda_limit=0
#path_contacts="testbench/data/openABM_2k_contacts.npz"
#path_contacts="testbench/data/cts_thiers13_6hrsb.npz"
#path_contacts="testbench/data/cts_thiers13_3hrsb.npz"
#path_contacts="testbench/data/cts_thiers13_2hrsb.npz"
path_contacts="testbench/data/cts_thiers_2hrs_0pause.npz"

p_source=-2

pr_sympt=0
n_test_rnd=2
delay_test_p="0. 0.4 0.5 0.6"

tobs_min=0
min_ninf=30

init_name="to_${tobs_min}_ps${pr_sympt}_inf${min_ninf}_"


EXEC="python -u"

SCRIPT=" testbench/run_epi.py"
#init_name="exp_"

#path_dir="$(pwd)/results/epijl/${type_graph}_${nsrc}src/N_${N}_${n_test_rnd}rnd/"
path_dir="$(pwd)/results/gr/${type_graph}/epijl/N_${N}_T_${t_limit}_${nsrc}src/${n_test_rnd}rnd_to${tobs_min}/"
#path_dir="$(pwd)/results/epijl/${type_graph}_${nsrc}src/N_${N}_${n_test_rnd}rnd/lessobs/"


GEN_GRAPH="--type_graph $type_graph -N $N -d $d --height $height -T $t_limit --lambda $lambda --mu $mu --p_edge $p_edge --n_sources $nsrc --scale $scale"
EXTRA_GEN="--gamma $gamma --path_contacts $path_contacts --small_lambda_limit $small_lambda_limit --ninf_min $min_ninf"


EXTRA_FLAGS=" --init_name_file $init_name --path_dir $path_dir "
SPARSE_OBS="--sparse_obs --sparse_rnd_tests $n_test_rnd --pr_sympt $pr_sympt --delay_test_p $delay_test_p --sp_obs_min_t $tobs_min --sp_obs_new "

EPIFL="--p_source $p_source --max_iter 1000 --eps_conv 1e-5 --damps 0.8 0.9 " # --seeds_range 0 1"

num_conf=150 #$((60-37))
st_conf=0

seed_st=0
nseed=2
seed_end=$(( $seed_st + $nseed - 1 ))

end_conf=$((st_conf + num_conf))

#echo $EXEC $SCRIPT
mkdir -p $path_dir
for c in $(seq $st_conf 3 $end_conf)
do
    #if [ $seed -eq 45 ]; then
    #    continue
    #fi
    echo $seed $c $(($c + 3))
    #n_conf=$(( $st_conf+$num_conf ))
    $EXEC  $SCRIPT $GEN_GRAPH $EXTRA_GEN --seed $seed $EXTRA_FLAGS $SPARSE_OBS $EPIFL --start_conf $c --num_conf 3 &
done