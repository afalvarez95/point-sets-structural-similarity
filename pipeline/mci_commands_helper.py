from config import (PROJECT_ROOT,
MCIHELP__POINT_CLOUD_FOLDER,
MCIHELP__OUTPUT_FOLDER,
MCIHELP__SET_TYPE,
MCIHELP__N_BATCHES,
MCIHELP__MIN_RADIUS,
MCIHELP__MAX_RADIUS,
MCIHELP__RADIUS_STEP)

#This file prints one mci_process.py command per batch, so each batch can be copied and run separately.

MCI_PROCESS_SCRIPT = PROJECT_ROOT / "mci_lib" / "processes" / "mci_process.py"

for batch_index in range(MCIHELP__N_BATCHES):
    print(f"Batch {batch_index}")
    print(f'python "{MCI_PROCESS_SCRIPT}" "{MCIHELP__POINT_CLOUD_FOLDER}" {MCIHELP__N_BATCHES} {batch_index} '
          f'{MCIHELP__MIN_RADIUS} {MCIHELP__MAX_RADIUS} {MCIHELP__RADIUS_STEP} "{MCIHELP__SET_TYPE}" "{MCIHELP__OUTPUT_FOLDER}"')
    print()
