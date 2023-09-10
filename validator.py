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
    "test": {
        "uid_range": (50, 60),
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

def load_dataset(fpath, specs):
    uid_dict = dict()
    for l in open(fpath):
        if l.startswith("uid"):
            continue
        l = l.rstrip()
        uid_str, d_str, t_str, x_str, y_str = l.split(",")
        uid = int(uid_str)
        if uid < specs["uid_range"][0]:
            continue
        d = int(d_str)
        t = int(t_str)
        x = int(x_str)
        y = int(y_str)

        if uid not in uid_dict.keys():
            uid_dict[uid] = list()
        if d >= specs["d_min"]:
            uid_dict[uid].append((d, t, x, y))

    return uid_dict

def check_consistency(pred_seq, ans_seq, uid):
    # check the consistency between a trajectory in prediction and its counterpart in reference
    error_prefix = "Error occurring regarding uid {}: ".format(uid)

    # the trajectory length
    if len(pred_seq) != len(ans_seq):
        error(
            error_prefix + \
            "The length doesn't match between the generated and reference trajectories.")

    # consistency of day and time
    for idx, (pred_step, ans_step) in enumerate(zip(pred_seq, ans_seq)):
        pred_d, pred_t = pred_step[:2]
        ans_d, ans_t = ans_step[:2]
        if not (pred_d == ans_d and pred_t == ans_t):
            error(
                error_prefix + \
                "Day and time are not the same; "
                "(d, t) = ({}, {}) for generated while (d, t) = ({}, {}) for reference at step {} of the trajectory.".format(
                    pred_d, pred_t, ans_d, ans_t, idx))

def main():
    # parse the arguments
    if len(sys.argv) != 4:
        error(
            "Usage: \n"
            "    python3 validator.py task_id dataset_file_path submission_file_path\n"
            "        where task_id is either 1 or 2")

    task_id = sys.argv[1]
    dataset_fpath = sys.argv[2]
    generated_fpath = sys.argv[3]

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
    pred_uid_dict = dict()
    ans_uid_dict = dict()

    print("Loading the submission file...")
    for i, l in enumerate(open(generated_fpath)):
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

        if uid not in pred_uid_dict.keys():
            pred_uid_dict[uid] = list()
        pred_uid_dict[uid].append((d, t, x, y))
    print("")

    # uid check
    print("Checking the set of uid's...")
    if uid_set != uid_set_ref:
        error(
            "The set of uid's doesn't match that of reference; "
            "there seem to be extra or lacking uid's")
    print("")

    # comparison between the submission file and the dataset
    print("Now loading the dataset file and comparing the submission data to it...")
    ans_uid_dict = load_dataset(dataset_fpath, specs)
    for uid in range(specs["uid_range"][0], specs["uid_range"][1]):
        pred_seq = pred_uid_dict[uid]
        ans_seq = ans_uid_dict[uid]
        check_consistency(pred_seq, ans_seq, uid)
    print("")


    print("Validation finished without errors!")

if __name__ == "__main__":
    main()
