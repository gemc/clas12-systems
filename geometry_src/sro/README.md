# FT-Cal streaming readout

**Upcoming in the next release.** `ft_cal.gplugin` exports both the detector digitizer and a
`GSROImplementationFactory`. GEMC's factory remains `sro`. Worker threads create owned JLAB integral
payloads; a separate thread for each crate assembles and writes its completed frames.

## Configure a run

Build against GEMC's current SRO interfaces, including `gSROImplementation.h`, and rebuild the CLAS12
plugins. From an environment already configured for the FT geometry, CCDB, and plugin search path, run:

```sh
gemc geometry_src/ft/ft.yaml -n=10000 \
  -gstreamer='[{format: sro, filename: ftcal_sro, implementation: ft_cal}]' \
  -eventTimeWidth='10*ns'
```

The 10 ns event width above is an example acquisition model, not a measured CLAS12 beam parameter.
Set it explicitly for your simulation; its default of zero rejects an SRO run. Ordinary output runs do
not require it. The FT bootstrap registrar `ft.gplugin` supplies the options for `ft_cal.gplugin`.
Output files are `<basename>_r<resolved_run>_crate<crate>.ev`. Reusing a basename/run overwrites those files.
Only FT-Cal currently supplies SRO payloads. The supplied old FT-Hodo and FT-MMTRK digitizers were empty,
with no streaming hook. Their normal digitization remains available, but no new SRO model is added for them.

## Sensitive identity and translation table

`FTCALDigitization::loadTTImpl` reads `/daq/tt/ftcal:1`, retaining the existing reference-run TT convention.
For each CCDB row it loads crate, slot, and channel from columns 0, 1, and 2, then converts column 5:

```cpp
const int ix = crystal % 22 + 1;
const int iy = crystal / 22 + 1;
table->addGElectronicWithIdentity({ix, iy},
    GElectronic(crate, slot, channel, GElectronic::ComparisonMode::crate));
```

This key matches the geometry's `{ih, iv}` identity and `hit->getTTID()`. Comparison mode `crate` is the
modern form of the old mode 0: the crate is the frame source, while the entry retains slot and channel.
Workers resolve this table directly; hardware addresses are never inferred from the crystal coordinates.

## Worker payload and timing

[IntegralPayload](jlab_sro.h) owns the legacy five values: crate, slot, channel, charge, and time.
The worker emits one integral per Geant4 hit, using the detector's existing hit integration window
(`ft_cal_timeWindow`, normally 400 ns). Charge uses the calibrated energy-to-ADC calculation from
`digitizeHitImpl`, truncates to an integer, and saturates at 8191 to fit the format's 13-bit charge field.
Zero-energy hits and hardware-disabled channels (when that policy is enabled) emit nothing.

Arrival time includes the hit's mean time, propagation to the crystal end, calibration offset, and Gaussian
resolution. It is converted to integral ns and added to `event_id * eventTimeWidth`.
The envelope carries absolute run time; the payload stores time relative to its 65536 ns frame.
The encoder quantizes that relative time to 4 ns. This is an integral-hit implementation; contributions from
separate hits/events remain separate. Pulse-shape sampling, overlap merging, and dead time are future work.

`ft_cal_sro_min_signal_time` defaults to -1000 ns and declares the minimum event-relative arrival time,
including generator timing and electronics corrections. A worker fails the run if a signal violates this
bound, rather than silently writing late data into an already completed frame. Gaussian smearing has
unbounded tails, so this is an enforced acquisition constraint, not a mathematical bound on the distribution.
Choose it for your source/calibration model. Nonfinite times and delays beyond 1e12 ns are also rejected.
Signals before acquisition time zero are discarded. Event spacing must be a positive integral number of ns.

The progress bound after events `[0, first)` are fully delivered is
`first * event_spacing + minimum_signal_time`. A crate writes a frame only when its end is at or before that
bound. Run completion does not extend the bound to infinity. Unfinished frames are discarded on normal or
interrupted shutdown; wholly empty frames are omitted. Sinks open, write, and close on their crate threads.

## Binary layout and compatibility

[jlab_sro.cc](jlab_sro.cc) uses the named DAQ header and setup in [daq/](daq/README.md). The required
JLAB definitions have been ported into the active implementation:

- File preamble: `0xC0DA2019`, `0xC0DA0001`, written once even if the first occupied frame is later than 1.
- Header: 52 bytes; source 0, payload/total lengths, magic, version 257, flags 0, and three 64-bit fields.
- Record counter: frame index + 1. Timestamp: frame end in ns, matching the legacy `counter * 65536` rule.
- Payload: `0x80000000`, 16 slot-directory words, and each occupied slot's marker plus hit words.
- Slot directory: `(word_count << 16) | offset`; count includes the marker, offset is from the payload start.
- Marker: `0x80008000 | (crate << 8) | slot`; the crate comes from the owning collector, fixing the old
  uninitialized/stale crate selection. Empty slots retain an offset with zero count.
- Integral word: `charge | (channel << 13) | ((time / 4) << 17)`.
- Payload and compressed lengths are identical byte counts; total length is payload bytes + 52 - 4.

Words are explicitly little-endian. The three 64-bit header values retain high-word-first ordering,
matching the old half-word swap on little-endian hosts. No packed-struct aliasing or host-endian writes are
used. Crates above 255, slots above 15, channels above 15, and overflowing slot directories fail explicitly.
The collector also limits each frame to 65500 samples. A different hardware layout needs a format extension;
it must not silently lose channels. File errors propagate through GEMC's SRO service.

This port has local format fixtures and an independent test decoder. Compatibility with a production JLAB
reader and real FT-Cal CCDB assignments still needs validation. See [DAQ documentation](daq/README.md)
for source provenance, the crate/slot-range discrepancy in the original definitions, and the procedure for
changing a DAQ definition. Obsolete source copies have been removed.

## Tests

```sh
meson test -C build --suite sro --print-errorlogs
```

`test_sro_jlab_format` checks fixed expected words, byte order, address/charge/time ranges, directory overflow,
exact frame boundaries, interrupted-tail discard, and file-open failure.

`sro_ftcal_full_path` creates a local synthetic CCDB database and two small crystal volumes. It exercises
real constant loading and `loadTTImpl`, worker payload creation, two crate files, and an independent binary
decoder. One and four workers must produce identical completed output; an extra partial frame must be
discarded. This test uses fixture calibrations and does not connect to a remote CCDB server.
