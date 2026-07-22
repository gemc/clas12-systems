#include "ltcc/histos.h"

#include "TCanvas.h"
#include "TDirectory.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TLatex.h"
#include "TPad.h"

#include <iostream>
#include <stdexcept>
#include <string>

namespace {

void draw_pad_label(const std::string &label)
{
    TLatex latex;
    latex.SetNDC(true);
    latex.SetTextFont(43);
    latex.SetTextSize(16);
    latex.DrawLatex(0.14, 0.92, label.c_str());
}

void draw_spectra(TCanvas *canvas, const std::vector<TH1D *> &histos,
                  const std::vector<std::string> &labels)
{
    canvas->Divide(2, 2, 0.001, 0.001);
    for (std::size_t index = 0; index < histos.size(); ++index) {
        canvas->cd(static_cast<int>(index + 1));
        gPad->SetGrid();
        gPad->SetTopMargin(0.12);
        histos[index]->SetLineColor(kBlue + 1);
        histos[index]->SetLineWidth(2);
        histos[index]->SetMinimum(0.0);
        histos[index]->DrawCopy("hist");
        draw_pad_label(labels[index]);
    }
}

} // namespace

LTCCHistos::LTCCHistos(const std::string &label) :
    label_(label),
    safe_label_(sanitize_root_name(label))
{
    book();
}

void LTCCHistos::book()
{
    for (int side = 0; side < kSides; ++side) {
        const auto name = side_name(side);
        adc_side_[side] = std::make_unique<TH1D>(
            (safe_label_ + "_ltcc_side" + name + "_adc").c_str(),
            ("Digitized ADC per PMT hit (LTCC::adc), half sector " + name +
             ", all sectors;ADC;hits").c_str(),
            kAdcBins,
            0.0,
            kAdcMax);
        adc_side_[side]->Sumw2();

        tdc_side_[side] = std::make_unique<TH1D>(
            (safe_label_ + "_ltcc_side" + name + "_tdc").c_str(),
            ("Digitized TDC per PMT hit (LTCC::tdc), half sector " + name +
             ", all sectors;TDC;hits").c_str(),
            kTdcBins,
            0.0,
            kTdcMax);
        tdc_side_[side]->Sumw2();
    }

    adc_all_ = std::make_unique<TH1D>(
        (safe_label_ + "_ltcc_all_adc").c_str(),
        "Digitized ADC per PMT hit (LTCC::adc), both half sectors and all sectors;ADC;hits",
        kAdcBins,
        0.0,
        kAdcMax);
    adc_all_->Sumw2();

    tdc_all_ = std::make_unique<TH1D>(
        (safe_label_ + "_ltcc_all_tdc").c_str(),
        "Digitized TDC per PMT hit (LTCC::tdc), both half sectors and all sectors;TDC;hits",
        kTdcBins,
        0.0,
        kTdcMax);
    tdc_all_->Sumw2();

    for (int sector = 0; sector < kSectors; ++sector) {
        const int s = sector + 1;
        occupancy_[sector] = std::make_unique<TH2D>(
            (safe_label_ + "_ltcc_s" + std::to_string(s) + "_occupancy").c_str(),
            ("Digitized-hit counts (LTCC::adc rows) per PMT segment and half sector (1, 2), sector " +
             std::to_string(s) + ";segment;half sector;counts")
                .c_str(),
            kSegments,
            0.5,
            kSegments + 0.5,
            kSides,
            0.5,
            kSides + 0.5);
        occupancy_[sector]->Sumw2();
    }

    xy_global_ = std::make_unique<TH2D>(
        (safe_label_ + "_ltcc_xy_global").c_str(),
        "True-hit y vs x in the lab frame (MC::True avgX/avgY, detector 16 = LTCC);x [mm];y [mm];entries",
        kXYBins,
        -kXYRange,
        kXYRange,
        kXYBins,
        -kXYRange,
        kXYRange);
    xy_global_->Sumw2();

    true_time_ = std::make_unique<TH1D>(
        (safe_label_ + "_ltcc_true_time").c_str(),
        "True hit time (MC::True avgT, detector 16 = LTCC): energy-weighted track time at the mirror, "
        "before digitization;time [ns];hits",
        kTrueTimeBins,
        0.0,
        kTrueTimeMax);
    true_time_->Sumw2();
}

