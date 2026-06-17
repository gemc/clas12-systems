// hipo plugin
#include "gstreamerHIPOFactory.h"

// hipo
#include "hipo4/bank.h"

// c++
#include <cmath>

bool GStreamerHIPOFactory::publishEventGeneratedParticlesImpl(
    const std::string&            bankName,
    const GGeneratedParticleBank& particles) {

    // MC::Event and MC::Particle are written once per event from "generated".
    // That bank contains runtime-generated particles plus source-only records not propagated in Geant4.
    if (bankName != "generated") return true;
    if (particles.empty()) return true;

    const int nParticles = static_cast<int>(particles.size());

    // --- MC::Particle ---
    // Units: momentum in GeV (GEMC internal = MeV → divide by 1000),
    //        vertex in cm  (GEMC internal = mm  → divide by 10).
    hipo::bank mcParticleBank(schemas->geantParticle, nParticles);

    for (int i = 0; i < nParticles; ++i) {
        const auto& p = particles[i];

        const float px = static_cast<float>(p.p * std::sin(p.theta) * std::cos(p.phi) / 1000.0);
        const float py = static_cast<float>(p.p * std::sin(p.theta) * std::sin(p.phi) / 1000.0);
        const float pz = static_cast<float>(p.p * std::cos(p.theta)                   / 1000.0);

        mcParticleBank.putInt("pid", i, p.pid);
        mcParticleBank.putFloat("px", i, px);
        mcParticleBank.putFloat("py", i, py);
        mcParticleBank.putFloat("pz", i, pz);
        mcParticleBank.putFloat("vx", i, static_cast<float>(p.vx / 10.0));
        mcParticleBank.putFloat("vy", i, static_cast<float>(p.vy / 10.0));
        mcParticleBank.putFloat("vz", i, static_cast<float>(p.vz / 10.0));
        mcParticleBank.putFloat("vt", i, 0.0f);
    }

    outEvent->addStructure(mcParticleBank);

    // --- MC::Event (LUND-style event header) ---
    hipo::bank mcEventBank(schemas->mcEventHeader, 1);

    mcEventBank.putShort("npart",     0, static_cast<int16_t>(nParticles));
    mcEventBank.putShort("atarget",   0, 0);
    mcEventBank.putShort("ztarget",   0, 0);
    mcEventBank.putFloat("ptarget",   0, 0.0f);
    mcEventBank.putFloat("pbeam",     0, 0.0f);
    mcEventBank.putShort("btype",     0, 0);
    mcEventBank.putFloat("ebeam",     0, 0.0f);
    mcEventBank.putShort("targetid",  0, 0);
    mcEventBank.putShort("processid", 0, 0);
    mcEventBank.putFloat("weight",    0, 0.0f);

    outEvent->addStructure(mcEventBank);

    log->info(2, FUNCTION_NAME,
              "MC::Particle + MC::Event: ", nParticles, " particles");
    return true;
}
