import argparse
import csv
from datetime import datetime
from pathlib import Path

from src.grana_model.simulationenv import SimulationEnvironment
from src.grana_model.overlapagent import OverlapAgent, Rings


def write_to_log(log_path: str, row_data: list):
    """exports progress data for a job to csv"""
    with open(log_path, "a") as fd:
        write = csv.writer(fd)
        write.writerow(row_data)


def get_log_path(batch_num: int,):
    """uses the batch_num and date to create output log file"""
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y_%H%M%S")
    return (
        Path.cwd()
        / "src"
        / "grana_model"
        / "res"
        / "log"
        / f"{dt_string}_{batch_num}.csv"
    )


def main(
    batch_num: int,
    filename: str,
    num_loops: int = 100,
    object_data_exists: bool = False,
    actions_per_zone: int = 500,
):

    sim_env = SimulationEnvironment(
        # pos_csv_filename="16102021_083647_5_overlap_66_data.csv",
        pos_csv_filename=filename,
        object_data_exists=object_data_exists,
    )

    object_list, _ = sim_env.spawner.setup_model()

    overlap_agent = OverlapAgent(
        object_list=object_list,
        area_strategy=Rings(object_list, origin_point=(200, 200)),
        collision_handler=sim_env.collision_handler,
        space=sim_env.space,
    )

    overlap_agent._update_space()

    log_path = get_log_path(batch_num)
    print(f"log_path: {log_path}")

    write_to_log(
        log_path=log_path,
        row_data=[
            "datetime",
            "batch_num",
            "t_idx",
            "total_actions",
            "overlap_pct",
            "overlap",
        ],
    )

    time_limits = [actions_per_zone for _ in range(0, num_loops)]

    for t_idx, time_limit in enumerate(time_limits):

        overlap_agent.time_limit = time_limit

        action_limit = overlap_agent.time_limit * 5

        # max_time = action_limit / 20

        # t1 = process_time()

        overlap_results = overlap_agent.run(debug=False)

        # elapsed_time = process_time() - t1

        overlap_begin = sum(overlap_results[0:9]) / 10
        overlap_end = sum(overlap_results[-10:-1]) / 10
        overlap_reduction_percent = (
            (overlap_begin - overlap_end) / (overlap_begin + 0.1)
        ) * 100

        write_to_log(
            log_path=log_path,
            row_data=[
                datetime.now(),
                batch_num,
                t_idx,
                (action_limit * overlap_agent.area_strategy.total_zones),
                round(overlap_reduction_percent, 2),
                overlap_end,
            ],
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="launches an overlap agent run"
    )

    parser.add_argument(
        "-batch_num",
        help="job batch number for SLURM run",
        type=int,
        default=0,
    )

    parser.add_argument(
        "-filename",
        help="filename of csv position datafile in res/grana_coordinates/",
        type=str,
        default="082620_SEM_final_coordinates.csv",
    )

    parser.add_argument(
        "-num_loops",
        help="number of times the overlap agent will loop through the zones",
        type=int,
        default=10000,
    )

    parser.add_argument(
        "-object_data_exists",
        help="object data exists. False: generate new object types for XY coordinates. True: load xy, object type, angle from datafile",
        type=bool,
        default=False,
    )

    parser.add_argument(
        "-actions_per_zone",
        help="perform this many actions before moving to next zone",
        type=int,
        default=500,
    )

    args = parser.parse_args()

    main(**vars(args))
