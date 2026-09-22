import argparse, subprocess, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from mci_lib.processes.mci_process import DatasetType, mci_process
import traceback

#TODO
#COMMAND to cast in root folder with prepared env
#python -m pipeline.mci_scheduler <folder> 10 10 20 2 "Permutation"



HERE = Path(__file__).resolve().parent
mci_script = (HERE / "../lib/processes/mci_process.py").resolve()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder",type=str)
    parser.add_argument("n_batches", type=int)
    parser.add_argument("min_radius",type=int)
    parser.add_argument("max_radius",type=int)
    parser.add_argument("radius_step",type=int)
    parser.add_argument("dataset_type",type=DatasetType)
    parser.add_argument("output_folder",type=str)
    #n_batches, i, min_radius, max_radius, radius_step = [int(sys.argv[i]) for i in range(2,7)]
    #Options for the type of dataset: if it's perturbation, rigid, or both.
    #dataset_type = str(sys.argv[7])


    parser.add_argument("--workers", type=int, help="How many run at once (default is all)")
    a = parser.parse_args()

    folder = str(Path(a.folder).resolve())

    with ProcessPoolExecutor(max_workers=a.workers or a.n_batches) as ex:
        futures = {ex.submit(mci_process, folder, a.n_batches, i, a.min_radius, a.max_radius, a.radius_step, a.dataset_type, a.output_folder): i for i in range(a.n_batches)}

        for fut in as_completed(futures):
            i = futures[fut]
            try:
                res = fut.result()
                print(f"Batch {i}: {res['ok']} ok, {len(res['failed'])} failed")
            except Exception as e:
                print(f"Batch {i} crashed: {e!r}", file=sys.stderr)
                traceback.print_exc()

if __name__ == "__main__":
    main()