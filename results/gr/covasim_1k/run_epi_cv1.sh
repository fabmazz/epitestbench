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

init_name="${n_test_rnd}rnd_pr0_"


EXEC="python -u"

SCRIPT=" testbench/run_epi.py"
#init_name="exp_"

#path_dir="$(pwd)/results/epijl/${type_graph}_${nsrc}src/N_${N}_${n_test_rnd}rnd/"
path_dir="$(pwd)/epijl/N_${N}_${nsrc}src/${n_test_rnd}rnd_to${tobs_min}/"
#path_dir="$(pwd)/results/epijl/${type_graph}_${nsrc}src/N_${N}_${n_test_rnd}rnd/lessobs/"


GEN_GRAPH="--type_graph $type_graph -N $N -d $d --height $height -T $t_limit --lambda $lambda --mu $mu --p_edge $p_edge --n_sources $nsrc --scale $scale"
EXTRA_GEN="--gamma $gamma --path_contacts $path_contacts --small_lambda_limit $small_lambda_limit --ninf_min $min_ninf --ninf_max $max_ninf"


EXTRA_FLAGS=" --init_name_file $init_name --path_dir $path_dir "
SPARSE_OBS="--sparse_obs --sparse_rnd_tests $n_test_rnd --pr_sympt $pr_sympt --delay_test_p $delay_test_p --sp_obs_min_t $tobs_min --sp_obs_new "

EPIFL="--p_source $p_source --max_iter 600 --eps_conv 1e-5 --damps 0.2 0.8" # --seeds_range 0 1"

num_conf=10 #$((60-37))
st_conf=$1

seed_st=0
nseed=2
seed_end=$(( $seed_st + $nseed - 1 ))

## GO BACK TO ROOT FOLDER
cd ../../..

#echo $EXEC $SCRIPT
mkdir -p $path_dir
for seed in $seed #$(seq $seed_st $seed_end)
do
    #if [ $seed -eq 45 ]; then
    #    continue
    #fi
    echo $seed
    #n_conf=$(( $st_conf+$num_conf ))
    $EXEC  $SCRIPT $GEN_GRAPH $EXTRA_GEN --seed $seed $EXTRA_FLAGS $SPARSE_OBS $EPIFL --start_conf $st_conf --num_conf $num_conf
done