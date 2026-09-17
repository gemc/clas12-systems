#include "jlab_sro.h"

#include <array>
#include <fstream>
#include <map>
#include <stdexcept>

namespace clas12::sro {

std::vector<std::uint32_t> encode_frame(const GSROFrame& frame, daq::HeaderSettings settings) {
    if (!frame.data || frame.crate_id > daq::max_crate || frame.begin < GSROTime{0} ||
        frame.end - frame.begin != frame_duration || frame.begin % frame_duration != GSROTime{0} ||
        frame.frame_id != static_cast<std::uint64_t>(frame.begin / frame_duration)) {
        throw std::invalid_argument("Invalid JLAB SRO frame boundary or crate");
    }
    const auto& data = dynamic_cast<const FrameData&>(*frame.data);
    std::array<std::vector<std::uint32_t>, daq::slot_count> slots;
    for (const auto& sample : data.samples) {
        if (sample.crate != frame.crate_id || sample.slot >= slots.size() ||
            sample.channel > daq::max_channel ||
            sample.charge > daq::max_charge || sample.time >= frame_duration.count()) {
            throw std::invalid_argument("JLAB SRO payload exceeds crate/slot/channel/charge/time range");
        }
        slots[sample.slot].push_back(sample.charge | (sample.channel << 13) |
                                     ((sample.time / daq::time_tick_ns) << 17));
    }
    std::vector<std::uint32_t> payload(1 + daq::slot_count, 0);
    payload[0] = 0x80000000;
    for (std::size_t slot = 0; slot < slots.size(); ++slot) {
        const auto offset = payload.size();
        const auto count = slots[slot].empty() ? 0 : slots[slot].size() + 1;
        if (offset > 65535 || count > 65535) {
            throw std::overflow_error("JLAB SRO slot directory exceeds 16-bit count/offset capacity");
        }
        payload[1 + slot] = static_cast<std::uint32_t>((count << 16) | offset);
        if (count) {
            payload.push_back(0x80008000 | (frame.crate_id << 8) | static_cast<std::uint32_t>(slot));
            payload.insert(payload.end(), slots[slot].begin(), slots[slot].end());
        }
    }
    const auto bytes = static_cast<std::uint32_t>(payload.size() * 4);
    const auto counter = frame.frame_id + 1; // Legacy record numbering starts at one.
    const auto timestamp = static_cast<std::uint64_t>(frame.end.count()); // Legacy counter * 65536 ns.
    const auto header = daq::setup_frame_header(bytes, counter, timestamp, settings);
    const auto header_words = daq::encode_header(header);
    std::vector<std::uint32_t> words(header_words.begin(), header_words.end());
    words.insert(words.end(), payload.begin(), payload.end());
    return words;
}

namespace {

class BinarySink final : public GSROFrameSink {
public:
    BinarySink(const std::string& filename, daq::HeaderSettings values) : settings(values) {
        file.exceptions(std::ios::failbit | std::ios::badbit);
        file.open(filename, std::ios::binary | std::ios::trunc);
        write_words({magic, super_magic}); // Once per file, even when the first occupied frame is not frame 1.
    }
    void write_frame(GSROFrame frame) override { write_words(encode_frame(frame, settings)); }
    void finish_output() override { file.close(); }
private:
    void write_words(const std::vector<std::uint32_t>& words) {
        std::vector<unsigned char> bytes;
        bytes.reserve(words.size() * 4);
        for (auto word : words) {
            for (unsigned shift = 0; shift < 32; shift += 8) {
                bytes.push_back(static_cast<unsigned char>((word >> shift) & 0xff));
            }
        }
        file.write(reinterpret_cast<const char*>(bytes.data()), static_cast<std::streamsize>(bytes.size()));
    }
    daq::HeaderSettings settings;
    std::ofstream file;
};

class Crate final : public GSROCratePlugin {
public:
    Crate(GSROFrameSink& sink, GSROCrateId id) : GSROCratePlugin(sink), crate(id) {}
    void consume_payload(GSROPayload payload) override {
        const auto& sample = dynamic_cast<const IntegralPayload&>(*payload.data);
        if (payload.crate_id != crate || sample.crate != crate || payload.time < GSROTime{0} ||
            sample.time != (payload.time % frame_duration).count()) {
            throw std::invalid_argument("JLAB SRO payload address/time does not match its envelope");
        }
        const auto id = static_cast<std::uint64_t>(payload.time / frame_duration);
        auto& frame = frames[id];
        if (!frame) { frame = std::make_unique<FrameData>(); }
        // Fail before the per-frame slot directory can overflow; split-frame records are not defined here.
        if (frame->samples.size() >= 65500) { throw std::overflow_error("JLAB SRO frame is too large"); }
        frame->samples.push_back(sample);
    }
    void advance_time(GSROTime safe_time) override {
        while (!frames.empty()) {
            const auto id = frames.begin()->first;
            const auto begin = frame_duration * static_cast<std::int64_t>(id);
            const auto end = begin + frame_duration;
            if (end > safe_time) { break; }
            auto frame = frames.extract(frames.begin());
            output.write_frame({crate, id, begin, end, std::move(frame.mapped())});
        }
    }
    void finish_run(const GSROEndContext&) override { frames.clear(); } // Discard every unproven tail.
private:
    GSROCrateId crate;
    std::map<std::uint64_t, std::unique_ptr<FrameData>> frames;
};

} // namespace

GSROCrateResources create_crate(GSROCrateId crate, const std::string& filename,
                               daq::HeaderSettings settings) {
    if (crate > daq::max_crate) {
        throw std::invalid_argument("JLAB SRO crate exceeds its 8-bit marker field");
    }
    auto sink = std::make_unique<BinarySink>(filename, settings);
    auto plugin = std::make_unique<Crate>(*sink, crate);
    return {std::move(sink), std::move(plugin)};
}

} // namespace clas12::sro
