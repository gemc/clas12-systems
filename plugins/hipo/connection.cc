// hipo plugin
#include "gstreamerHIPOFactory.h"
#include "gemc/gstreamer/gstreamerConventions.h"

bool GStreamerHIPOFactory::startRunImpl(const std::shared_ptr<GRunDataCollection>& run_data) {
    runNumber = run_data->getHeader()->getRunID();
    log->info(1, FUNCTION_NAME, "run number: ", runNumber);
    return true;
}

bool GStreamerHIPOFactory::openConnection() {
    schemas  = std::make_unique<HipoSchemas>();
    outEvent = std::make_unique<hipo::event>(1024 * 1024 * 2);

    // All schemas must be registered with the writer before the file is opened
    // because HIPO writes the schema dictionary into the file header.
    for (auto& [name, schema] : schemas->schemasToLoad) {
        hipoWriter.getDictionary().addSchema(schema);
    }

    hipoWriter.open(filename().c_str());
    log->info(1, FUNCTION_NAME, "opened HIPO file: ", filename());
    return true;
}

bool GStreamerHIPOFactory::closeConnectionImpl() {
    hipoWriter.close();
    log->info(1, FUNCTION_NAME, "closed HIPO file: ", filename());
    return true;
}
