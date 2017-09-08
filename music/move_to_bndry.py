#!/home/lbignone/anaconda/bin/python

from pygadget import Simulation
from struct import pack
import sys

particle_keys = [
            "gas",
            "halo",
            "disk",
            "buldge",
            "stars",
            "bndry",
        ]

types_n = len(particle_keys)


def main(fname):

    snap = Simulation(fname, skip_file_check=True)

    n_destination = snap.particle_total_numbers['bndry']
    if n_destination != 0.0:
        print("Error: bndry is not empty")
        return 1

    for i, key in enumerate(particle_keys[::-1]):
        n = snap.particle_total_numbers[key]
        mass = snap.particle_mass[key]
        final_key = key
        if n != 0:
            break

    print("Moving {:s} to bndry".format(key))

    snap.particle_numbers[final_key] = 0
    snap.particle_total_numbers[final_key] = 0
    snap.particle_mass[final_key] = 0

    snap.particle_numbers["bndry"] = n
    snap.particle_total_numbers["bndry"] = n
    snap.particle_mass["bndry"] = mass

    with open(fname, 'r+b') as f:
        f.seek(4, 0)  # header int
        for key in particle_keys:
            data = pack('I', snap.particle_numbers[key])
            f.write(data)

        for key in particle_keys:
            data = pack('d', snap.particle_mass[key])
            f.write(data)

        skip = 4  # header int
        skip += types_n*4  # Npart
        skip += types_n*8  # Massarr
        skip += 8  # Time
        skip += 8  # Redshift
        skip += 4  # FlagSfr
        skip += 4  # FlagFeedback
        f.seek(skip, 0)
        for key in particle_keys:
            data = pack('I', snap.particle_total_numbers[key])
            f.write(data)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: move_to_bndry <fname>")
    main(sys.argv[1])
