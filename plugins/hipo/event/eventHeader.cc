// hipo plugin
#include "gstreamerHIPOFactory.h"

// hipo
#include "hipo4/bank.h"

// c++
#include <ctime>

bool GStreamerHIPOFactory::publishEventHeaderImpl(
    const std::unique_ptr<GEventHeader>& gevent_header) {

    hipo::bank runConfigBank(schemas->runConfigSchema, 1);

    runConfigBank.putInt("run",      0, runNumber);
    runConfigBank.putInt("event",    0, gevent_header->getG4LocalEvn());
    runConfigBank.putInt("unixtime", 0, static_cast<int>(std::time(nullptr)));
    runConfigBank.putLong("trigger",   0, 0L);
    runConfigBank.putLong("timestamp", 0, 0L);
    runConfigBank.putByte("type",    0, 0);
    runConfigBank.putByte("mode",    0, 0);
    runConfigBank.putFloat("torus",    0, 0.0f);   // placeholder — add hipo_torus option later
    runConfigBank.putFloat("solenoid", 0, 0.0f);   // placeholder — add hipo_solenoid option later

    outEvent->addStructure(runConfigBank);

    log->info(2, FUNCTION_NAME,
              "RUN::config: run=", runNumber,
              " event=", gevent_header->getG4LocalEvn());
    return true;
}
