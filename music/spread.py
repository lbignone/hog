#!/home/lbignone/anaconda/bin/python

from pygadget import Simulation
from struct import pack, unpack
import sys

from numpy import fromstring

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

    fname2 = fname.split('.')[0] + '_spread.' + fname.split('.')[1]
    # fname2 = fname.split('.')[0] + '.' + fname.split('.')[1]

    snap = Simulation(fname, skip_file_check=True)

    mass = snap.read_block("mass", "bndry")

    g = mass.groupby("mass")

    mass_values = g.size().index

    n = g.size().values

    snap.particle_numbers['disk'] = n[0]
    snap.particle_numbers['buldge'] = n[1:-1].sum()
    snap.particle_numbers['bndry'] = n[-1]

    snap.particle_mass['disk'] = mass_values[0]
    snap.particle_mass['bndry'] = mass_values[-1]

    n_block_mass = 4

    with open(fname, 'rb') as f:
        with open(fname2, 'wb') as f_out:
            for i in range(n_block_mass+1):

                block_size = f.read(4)
                size = unpack('i', block_size)[0]
            
                data = f.read(size)
            
                block_size2 = f.read(4)
                size2 = unpack('i', block_size2)[0]

                assert size == size2

                if i == n_block_mass:
                    skip = (n[0])*4
                    lim = (n[0:-1].sum())*4
                    data = data[skip:lim]

                    assert len(data) == n[1:-1].sum()*4

                    block_size = pack('I', len(data))
                    block_size2 = block_size

                f_out.write(block_size)
                f_out.write(data)
                f_out.write(block_size2)

    with open(fname2, 'r+b') as f_out:
        f_out.seek(4, 0)  # header int
        for key in particle_keys:
            data = pack('I', snap.particle_numbers[key])
            f_out.write(data)

        for key in particle_keys:
            data = pack('d', snap.particle_mass[key])
            f_out.write(data)

        skip = 4  # header int
        skip += types_n*4  # Npart
        skip += types_n*8  # Massarr
        skip += 8  # Time
        skip += 8  # Redshift
        skip += 4  # FlagSfr
        skip += 4  # FlagFeedback
        f_out.seek(skip, 0)
        for key in particle_keys:
            data = pack('I', snap.particle_numbers[key])
            f_out.write(data)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: spread <fname>")
    main(sys.argv[1])