void LTCCHistos::fill(const hipo::bank &ltcc_adc, const hipo::bank &ltcc_tdc, const hipo::bank &mc_true)
{
    ++events_;

    for (int row = 0; row < ltcc_adc.getRows(); ++row) {
        const int sector = ltcc_adc.getInt("sector", row);
        const int side = ltcc_adc.getInt("layer", row);
        const int segment = ltcc_adc.getInt("component", row);
        if (sector < 1 || sector > kSectors || side < 1 || side > kSides ||
            segment < 1 || segment > kSegments) {
            continue;
        }

        const int adc = ltcc_adc.getInt("ADC", row);
        adc_side_[side - 1]->Fill(adc);
        adc_all_->Fill(adc);
        occupancy_[sector - 1]->Fill(segment, side);
    }

    for (int row = 0; row < ltcc_tdc.getRows(); ++row) {
        const int sector = ltcc_tdc.getInt("sector", row);
        const int side = ltcc_tdc.getInt("layer", row);
        const int segment = ltcc_tdc.getInt("component", row);
        if (sector < 1 || sector > kSectors || side < 1 || side > kSides ||
            segment < 1 || segment > kSegments) {
            continue;
        }

        const int tdc = ltcc_tdc.getInt("TDC", row);
        tdc_side_[side - 1]->Fill(tdc);
        tdc_all_->Fill(tdc);
    }

    // Raw global hit position (y vs x) for LTCC true hits, unweighted, so the two-file comparison
    // runs on raw bin entries.
    for (int row = 0; row < mc_true.getRows(); ++row) {
        if (mc_true.getInt("detector", row) != kLtccDetectorId) {
            continue;
        }
        xy_global_->Fill(mc_true.getDouble("avgX", row), mc_true.getDouble("avgY", row));
        true_time_->Fill(mc_true.getDouble("avgT", row));
    }
}

void LTCCHistos::finalize()
{
    // The ADC/TDC spectra and 2D maps are kept as raw counts; per-event normalization is applied by
    // the comparison framework via the default scale when the two inputs have different event counts.
}

void LTCCHistos::write(TDirectory *directory) const
{
    TDirectory *saved_dir = gDirectory;
    directory->cd();

    auto *subdir = directory->mkdir(safe_label_.c_str());
    subdir->cd();
    for (int side = 0; side < kSides; ++side) {
        adc_side_[side]->Write();
        tdc_side_[side]->Write();
    }
    adc_all_->Write();
    tdc_all_->Write();
    for (int sector = 0; sector < kSectors; ++sector) {
        occupancy_[sector]->Write();
    }
    xy_global_->Write();
    true_time_->Write();
    saved_dir->cd();
}

void LTCCHistos::save_plots(const std::string &plot_dir) const
{
    std::vector<TH1D *> adc_histos;
    std::vector<TH1D *> tdc_histos;
    std::vector<std::string> spectra_labels;
    for (int side = 0; side < kSides; ++side) {
        adc_histos.push_back(adc_side_[side].get());
        tdc_histos.push_back(tdc_side_[side].get());
        spectra_labels.push_back("half sector " + side_name(side));
    }
    adc_histos.push_back(adc_all_.get());
    tdc_histos.push_back(tdc_all_.get());
    spectra_labels.emplace_back("all");

    auto *adc_canvas = make_canvas("c_" + safe_label_ + "_ltcc_adc", label_ + " LTCC ADC", 1800, 1200);
    draw_spectra(adc_canvas, adc_histos, spectra_labels);
    draw_canvas_description(adc_canvas, label_ + ": digitized ADC per PMT hit (LTCC::adc), by half sector");
    adc_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_ltcc_adc").c_str());
    show_canvas(adc_canvas);

    auto *tdc_canvas = make_canvas("c_" + safe_label_ + "_ltcc_tdc", label_ + " LTCC TDC", 1800, 1200);
    draw_spectra(tdc_canvas, tdc_histos, spectra_labels);
    draw_canvas_description(tdc_canvas, label_ + ": digitized TDC per PMT hit (LTCC::tdc), by half sector");
    tdc_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_ltcc_tdc").c_str());
    show_canvas(tdc_canvas);

    draw_overlay({true_time_.get()}, {label_}, "ltcc_true_time",
                 plot_file(plot_dir, safe_label_ + "_ltcc_true_time"));

    auto *occupancy_canvas = make_canvas("c_" + safe_label_ + "_ltcc_occupancy",
                                         label_ + " LTCC hit counts", 2100, 1300);
    occupancy_canvas->Divide(3, 2, 0.001, 0.001);
    for (int sector = 0; sector < kSectors; ++sector) {
        occupancy_canvas->cd(sector + 1);
        gPad->SetGrid();
        gPad->SetRightMargin(0.15);
        gPad->SetTopMargin(0.10);
        occupancy_[sector]->DrawCopy("colz");
        draw_pad_label("S" + std::to_string(sector + 1) + " counts");
    }
    draw_canvas_description(occupancy_canvas,
                            label_ + ": digitized-hit counts per segment and half sector (LTCC::adc), by sector");
    occupancy_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_ltcc_occupancy").c_str());
    show_canvas(occupancy_canvas);

    draw_2d(xy_global_.get(), label_ + " LTCC hit y vs x (global)",
            plot_file(plot_dir, safe_label_ + "_ltcc_xy_global"));
}

