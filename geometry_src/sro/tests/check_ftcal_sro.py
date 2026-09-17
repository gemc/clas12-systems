#!/usr/bin/env python3
"""Offline full path: synthetic CCDB -> real loadTTImpl -> FT-Cal workers -> decoded JLAB crate files."""

import os
from pathlib import Path
import sqlite3
import struct
import subprocess
import sys
import tempfile

from pygemc import GVolume, autogeometry


def geometry():
    # No detector geometry changes: use two small, independently addressed crystals as the test fixture.
    cfg = autogeometry("clas12", "ft")
    world = GVolume("root")
    world.make_box(50, 50, 60)
    world.material = "G4_Galactic"
    world.publish(cfg)
    for ix in (1, 2):
        crystal = GVolume(f"crystal{ix}")
        crystal.mother = "root"
        crystal.make_box(5, 5, 0.05)
        crystal.set_position(0, 0, 10 * ix)
        crystal.material = "G4_PbWO4"
        crystal.digitization = "ft_cal"
        crystal.set_identifier("ih", ix, "iv", 1)
        crystal.publish(cfg)


def calibration(schema, destination):
    with sqlite3.connect(f"file:{schema}?mode=ro", uri=True) as source:
        with sqlite3.connect(destination) as db:
            source.backup(db)
            next_id = 100000
            directories = {}

            def directory(path):
                nonlocal next_id
                if not path:
                    return 0
                if path not in directories:
                    parent, _, name = path.rpartition("/")
                    parent_id = directory(parent)
                    next_id += 1
                    directories[path] = next_id
                    db.execute('INSERT INTO directories(id,name,parentId) VALUES(?,?,?)',
                               (next_id, name, parent_id))
                return directories[path]

            def table(path, rows):
                nonlocal next_id
                parent, _, name = path.rpartition("/")
                parent_id = directory(parent)
                next_id += 1
                tid = next_id
                db.execute('INSERT INTO typeTables(id,directoryId,name,nRows,nColumns,nAssignments) '
                           'VALUES(?,?,?,?,?,1)', (tid, parent_id, name, len(rows), len(rows[0])))
                for col in range(len(rows[0])):
                    next_id += 1
                    db.execute('INSERT INTO columns(id,name,typeId,columnType,"order") VALUES(?,?,?,?,?)',
                               (next_id, f"c{col}", tid, "double", col))
                db.execute('INSERT INTO constantSets(id,vault,constantTypeId) VALUES(?,?,?)',
                           (tid, "|".join(str(v) for row in rows for v in row), tid))
                db.execute('INSERT INTO runRanges(id,runMin,runMax) VALUES(?,0,2147483647)', (tid,))
                db.execute('INSERT INTO assignments(id,variationId,runRangeId,constantSetId) VALUES(?,1,?,?)',
                           (tid, tid, tid))

            table('daq/tt/ftcal', [[11, 3, 4, 1, 0, 0, 0], [12, 3, 5, 1, 0, 1, 0]])
            table('calibration/ft/ftcal/noise', [[1, 0, c, 0, 0, 0, 0, 0] for c in (0, 1)])
            table('calibration/ft/ftcal/charge_to_energy', [[1, 0, c, 1, 1, 0.001, 1, 1] for c in (0, 1)])
            table('calibration/ft/ftcal/time_offsets', [[1, 0, c, 10, 0] for c in (0, 1)])


def decode(path, crate, complete_frames):
    content = path.read_bytes()
    assert len(content) % 4 == 0
    words = struct.unpack('<' + 'I' * (len(content) // 4), content)
    assert words[:2] == (0xC0DA2019, 0xC0DA0001)
    pos, records = 2, []
    while pos < len(words):
        header = words[pos:pos + 13]
        assert len(header) == 13 and header[0] == 0 and header[4:7] == (0xC0DA2019, 257, 0)
        assert header[1] == header[2] + 48 and header[2] == header[3] and header[2] % 4 == 0
        record = (header[7] << 32) | header[8]
        timestamp = ((header[9] << 32) | header[10]) * 1000000000 + ((header[11] << 32) | header[12])
        assert timestamp == record * 65536 and 1 <= record <= complete_frames
        payload = words[pos + 13:pos + 13 + header[2] // 4]
        assert len(payload) == header[2] // 4 and payload[0] == 0x80000000
        samples = 0
        for slot, entry in enumerate(payload[1:17]):
            count, offset = entry >> 16, entry & 65535
            assert offset <= len(payload)
            if count:
                assert slot == 3 and offset + count <= len(payload)
                assert payload[offset] == 0x80008000 | (crate << 8) | slot
                for word in payload[offset + 1:offset + count]:
                    assert (word >> 13) & 15 == crate - 7  # TT: crate 11/channel 4, crate 12/channel 5.
                    assert 0 <= word & 8191 <= 8191
                    assert ((word >> 17) & 32767) * 4 < 65536
                    samples += 1
        assert samples > 0
        records.append(record)
        pos += 13 + header[2] // 4
    assert records == list(range(1, complete_frames + 1)), records
    return content


def main():
    gemc, plugins, schema = (Path(arg).resolve() for arg in sys.argv[1:])
    with tempfile.TemporaryDirectory(prefix="ftcal-sro-run-") as temp:
        directory = Path(temp)
        subprocess.run([sys.executable, str(Path(__file__).resolve()), '--geometry', '-f', 'ascii'],
                       cwd=directory, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        calibration(schema, directory / 'ccdb.sqlite')
        env = dict(os.environ, CCDB_CONNECTION='sqlite:///' + str(directory / 'ccdb.sqlite'))
        card = directory / 'ft.yaml'
        card.write_text("""experiment: clas12
runno: 1
seed: 12345
no_true_info: all
gsystem: [{name: ft, factory: ascii}]
gstreamer: [{format: sro, filename: ftcal, implementation: ft_cal}]
eventTimeWidth: 32768*ns
ft_cal_sro_min_signal_time: 0
phys_list: QBBC
gparticle: [{name: e-, p: 1*GeV, theta: 0*deg}]
""")
        reference = None
        for workers, events in ((1, 8), (4, 8), (4, 9), (4, 1)):
            base = directory / f'ftcal_w{workers}_n{events}'
            output = f"[{{format: sro, filename: '{base}', implementation: ft_cal}}]"
            result = subprocess.run([str(gemc), str(card), f'-plugin_path={plugins}',
                                     f'-nthreads={workers}', f'-n={events}', f'-gstreamer={output}'],
                                    cwd=directory, env=env, text=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, timeout=60)
            assert result.returncode == 0, result.stdout[-8000:]
            found = sorted(directory.glob(base.name + '*.ev'))
            expected = [Path(f'{base}_r1_crate{crate}.ev') for crate in (11, 12)]
            assert found == expected, found
            contents = [decode(path, crate, events // 2) for path, crate in zip(found, (11, 12))]
            if reference is None:
                reference = contents
            elif events >= 8:
                assert contents == reference, 'Worker scheduling or tail changed the completed binary frames'
        result = subprocess.run([str(gemc), str(card), f'-plugin_path={plugins}', '-n=1',
                                 '-eventTimeWidth=0*ns'], cwd=directory, env=env, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
        assert result.returncode != 0 and 'eventTimeWidth' in result.stdout, result.stdout[-4000:]
    print('FTCAL CCDB-to-worker-to-JLAB output checks passed (one/four workers, mapping, frames and tail).')


if __name__ == '__main__':
    if '--geometry' in sys.argv:
        sys.argv.remove('--geometry')
        geometry()
    else:
        main()
