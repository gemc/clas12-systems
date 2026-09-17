#pragma once

#include <gemc/gstreamer/sro/gSROCrate.h>
#include "daq/format.h"
#include <cstdint>
#include <string>
#include <vector>

namespace clas12::sro {

inline constexpr GSROTime frame_duration{daq::frame_duration_ns};
inline constexpr auto magic = daq::magic;
inline constexpr auto super_magic = daq::super_magic;
inline constexpr auto format_version = daq::format_version;
inline constexpr auto header_bytes = daq::header_bytes;

// Logical JLAB integral payload: electronics address, 13-bit charge, and frame-relative time in ns.
// Time is quantized to 4 ns only when encoding. The GSROPayload envelope carries absolute run time.
struct IntegralPayload final : GSROData {
    IntegralPayload(std::uint32_t c, std::uint32_t s, std::uint32_t ch,
                    std::uint32_t q, std::uint32_t t) : crate(c), slot(s), channel(ch), charge(q), time(t) {}
    std::uint32_t crate;
    std::uint32_t slot;
    std::uint32_t channel;
    std::uint32_t charge;
    std::uint32_t time;
    std::size_t size_bytes() const noexcept override { return sizeof(*this); }
};

struct FrameData final : GSROData {
    std::vector<IntegralPayload> samples;
    std::size_t size_bytes() const noexcept override {
        return sizeof(*this) + samples.capacity() * sizeof(IntegralPayload);
    }
};

// Encode the preserved 52-byte header and slot directory as explicitly little-endian 32-bit words.
// The three legacy 64-bit fields retain their high-word-first ordering (the old llswap behavior).
std::vector<std::uint32_t> encode_frame(const GSROFrame& frame, daq::HeaderSettings settings = {});
GSROCrateResources create_crate(GSROCrateId crate, const std::string& filename,
                               daq::HeaderSettings settings = {});

} // namespace clas12::sro
