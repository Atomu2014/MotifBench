import sys
import os
import pandas as pd
from tqdm import tqdm


import os
import shutil
import subprocess
import pandas as pd
from tqdm import tqdm


def compute_motif_cluster(pdb_files, success_path='fs_input', fs_tmp_path='fs_tmp'):
    shutil.rmtree(success_path, ignore_errors=True)
    os.makedirs(success_path, exist_ok=True)
    for pdb_file in pdb_files:
        shutil.copy(pdb_file, os.path.join(success_path, os.path.basename(pdb_file)))

    shutil.rmtree(fs_tmp_path, ignore_errors=True)
    os.makedirs(fs_tmp_path, exist_ok=True)

    subprocess.run([
        "foldseek", "easy-cluster",
        success_path,
        f"{fs_tmp_path}/res",
        fs_tmp_path,
        "--alignment-type", "1",
        "--cov-mode", "0",
        "--min-seq-id", "0",
        "--tmscore-threshold", "0.6"
    ], stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    check=True)

    fs_results = pd.read_csv(f"{fs_tmp_path}/res_cluster.tsv", sep="\t", header=None)

    n_cluster = len(fs_results.iloc[:, 0].unique())
    n_member = len(fs_results.iloc[:, 1].unique())
    n_total = len(fs_results)

    return n_cluster, n_member, n_total


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python count_success.py <output_dir>")
        sys.exit(1)

    # iterate over all subdirectories in the output directory
    for subdir in sorted(os.listdir(sys.argv[1])):
        summary_file = os.path.join(sys.argv[1], subdir, 'esm_summary_results.csv')
        if not os.path.exists(summary_file):
            print(f'{summary_file} not found')
            continue
        task_name = summary_file.split('/')[1]
        df = pd.read_csv(summary_file)
        n_success = df['Success'].sum() / 8
        # get all backbone_path in df where Success is True
        backbone_paths = df[df['Success'] == True]['backbone_path'].unique()
        if len(backbone_paths) == 0:
            print(f'{task_name}: no successful scaffolds')
            continue
        n_cluster, n_member, n_total = compute_motif_cluster(backbone_paths)

        print(f'{task_name}: n_success: {n_success}, n_cluster: {n_cluster}')