std::vector<TH1 *> LTCCHistos::comparison_histos() const
{
    std::vector<TH1 *> histos;
    for (int side = 0; side < kSides; ++side) {
        histos.push_back(adc_side_[side].get());
    }
    histos.push_back(adc_all_.get());
    for (int side = 0; side < kSides; ++side) {
        histos.push_back(tdc_side_[side].get());
    }
    histos.push_back(tdc_all_.get());
    histos.push_back(true_time_.get());
    return histos;
}

std::vector<std::string> LTCCHistos::comparison_names() const
{
    std::vector<std::string> names;
    for (int side = 0; side < kSides; ++side) {
        names.push_back("ltcc_side" + side_name(side) + "_adc");
    }
    names.emplace_back("ltcc_all_adc");
    for (int side = 0; side < kSides; ++side) {
        names.push_back("ltcc_side" + side_name(side) + "_tdc");
    }
    names.emplace_back("ltcc_all_tdc");
    names.emplace_back("ltcc_true_time");
    return names;
}

std::vector<TH2 *> LTCCHistos::comparison_2d_histos() const
{
    std::vector<TH2 *> histos;
    for (int sector = 0; sector < kSectors; ++sector) {
        histos.push_back(occupancy_[sector].get());
    }
    histos.push_back(xy_global_.get());
    return histos;
}

std::vector<std::string> LTCCHistos::comparison_2d_names() const
{
    std::vector<std::string> names;
    for (int sector = 0; sector < kSectors; ++sector) {
        names.push_back("ltcc_s" + std::to_string(sector + 1) + "_occupancy");
    }
    names.emplace_back("ltcc_xy_global");
    return names;
}

std::string LTCCHistos::side_name(int side_index)
{
    static const std::array<std::string, kSides> names = {"1", "2"};
    if (side_index < 0 || side_index >= kSides) {
        return "unknown";
    }
    return names[side_index];
}

std::unique_ptr<SubsystemHistos> LTCCSubsystem::create_histos(const InputSpec &input,
                                                              const RunOptions &) const
{
    return std::make_unique<LTCCHistos>(input.label);
}

void LTCCSubsystem::process_file(const RunOptions &options, const InputSpec &input,
                                 SubsystemHistos &histos) const
{
    auto *ltcc_histos = dynamic_cast<LTCCHistos *>(&histos);
    if (ltcc_histos == nullptr) {
        throw std::runtime_error("Internal error: LTCC subsystem received non-LTCC histogram storage.");
    }

    hipo::reader reader;
    reader.open(input.path.c_str());

    hipo::dictionary factory;
    reader.readDictionary(factory);

    for (const char *bank_name : {"LTCC::adc", "LTCC::tdc", "MC::True"}) {
        if (!factory.hasSchema(bank_name)) {
            throw std::runtime_error("Input file '" + input.path + "' does not contain bank " + bank_name);
        }
    }

    hipo::bank ltcc_adc(factory.getSchema("LTCC::adc"));
    hipo::bank ltcc_tdc(factory.getSchema("LTCC::tdc"));
    hipo::bank mc_true(factory.getSchema("MC::True"));
    hipo::event event;

    long event_counter = 0;
    while (reader.next() && (options.max_events < 0 || event_counter < options.max_events)) {
        reader.read(event);
        event.getStructure(ltcc_adc);
        event.getStructure(ltcc_tdc);
        event.getStructure(mc_true);
        ltcc_histos->fill(ltcc_adc, ltcc_tdc, mc_true);
        ++event_counter;

        if (options.print_interval > 0 && event_counter % options.print_interval == 0) {
            std::cout << "  " << input.label << ": processed " << event_counter << " events\n";
        }
    }

    std::cout << "  " << input.label << ": processed " << event_counter << " events\n";
}
