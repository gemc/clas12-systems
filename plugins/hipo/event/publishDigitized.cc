// hipo plugin
#include "gstreamerHIPOFactory.h"

// gemc
#include "gemc/ghit/ghit.h"   // getIdentityMap

// hipo
#include "hipo4/bank.h"

bool GStreamerHIPOFactory::publishEventDigitizedDataImpl(
    const std::string&                        detectorName,
    const std::vector<const GDigitizedData*>& digitizedData) {

    if (digitizedData.empty()) return true;

    const int nHits = static_cast<int>(digitizedData.size());

    // Determine which bank types are present by inspecting the first hit's variables.
    // Convention used by digitization plugins:
    //   "ADC_" prefix  →  ADC bank
    //   "TDC_" prefix  →  TDC bank
    //   "WF_"  prefix  →  WF bank
    const auto& firstIntVars = digitizedData[0]->getIntObservablesMap(0);
    const auto& firstDblVars = digitizedData[0]->getDblObservablesMap(0);

    bool hasADC = false;
    bool hasTDC = false;
    bool hasWF  = false;

    for (const auto& [name, _] : firstIntVars) {
        if (name.rfind("ADC_", 0) == 0) hasADC = true;
        if (name.rfind("TDC_", 0) == 0) hasTDC = true;
        if (name.rfind("WF_",  0) == 0) hasWF  = true;
    }
    for (const auto& [name, _] : firstDblVars) {
        if (name.rfind("ADC_", 0) == 0) hasADC = true;
        if (name.rfind("TDC_", 0) == 0) hasTDC = true;
        if (name.rfind("WF_",  0) == 0) hasWF  = true;
    }

    hipo::schema adcSchema = schemas->getSchema(detectorName, 0);
    hipo::schema tdcSchema = schemas->getSchema(detectorName, 1);
    hipo::schema wfSchema  = schemas->getSchema(detectorName, 2);

    // Suppress bank if the schema is empty (detector has no ADC/TDC/WF).
    if (adcSchema.getEntryName(0) == "empty") hasADC = false;
    if (tdcSchema.getEntryName(0) == "empty") hasTDC = false;
    if (wfSchema.getEntryName(0)  == "empty") hasWF  = false;

    if (!hasADC && !hasTDC && !hasWF) return true;

    hipo::bank adcBank(adcSchema, nHits);
    hipo::bank tdcBank(tdcSchema, nHits);
    hipo::bank wfBank(wfSchema,   nHits);

    for (int nh = 0; nh < nHits; ++nh) {
        const auto* hit    = digitizedData[nh];
        auto identityMap   = getIdentityMap(hit->getIdentity());
        auto intVars       = hit->getIntObservablesMap(0);
        auto dblVars       = hit->getDblObservablesMap(0);

        // sector / layer / order are bytes; component is a short.
        // They come from the hit identity (set by the digitization plugin).
        auto putIdentity = [&](hipo::bank& bank) {
            for (const auto& [idName, idVal] : identityMap) {
                if (idName == "sector" || idName == "layer" || idName == "order") {
                    bank.putByte(idName.c_str(), nh, static_cast<int8_t>(idVal));
                }
                else if (idName == "component") {
                    bank.putShort(idName.c_str(), nh, static_cast<int16_t>(idVal));
                }
            }
        };

        auto fillBank = [&](hipo::bank& bank, const std::string& prefix) {
            putIdentity(bank);
            const std::size_t prefixLen = prefix.size();

            for (const auto& [name, val] : intVars) {
                if (name.rfind(prefix, 0) == 0) {
                    std::string col = name.substr(prefixLen);
                    bank.putInt(col.c_str(), nh, val);
                }
            }
            for (const auto& [name, val] : dblVars) {
                if (name.rfind(prefix, 0) == 0) {
                    std::string col = name.substr(prefixLen);
                    bank.putFloat(col.c_str(), nh, static_cast<float>(val));
                }
            }
        };

        if (hasADC) fillBank(adcBank, "ADC_");
        if (hasTDC) fillBank(tdcBank, "TDC_");
        if (hasWF)  fillBank(wfBank,  "WF_");
    }

    if (hasADC) outEvent->addStructure(adcBank);
    if (hasTDC) outEvent->addStructure(tdcBank);
    if (hasWF)  outEvent->addStructure(wfBank);

    log->info(2, FUNCTION_NAME,
              detectorName,
              ": ADC=", hasADC, " TDC=", hasTDC, " WF=", hasWF,
              " hits=", nHits);
    return true;
}
