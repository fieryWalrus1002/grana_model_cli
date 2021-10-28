import argparse

parser = argparse.ArgumentParser()

parser.add_argument("job_id", help="job number in slurm")

args = parser.parse_args()

print(f"{args.job_id} says ni!")
