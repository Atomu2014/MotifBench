# # Run the evaluation for each problem in sequence on one machine / GPU
# ls motif_pdbs/ | sed 's/\.pdb$//' | while read motif; do
#     ./scripts/evaluate_bbs.sh $motif config.txt
# done

# Or run on the whole set of scaffolds in parallel on a Slurm cluster
# ./scripts/launch_all.sh config.txt

#!/bin/bash
set -euo pipefail

TASKS=(
    # 01_1LDB
    # 02_1ITU
    # 03_2CGA
    # 04_5WN9
    # 05_5ZE9
    # 06_6E6R
    # # 07_6E6R
    # 08_7AD5
    # 09_7CG5
    # 10_7WRK
    # 11_3TQB
    # 12_4JHW
    # 13_4JHW
    14_5IUS
    15_7A8S
    16_7BNY
    17_7DGW
    # 18_7MQQ
    # 19_7MQQ
    20_7UWL
    21_1B73
    22_1BCF
    23_1MPY
    24_1QY3
    25_2RKX
    26_3B5V
    27_4XOJ
    28_5YUI
    29_6CPA
    30_7UWL
)

export CUDA_VISIBLE_DEVICES="0,5,6,7,8,9"

echo "CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
if [ -n "${CUDA_VISIBLE_DEVICES:-}" ]; then
    IFS=',' read -ra GPU_LIST <<< "$CUDA_VISIBLE_DEVICES"
else
    GPU_LIST=($(nvidia-smi --query-gpu=index --format=csv,noheader))
fi

NUM_GPUS=${#GPU_LIST[@]}

echo "Detected GPUs: ${GPU_LIST[*]}"
echo "NUM_GPUS=$NUM_GPUS"

gpu_idx=0
pids=()

echo "Starting evaluation..."

export scaffold_base_dir=/data/yanruqu2/ProteinaEdit/scaffolds_motif_bench

for motif in "${TASKS[@]}"; do
    if [ ! -d "$scaffold_base_dir/$motif" ]; then
        echo "Skipping $motif: $scaffold_base_dir/$motif not found"
        continue
    fi
    gpu_id=${GPU_LIST[$gpu_idx]}

    echo "Starting motif: $motif on GPU: $gpu_id"

    CUDA_VISIBLE_DEVICES=$gpu_id ./scripts/evaluate_bbs.sh "$motif" config.txt &

    pids+=($!)
    gpu_idx=$((gpu_idx + 1))

    if [ "$gpu_idx" -ge "$NUM_GPUS" ]; then
        echo "Waiting for current batch to finish..."
        for pid in "${pids[@]}"; do
            wait "$pid"
        done
        pids=()
        gpu_idx=0
    fi
done

for pid in "${pids[@]}"; do
    wait "$pid"
done

echo "All evaluations have been completed."
