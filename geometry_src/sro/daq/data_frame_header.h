#pragma once

#include <cstddef>
#include <cstdint>
#include <type_traits>

namespace clas12::sro::daq {

// DAQ field declaration ported from the original CODA SRO/GEMC definitions. See README.md for provenance.
// Packing describes the wire layout; output still serializes each integer explicitly, never native memory.
#pragma pack(push, 1)
struct DataFrameHeader
{
    uint32_t source_id;
    uint32_t total_length;
    uint32_t payload_length;
    uint32_t compressed_length;
    uint32_t magic;
    uint32_t format_version;
    uint32_t flags;
    uint64_t record_counter;
    uint64_t ts_sec;
    uint64_t ts_nsec;
};
#pragma pack(pop)

// Changing the DAQ declaration requires reviewing setup_frame_header, encode_header, and byte fixtures.
// Fail compilation if a field is inserted/reordered without an explicit wire-format update.
static_assert(std::is_standard_layout_v<DataFrameHeader>);
static_assert(sizeof(DataFrameHeader) == 52);
static_assert(offsetof(DataFrameHeader, source_id) == 0);
static_assert(offsetof(DataFrameHeader, total_length) == 4);
static_assert(offsetof(DataFrameHeader, payload_length) == 8);
static_assert(offsetof(DataFrameHeader, compressed_length) == 12);
static_assert(offsetof(DataFrameHeader, magic) == 16);
static_assert(offsetof(DataFrameHeader, format_version) == 20);
static_assert(offsetof(DataFrameHeader, flags) == 24);
static_assert(offsetof(DataFrameHeader, record_counter) == 28);
static_assert(offsetof(DataFrameHeader, ts_sec) == 36);
static_assert(offsetof(DataFrameHeader, ts_nsec) == 44);

} // namespace clas12::sro::daq
