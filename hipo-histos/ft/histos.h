#ifndef HIPO_HISTOS_FT_HISTOS_H
#define HIPO_HISTOS_FT_HISTOS_H

#include "common.h"
#include "subsystems.h"

#include "TH1D.h"
#include "hipo4/reader.h"

#include <array>
#include <memory>
#include <string>
#include <vector>

class TDirectory;

class FTHistos final : public SubsystemHistos {
  public:
    explicit FTHistos(const std::string &label);

    const std::string &label() const override { return label_; }
    long events() const override { return events_; }

    void fill(const hipo::bank &ftcal_adc, const hipo::bank &fthodo_adc,
              const hipo::bank &fttrk_adc);
    void finalize() override;
    void write(TDirectory *directory) const override;
    void save_plots(const std::string &plot_dir) const override;

    std::vector<TH1 *> comparison_histos() const override;
    std::vector<std::string> comparison_names() const override;

  private:
    static constexpr int kDetectors = 3;
    static constexpr std::array<const char *, kDetectors> kDetectorNames = {
        "ftcal", "fthodo", "fttrk"};
    static constexpr std::array<const char *, kDetectors> kBankNames = {
        "FTCAL::adc", "FTHODO::adc", "FTTRK::adc"};
    static constexpr std::array<int, kDetectors> kAdcBins = {150, 200, 100};
    static constexpr std::array<double, kDetectors> kAdcMax = {30000.0, 100000.0, 2000.0};

    std::string label_;
    std::string safe_label_;
    long events_ = 0;
    std::array<std::unique_ptr<TH1D>, kDetectors> adc_;

    void book();
};

class FTSubsystem final : public Subsystem {
  public:
    const std::string &name() const override { return name_; }
    std::unique_ptr<SubsystemHistos> create_histos(const InputSpec &input,
                                                   const RunOptions &options) const override;
    void process_file(const RunOptions &options, const InputSpec &input,
                      SubsystemHistos &histos) const override;

  private:
    std::string name_ = "ft";
};

#endif
