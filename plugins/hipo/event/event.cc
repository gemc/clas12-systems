// hipo plugin
#include "gstreamerHIPOFactory.h"
#include "gemc/gstreamer/gstreamerConventions.h"

// hipo
#include "hipo4/bank.h"

bool GStreamerHIPOFactory::startEventImpl(
    [[maybe_unused]] const std::shared_ptr<GEventDataCollection>& event_data) {

    outEvent->reset();
    trueInfoBuffer.clear();

    log->info(2, FUNCTION_NAME, "event ", event_data->getHeader()->getG4LocalEvn());
    return true;
}

bool GStreamerHIPOFactory::endEventImpl(
    [[maybe_unused]] const std::shared_ptr<GEventDataCollection>& event_data) {

    // Assemble the MC::True bank now that all detectors have contributed rows.
    hipo::bank trueInfoBank(schemas->trueInfoSchema,
                            static_cast<int>(trueInfoBuffer.size()));

    for (int row = 0; row < static_cast<int>(trueInfoBuffer.size()); ++row) {
        const auto& r = trueInfoBuffer[row];
        trueInfoBank.putByte("detector", row, r.detectorID);

        for (const auto& [gemcName, value] : r.doubles) {
            std::string hipoName = getHipoName(gemcName);
            if (hipoName.empty()) continue;

            if (isTrueInfoIntVar(hipoName)) {
                trueInfoBank.putInt(hipoName.c_str(), row, static_cast<int>(value));
            }
            else {
                trueInfoBank.putFloat(hipoName.c_str(), row, static_cast<float>(value));
            }
        }
    }

    outEvent->addStructure(trueInfoBank);
    hipoWriter.addEvent(*outEvent);

    log->info(2, FUNCTION_NAME,
              "wrote event ", event_data->getHeader()->getG4LocalEvn(),
              " with ", trueInfoBuffer.size(), " MC::True rows");
    return true;
}
