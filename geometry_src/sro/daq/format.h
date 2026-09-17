#pragma once

#include "data_frame_header.h"
#include <array>
#include <limits>
#include <stdexcept>

namespace clas12::sro::daq {

// Fixed DAQ/setup values are centralized here, independently of GEMC's crate transport.
inline constexpr std::uint32_t magic = 0xC0DA2019;
inline constexpr std::uint32_t super_magic = 0xC0DA0001;
inline constexpr std::uint32_t format_version = 257;
inline constexpr std::uint32_t header_bytes = sizeof(DataFrameHeader);
inline constexpr std::uint32_t frame_duration_ns = 65536;
inline constexpr std::uint32_t time_tick_ns = 4;
inline constexpr std::uint32_t max_charge = 8191;
inline constexpr std::uint32_t max_channel = 15;
// Preserve the legacy writer range. The DAQ note describes a 7-bit rocid: see README before changing it.
inline constexpr std::uint32_t max_crate = 255;
inline constexpr std::uint32_t slot_count = 16; // Preserved legacy directory (DAQ marker allows 5 slot bits).

struct HeaderSettings {
    std::uint32_t source_id = 0;
    std::uint32_t magic = daq::magic;
    std::uint32_t format_version = daq::format_version;
    std::uint32_t flags = 0;
};

// Host-order values for inspection and modification. Byte order is applied only by encode_header/the sink.
inline DataFrameHeader setup_frame_header(std::uint32_t payload_bytes, std::uint64_t counter,
                                         std::uint64_t timestamp_ns, HeaderSettings settings = {}) {
    if (payload_bytes > std::numeric_limits<std::uint32_t>::max() - header_bytes + 4) {
        throw std::overflow_error("JLAB SRO frame length overflow");
    }
    DataFrameHeader header{};
    header.source_id = settings.source_id;
    header.total_length = payload_bytes + header_bytes - 4; // Original DAQ/legacy length convention.
    header.payload_length = payload_bytes;
    header.compressed_length = payload_bytes;
    header.magic = settings.magic;
    header.format_version = settings.format_version;
    header.flags = settings.flags;
    header.record_counter = counter;
    header.ts_sec = timestamp_ns / 1000000000;
    header.ts_nsec = timestamp_ns % 1000000000;
    return header;
}

// Seven 32-bit fields followed by three high-word-first 64-bit fields, matching legacy llswap.
// The sink emits each returned word little-endian. No packed member addresses or type-punning are used.
inline std::array<std::uint32_t, header_bytes / 4> encode_header(const DataFrameHeader& header) {
    return {header.source_id, header.total_length, header.payload_length, header.compressed_length,
            header.magic, header.format_version, header.flags,
            static_cast<std::uint32_t>(header.record_counter >> 32),
            static_cast<std::uint32_t>(header.record_counter),
            static_cast<std::uint32_t>(header.ts_sec >> 32), static_cast<std::uint32_t>(header.ts_sec),
            static_cast<std::uint32_t>(header.ts_nsec >> 32), static_cast<std::uint32_t>(header.ts_nsec)};
}

} // namespace clas12::sro::daq
