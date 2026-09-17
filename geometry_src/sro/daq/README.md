# DAQ declarations and format setup

This directory contains the DAQ declarations and setup used by the current encoder. The obsolete streamer,
translator example, and empty detector stubs are not part of this implementation.

- [data_frame_header.h](data_frame_header.h) retains the named `DataFrameHeader` declaration, fixed-width
  field types, packing, and compile-time size/offset checks. The header is 52 bytes, not a naturally padded
  native struct. Field names match the original source.
- [format.h](format.h) centralizes the preamble, version, frame duration, quantization, and supported ranges.
  `HeaderSettings` supplies source ID, magic, version, and flags; `setup_frame_header` fills the named length,
  counter, and timestamp fields in host order. `encode_header` applies the original field/word ordering.
- [jlab_sro.cc](../jlab_sro.cc) builds slot directories and integral words, calls header setup/serialization,
  and writes each 32-bit word little-endian. It never dumps packed native memory to disk.

A crate implementation can pass `daq::HeaderSettings` to `create_crate(crate, filename, settings)`; omitted
settings preserve source 0, magic 0xC0DA2019, version 257, and flags 0. This is a C++ setup interface, not a
new YAML option. The file handshake constants are separate from per-frame header settings.

## Changing a DAQ definition

1. Record the new DAQ definition and its source in this documentation; port the required fields and setup.
2. Update the explicit header declaration and its size/offset assertions to match that definition.
3. Update `setup_frame_header` and `encode_header` together: declaration changes alone must not silently
   produce a different wire layout. Counter/timestamp values stay in host order until encoding.
4. Update format constants and payload assembly only if that DAQ version changes their contract. Review
   frame timing and payload units together when changing the frame duration or time quantization.
5. Update independent byte fixtures and run the format and full FT-Cal tests. Revalidate with the target
   DAQ reader before claiming compatibility with a changed version.

## Sources and port decisions

The header and encoding were ported from GEMC's former `gemc/gstreamer/factories/JLABSRO` backend, available
in GEMC Git history at revision `b0d52efc88707dd091bb0678d76a4bfedb96a313`. The original DAQ note and translator
are in the separate `gemc/streaming` repository as `docs/meetings/codaSRO.txt` and
`docs/meetings/coda_sro_waveboard_translator.cc`. That note describes `CODA_SRO_Header_t`, the preamble, and
FADC hit words. Their required header, setup, and serialization are implemented here; copies of the old
programs are unnecessary.

The supplied `clas12-oldsystems/ft/plugin` code calls `chargeAndTimeAtHardware(timeR, ADC, ghit, gdata)` only
for FT-Cal. Its translation table uses `{ix, iy}` and crate comparison mode. FT-Hodo has a TT loader but an
empty digitizer; FT-MMTRK's digitizer is also empty. Neither supplied an SRO response, so neither is added.

### Format differences requiring validation

The former GEMC writer uses a 16-slot directory and accepts an eight-bit crate field. The original DAQ
note instead describes a five-bit slot and a seven-bit rocid (bits 14:8), with bit 15 belonging to the type.
The current port retains the existing writer's accepted ranges and does not infer a new layout from this
incomplete evidence. Production use of crates above 127, directory interpretation, and the old total-length
convention still require reader validation. Neither source defines an FT-TRK streaming payload.

The original FT-Cal helper uses the local X coordinate in its longitudinal delay calculation; the current
FT-Cal implementation uses local Z consistently with its normal digitizer. This is an existing port
difference, not a new detector response introduced during the SRO migration.
