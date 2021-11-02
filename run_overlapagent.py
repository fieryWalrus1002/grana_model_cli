import argparse
import csv
from datetime import datetime
from pathlib import Path
from time import process_time

from src.grana_model.overlapagent import OverlapAgent, Rings
from src.grana_model.simulationenv import SimulationEnvironment


def write_to_log(log_path: str, row_data: list, mode: str = "a"):
    """exports progress data for a job to csv"""
    with open(log_path, mode) as fd:
        write = csv.writer(fd)
        write.writerow(row_data)


def get_log_path(job_id: int):
    """uses the job_id and date to create output log file"""
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y_%H%M%S")
    return Path.cwd() / "log" / f"{dt_string}_{job_id}.csv"


def export_coordinates(job_id, step_num, zone_list, mean_overlap):
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y_%H%M%S")
    filename = (
        Path.cwd()
        / "output"
        / f"{dt_string}_jobid_{job_id}_step_{step_num}_overlap_{int(mean_overlap)}_data.csv"
    )

    with open(filename, "w", newline="") as f:
        write = csv.writer(f)
        # write the headers
        write.writerow(["type", "x", "y", "angle", "area"])
        for object in zone_list:
            write.writerow(
                (
                    object.type,
                    round(object.body.position[0], 2),
                    round(object.body.position[1], 2),
                    round(object.body.angle, 2),
                    round(object.area, 2),
                )
            )


def get_overlap_reduction_percent(overlap_begin, overlap_end):
    """ calculate and return the percent reduction from this iteration """
    return round(
        (overlap_begin - overlap_end) / (overlap_begin + 0.0001) * 100, 2
    )


def main(
    slurm_job_id,
    filename: str,
    num_loops: int = 100,
    object_data_exists: bool = False,
    actions_per_zone: int = 500,
):
    job_id = str(slurm_job_id)
    # print(f"job_id={job_id}")
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
        job_id=job_id,
    )

    _init_overlap = overlap_agent._update_space()

    log_path = get_log_path(str(job_id))
    # print(f"log_path: {log_path}")

    write_to_log(
        log_path=log_path,
        mode="w",
        row_data=[
            "datetime",
            "job_id",
            "step_num",
            "total_actions",
            "overlap_pct",
            "overlap",
            "process_time",
        ],
    )

    for step_num in range(0, num_loops):
        start_time = process_time()

        object_list_p, overlap_begin, overlap_end = overlap_agent.run(
            num_actions=actions_per_zone, step_num=step_num
        )

        write_to_log(
            log_path=log_path,
            mode="a",
            row_data=[
                datetime.now().strftime("%d/%m/%Y_%H:%M:%S"),
                job_id,
                step_num,
                (
                    overlap_agent.num_actions
                    * overlap_agent.area_strategy.total_zones
                ),
                get_overlap_reduction_percent(overlap_begin, overlap_end),
                overlap_end,
                round(process_time() - start_time, 3),
            ],
        )

        export_coordinates(job_id, step_num, object_list_p, overlap_end)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="launches an overlap agent run"
    )

    parser.add_argument("-slurm_job_id", help="job array number for SLURM run")

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
