import sys

task_specs = {
    "1": {
        "uid_range": (80000, 100000),
        "d_min": 60,
        "d_max": 74,
        "t_min": 0,
        "t_max": 47,
        "coord_min": 1,
        "coord_max": 200,
    },
    "2": {
        "uid_range": (22500, 25000),
        "d_min": 60,
        "d_max": 74,
        "t_min": 0,
        "t_max": 47,
        "coord_min": 1,
        "coord_max": 200,
    },
}

def error(message):
    print(message)
    sys.exit(1)

def main():
    # parse the arguments
    if len(sys.argv) != 3:
        error(
            "Usage: \n"
            "    python3 validator.py task_id submission_file_path\n"
            "        where task_id is either 1 or 2")

    task_id = sys.argv[1]
    fpath = sys.argv[2]

    if task_id not in task_specs.keys():
        error("Invalid task_id: {}".format(task_id))

    # retrieve the corresponding task specifications
    specs = task_specs[task_id]

    uid_range = specs["uid_range"]
    d_min = specs["d_min"]
    d_max = specs["d_max"]
    t_min = specs["t_min"]
    t_max = specs["t_max"]
    coord_min = specs["coord_min"]
    coord_max = specs["coord_max"]

    # prepare the reference set of uid's
    uid_set_ref = set()
    for uid in range(*specs["uid_range"]):
        uid_set_ref.add(uid)

    # now start the actual test...
    uid_set = set()

    for i, l in enumerate(open(fpath)):
        if i == 0 and l.startswith("uid,"):
            # skip the header line
            continue
        cols = l.rstrip().split(",")

        error_prefix = "Error at line index {}: ".format(i)

        # the number of columns
        if len(cols) != 5:
            error(
                error_prefix + \
                "The number of columns must be 5")

        # each column must be numeric
        for c in cols:
            if not c.isnumeric():
                error(
                    error_prefix + \
                    "Each column must be numeric")

        # convert the columns
        uid_str, d_str, t_str, x_str, y_str = cols
        uid = int(uid_str)
        d = int(d_str)
        t = int(t_str)
        x = int(x_str)
        y = int(y_str)

        # remember the uid
        uid_set.add(uid)

        # range check
        if d < d_min or d > d_max:
            error(
                error_prefix + \
                "d={} is out of range".format(d))
        if t < t_min or t > t_max:
            error(
                error_prefix + \
                "t={} is out of range".format(t))
        if x < coord_min or x > coord_max:
            error(
                error_prefix + \
                "x={} is out of range".format(x))
        if y < coord_min or y > coord_max:
            error(
                error_prefix + \
                "y={} is out of range".format(y))

    # uid check
    if uid_set != uid_set_ref:
        error(
            "The set of uid's doesn't match that of reference; "
            "there seem to be extra or lacking uid's")

    print("Validation finished without errors!")

if __name__ == "__main__":
    main()
