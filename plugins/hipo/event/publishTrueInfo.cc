// hipo plugin
#include "gstreamerHIPOFactory.h"

bool GStreamerHIPOFactory::publishEventTrueInfoDataImpl(
    const std::string&                       detectorName,
    const std::vector<const GTrueInfoData*>& trueInfoData) {

    if (trueInfoData.empty()) return true;

    int8_t detID = getDetectorID(detectorName);

    for (const auto* hit : trueInfoData) {
        TrueInfoRow row;
        row.detectorID = detID;
        row.doubles    = hit->getDoubleVariablesMap();
        trueInfoBuffer.push_back(std::move(row));
    }

    log->info(2, FUNCTION_NAME,
              detectorName, ": buffered ", trueInfoData.size(), " MC::True rows");
    return true;
}
