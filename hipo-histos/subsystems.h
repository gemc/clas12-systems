#ifndef HIPO_HISTOS_SUBSYSTEMS_H
#define HIPO_HISTOS_SUBSYSTEMS_H

#include "common.h"

#include <memory>
#include <string>
#include <vector>

class Subsystem {
  public:
    virtual ~Subsystem() = default;

    virtual const std::string &name() const = 0;
    virtual std::unique_ptr<SubsystemHistos> create_histos(const InputSpec &input,
                                                           const RunOptions &options) const = 0;
    virtual void process_file(const RunOptions &options, const InputSpec &input,
                              SubsystemHistos &histos) const = 0;
    virtual void save_comparison_plots(const std::vector<SubsystemHistos *> &histos,
                                       const std::string &plot_dir, const std::string &header,
                                       bool normalize, const DiagnosticSummary &diagnostics) const {}
};

std::unique_ptr<Subsystem> make_subsystem(const std::string &name);
std::vector<std::string> supported_subsystems();

#endif
