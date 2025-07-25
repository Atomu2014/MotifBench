import pandas as pd
import numpy as np
import argparse
import os

def diversity_cluster_path(base_dir, motif, rep=None):
    path = base_dir
    if rep is not None:
        path += f"/rep{rep}/"
    path += f"/{motif}/"
    path += f"/esm_successful_backbones/diversity_cluster.tsv"
    return path
   
def load_successes_and_cluster(fn):
    # Return empty list if there are no successes
    if not os.path.isfile(fn): return []

    successes_and_cluster = []
    with open(fn) as f:
        for l in f:
            if "assist" in l: continue
            cluster, bb = l.split()
            bb = int(bb[:-4].split("_")[-1])
            cluster = int(cluster[:-4].split("_")[-1])
            successes_and_cluster.append((bb,cluster))
    return successes_and_cluster

def MotifBenchScore(N, N_max=50, alpha=5):
    return 100*((N_max + alpha)/N_max) * N / (N + alpha)

def MBScore_boostrap(successes_and_cluster, n_subsamples=1000, subsample_size=50, alpha=5):
    num_clusters = []
    for _ in range(n_subsamples):
        idcs = np.random.choice(100, subsample_size, replace=False)
        successes_and_cluster_ = [(bb, cluster) for (bb, cluster) in
                successes_and_cluster if bb in idcs]
        num_clusters.append(len(set([cluster for (_, cluster) in
            successes_and_cluster_])))
    motif_bench_scores = [MotifBenchScore(num, N_max=subsample_size, alpha=alpha) for num in num_clusters]
    mean = np.mean(motif_bench_scores)
    sem = np.std(motif_bench_scores)/np.sqrt(n_subsamples)
    return mean, sem


def main(test_cases_file, summary_by_case_file, summary_by_group_file):
    # Load the input files
    test_cases = pd.read_csv(test_cases_file)
    test_cases['idx'] = [i + 1 for i in range(len(test_cases))]
    group_by_idx = {row[1]["idx"]: row[1]['group'] for row in test_cases.iterrows()}
    
    summary_by_case = pd.read_csv(summary_by_case_file)
    summary_by_case['group'] = [group_by_idx[int(row[1]['Problem'].split("_")[0])] for row in summary_by_case.iterrows()]

    # Group by the "group" column and calculate the required statistics
    summary_by_group = summary_by_case.groupby('group').agg(
        Number_Solved=('Num_Solutions', lambda x: (x > 0).sum()),
        Mean_Num_Solutions=('Num_Solutions', 'mean'),
        Mean_Novelty=('Novelty', 'mean'),
        Mean_Success_rate=('Success_Rate', 'mean')
    ).reset_index()

    # Rename columns to match the specified format
    summary_by_group.rename(columns={'group': 'Group'}, inplace=True)

    # Add summary row incorporating information across groups
    summary_by_group.loc[len(summary_by_group)] = {
        "Group": "overall",
        "Number_Solved": np.sum(summary_by_group["Number_Solved"]),
        "Mean_Num_Solutions": np.mean(summary_by_group["Mean_Num_Solutions"]),
        "Mean_Novelty": np.mean(summary_by_group["Mean_Novelty"]),
        "Mean_Success_rate": np.mean(summary_by_group["Mean_Success_rate"]),
    }

    # Compute the overall_score for all cases
    base_dir = "/".join(summary_by_case_file.split("/")[:-1])
    motifBenchScores = []
    for i, test_case in enumerate(test_cases.pdb_id):
        motif_name = f"{i+1:02d}_{test_case}"
        if len([s for s in summary_by_case.Problem if motif_name == s]) == 0:
            continue 
        div_cluster_path = diversity_cluster_path(base_dir, motif_name)
        successes_and_cluster = load_successes_and_cluster(div_cluster_path)
        motifBenchScore = MBScore_boostrap(successes_and_cluster)[0]
        motifBenchScores.append(motifBenchScore)
    summary_by_case['overall_score'] = np.array(motifBenchScores)
    overall_score = summary_by_case['overall_score'].mean()

    # Save the output to a new CSV file
    with open(summary_by_group_file, 'w') as f:
        summary_by_group.to_csv(f, float_format='%.2f', index=False)
        f.write(f"\nMotifBench score: {overall_score:.2f}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process test_cases and summary_by_case files to generate group-level statistics.")
    parser.add_argument("test_cases_file", help="Path to the test_cases.csv file")
    parser.add_argument("summary_by_case_file", help="Path to the summary_by_case.csv file")
    parser.add_argument("summary_by_group_file", help="Path to the summary_by_group.csv file")

    args = parser.parse_args()

    main(args.test_cases_file, args.summary_by_case_file, args.summary_by_group_file)
