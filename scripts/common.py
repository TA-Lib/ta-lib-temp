import os
import subprocess
import sys

def verify_git_repo() -> str:
    # Verify that the script is called from within a ta-lib git repos, and if yes
    # change the working directory to the root of it.
    #
    # That root path is returned.
    try:
        subprocess.run(['git', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("Git is not installed. Please install Git and try again.")
        sys.exit(1)

    error = False
    try:
        result = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stdout.strip() == b'true':
            # Change to the root directory of the Git repository
            root_dir = subprocess.run(['git', 'rev-parse', '--show-toplevel'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.strip().decode('utf-8')
            os.chdir(root_dir)
            return root_dir
        else:
            error = True
    except subprocess.CalledProcessError:
        error = True

    if error:
        print("Must run this script while the current directory is in a TA-Lib Git repository.")
        sys.exit(1)

    # Sanity check that src/ta_func exists.
    if not os.path.isdir('src/ta_func'):
        print("Current directory is not a TA-Lib Git repository (src/ta_func missing)")
        sys.exit(1)

def get_version_string(root_dir: str) -> str:
    """
    Parse the file src/ta_common/ta_version.c to build a version string.

    The file contains the following C definitions:
        #define MAJOR "0"
        #define MINOR "6"
        #define BUILD "0"
        #define EXTRA "dev"

    These become the string "0.6.0-dev".
    """
    version_info = {}
    version_file_path = os.path.join(root_dir, 'src/ta_common/ta_version.c')
    with open(version_file_path) as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('#define'):
                parts = line.split()
                if len(parts) == 3:
                    key = parts[1]
                    value = parts[2].strip('"')
                    version_info[key] = value

    # Check if MAJOR, MINOR, and BUILD are defined
    if 'MAJOR' not in version_info or 'MINOR' not in version_info or 'BUILD' not in version_info:
        print("Error: MAJOR, MINOR, and BUILD must be defined in src/ta_common/ta_version.h")
        sys.exit(1)

    version_string = f"{version_info.get('MAJOR', '0')}.{version_info.get('MINOR', '0')}.{version_info.get('BUILD', '0')}"
    if 'EXTRA' in version_info and version_info['EXTRA']:
        version_string += f"-{version_info['EXTRA']}"

    return version_string

