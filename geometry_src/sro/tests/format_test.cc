#include "jlab_sro.h"
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>

using namespace clas12::sro;

void require(bool value) { if (!value) { throw std::runtime_error("JLAB SRO format check failed"); } }

template<class F> void rejects(F action) {
    bool rejected = false;
    try { action(); } catch (const std::exception&) { rejected = true; }
    require(rejected);
}

int main() {
    // Check named host-order setup and serialization independently of frame construction.
    constexpr std::uint64_t counter = (std::uint64_t{1} << 32) + 7;
    constexpr std::uint64_t seconds = (std::uint64_t{1} << 32) + 3;
    const auto header = daq::setup_frame_header(76, counter, seconds * 1000000000 + 123456789,
                                               {42, 0xC0DA2019, 258, 8});
    require(header.source_id == 42 && header.total_length == 124 && header.payload_length == 76);
    require(header.compressed_length == 76 && header.record_counter == counter);
    require(header.ts_sec == seconds && header.ts_nsec == 123456789);
    const auto packed = daq::encode_header(header);
    require(packed == std::array<std::uint32_t, 13>{42, 124, 76, 76, 0xC0DA2019, 258, 8,
                                                 1, 7, 1, 3, 0, 123456789});
    rejects([] { daq::setup_frame_header(std::numeric_limits<std::uint32_t>::max(), 1, 0); });

    auto data = std::make_unique<FrameData>();
    data->samples.emplace_back(11, 3, 4, 0x123, 20);
    GSROFrame frame{11, 0, GSROTime{0}, frame_duration, std::move(data)};
    const auto words = encode_frame(frame);
    // Golden legacy layout: 13 header words, 17 directory words, one marker and one integral.
    require(words.size() == 32 && words[0] == 0 && words[1] == 124 && words[2] == 76 && words[3] == 76);
    require(words[4] == 0xC0DA2019 && words[5] == 257 && words[6] == 0);
    require(words[7] == 0 && words[8] == 1 && words[9] == 0 && words[10] == 0);
    require(words[11] == 0 && words[12] == 65536 && words[13] == 0x80000000);
    for (unsigned slot = 0; slot < 16; ++slot) {
        require(words[14 + slot] == (slot < 3 ? 17u : slot == 3 ? 0x00020011u : 19u));
    }
    require(words[30] == 0x80008b03 && words[31] == 0x000a8123);
    const auto configured = encode_frame(frame, {42, 0xC0DA2019, 258, 8});
    require(configured[0] == 42 && configured[5] == 258 && configured[6] == 8);
    require(std::equal(words.begin() + 7, words.end(), configured.begin() + 7));
    for (unsigned bad = 0; bad < 5; ++bad) {
        auto invalid = std::make_unique<FrameData>();
        invalid->samples.emplace_back(bad == 0 ? 12 : 11, bad == 1 ? 16 : 3, bad == 2 ? 16 : 4,
                                      bad == 3 ? 8192 : 1, bad == 4 ? 65536 : 0);
        rejects([&] { encode_frame({11, 0, GSROTime{0}, frame_duration, std::move(invalid)}); });
    }
    auto largest = std::make_unique<FrameData>();
    largest->samples.emplace_back(11, 15, 15, 8191, 65535);
    const auto maximum = encode_frame({11, 0, GSROTime{0}, frame_duration, std::move(largest)});
    require(maximum.back() == 0x7fffffff); // 16383 four-ns ticks, 4 channel bits, 13 charge bits.
    auto overflow = std::make_unique<FrameData>();
    for (unsigned i = 0; i < 65535; ++i) { overflow->samples.emplace_back(11, 3, 0, 1, 0); }
    rejects([&] { encode_frame({11, 0, GSROTime{0}, frame_duration, std::move(overflow)}); });
    const auto stamp = std::chrono::steady_clock::now().time_since_epoch().count();
    const auto path = std::filesystem::temp_directory_path() / ("ftcal-sro-" + std::to_string(stamp) + ".ev");
    auto resources = create_crate(11, path.string());
    resources.plugin->consume_payload({11, 0, 0, GSROTime{20},
                                      std::make_unique<IntegralPayload>(11, 3, 4, 0x123, 20)});
    resources.plugin->consume_payload({11, 1, 0, frame_duration,
                                      std::make_unique<IntegralPayload>(11, 3, 4, 1, 0)});
    resources.plugin->advance_time(frame_duration);
    resources.plugin->finish_run({GSROEndReason::interrupted, frame_duration});
    resources.sink->finish_output();
    std::ifstream file(path, std::ios::binary);
    std::vector<unsigned char> bytes((std::istreambuf_iterator<char>(file)), {});
    file.close();
    std::filesystem::remove(path);
    require(bytes.size() == 136); // Only frame 0; frame 1 starts at the exact safe boundary and is discarded.
    require(bytes[0] == 0x19 && bytes[1] == 0x20 && bytes[2] == 0xda && bytes[3] == 0xc0);
    require(bytes[4] == 1 && bytes[5] == 0 && bytes[6] == 0xda && bytes[7] == 0xc0);
    for (std::size_t i = 0; i < words.size(); ++i) {
        for (unsigned b = 0; b < 4; ++b) { require(bytes[8 + 4 * i + b] == ((words[i] >> (8 * b)) & 255)); }
    }
    rejects([&] { create_crate(11, (path / "missing" / "output.ev").string()); });
    std::cout << "JLAB format, address ranges, byte order, exact boundary and interrupted-tail checks passed\n";
}
