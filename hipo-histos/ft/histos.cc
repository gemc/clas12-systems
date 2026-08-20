#include "ft/histos.h"

#include "TDirectory.h"

#include <iostream>
#include <stdexcept>

FTHistos::FTHistos(const std::string &label) :
    label_(label),
    safe_label_(sanitize_root_name(label))
{
    book();
}

void FTHistos::book()
{
    for (int detector = 0; detector < kDetectors; ++detector) {
        adc_[detector] = std::make_unique<TH1D>(
            (safe_label_ + "_ft_" + kDetectorNames[detector] + "_adc").c_str(),
            (std::string("Digitized ADC per hit (") + kBankNames[detector] + ");ADC;hits").c_str(),
            kAdcBins[detector], 0.0, kAdcMax[detector]);
        adc_[detector]->Sumw2();
    }
}

void FTHistos::fill(const hipo::bank &ftcal_adc, const hipo::bank &fthodo_adc,
                    const hipo::bank &fttrk_adc)
{
    ++events_;
    const std::array<const hipo::bank *, kDetectors> banks = {&ftcal_adc, &fthodo_adc, &fttrk_adc};
    for (int detector = 0; detector < kDetectors; ++detector) {
        for (int row = 0; row < banks[detector]->getRows(); ++row) {
            adc_[detector]->Fill(banks[detector]->getInt("ADC", row));
        }
    }
}

void FTHistos::finalize()
{
    // Spectra remain raw counts. The comparison framework normalizes them when event counts differ.
}

void FTHistos::write(TDirectory *directory) const
{
    TDirectory *saved_dir = gDirectory;
    directory->cd();
    auto *subdir = directory->mkdir(safe_label_.c_str());
    subdir->cd();
    for (const auto &histo : adc_) {
        histo->Write();
    }
    saved_dir->cd();
}

void FTHistos::save_plots(const std::string &plot_dir) const
{
    for (int detector = 0; detector < kDetectors; ++detector) {
        draw_overlay({adc_[detector].get()}, {label_},
                     std::string("ft_") + kDetectorNames[detector] + "_adc",
                     plot_file(plot_dir, safe_label_ + "_ft_" + kDetectorNames[detector] + "_adc"));
    }
}

std::vector<TH1 *> FTHistos::comparison_histos() const
{
    std::vector<TH1 *> histos;
    for (const auto &histo : adc_) {
        histos.push_back(histo.get());
    }
    return histos;
}

std::vector<std::string> FTHistos::comparison_names() const
{
    std::vector<std::string> names;
    for (const auto *detector : kDetectorNames) {
        names.emplace_back(std::string("ft_") + detector + "_adc");
    }
    return names;
}

std::unique_ptr<SubsystemHistos> FTSubsystem::create_histos(const InputSpec &input,
                                                            const RunOptions &) const
{
    return std::make_unique<FTHistos>(input.label);
}

void FTSubsystem::process_file(const RunOptions &options, const InputSpec &input,
                               SubsystemHistos &histos) const
{
    auto *ft_histos = dynamic_cast<FTHistos *>(&histos);
    if (ft_histos == nullptr) {
        throw std::runtime_error("Internal error: FT subsystem received non-FT histogram storage.");
    }

    hipo::reader reader;
    reader.open(input.path.c_str());

    hipo::dictionary factory;
    reader.readDictionary(factory);
    for (const char *bank_name : {"FTCAL::adc", "FTHODO::adc", "FTTRK::adc"}) {
        if (!factory.hasSchema(bank_name)) {
            throw std::runtime_error("Input file '" + input.path + "' does not contain bank " + bank_name);
        }
    }

    hipo::bank ftcal_adc(factory.getSchema("FTCAL::adc"));
    hipo::bank fthodo_adc(factory.getSchema("FTHODO::adc"));
    hipo::bank fttrk_adc(factory.getSchema("FTTRK::adc"));
    hipo::event event;

    long event_counter = 0;
    while (reader.next() && (options.max_events < 0 || event_counter < options.max_events)) {
        reader.read(event);
        event.getStructure(ftcal_adc);
        event.getStructure(fthodo_adc);
        event.getStructure(fttrk_adc);
        ft_histos->fill(ftcal_adc, fthodo_adc, fttrk_adc);
        ++event_counter;

        if (options.print_interval > 0 && event_counter % options.print_interval == 0) {
            std::cout << "  " << input.label << ": processed " << event_counter << " events\n";
        }
    }

    std::cout << "  " << input.label << ": processed " << event_counter << " events\n";
}
