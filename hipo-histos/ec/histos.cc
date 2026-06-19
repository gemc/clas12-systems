#include "ec/histos.h"

#include "TCanvas.h"
#include "TDirectory.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TLatex.h"
#include "TLegend.h"
#include "TPad.h"

#include <algorithm>
#include <array>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>

namespace {

double max_bin_content_with_error(const TH1 *histo)
{
    if (histo == nullptr) {
        return 0.0;
    }

    double ymax = 0.0;
    for (int bin = 1; bin <= histo->GetNbinsX(); ++bin) {
        ymax = std::max(ymax, histo->GetBinContent(bin) + histo->GetBinError(bin));
    }
    return ymax;
}

void draw_pad_label(const std::string &label)
{
    TLatex latex;
    latex.SetNDC(true);
    latex.SetTextFont(43);
    latex.SetTextSize(16);
    latex.DrawLatex(0.14, 0.92, label.c_str());
}

void draw_comparison_pad(const std::vector<TH1 *> &histos, const std::vector<std::string> &labels,
                         const std::string &pad_label, bool draw_legend,
                         const bool *passed = nullptr)
{
    const std::array<int, 4> colors = {kBlack, kRed + 1, kBlue + 1, kGreen + 2};
    const std::array<int, 4> markers = {20, 24, 21, 25};
    double ymax = 0.0;
    for (auto *histo : histos) {
        ymax = std::max(ymax, max_bin_content_with_error(histo));
    }

    bool drew_one = false;
    for (std::size_t i = 0; i < histos.size(); ++i) {
        auto *histo = histos[i];
        if (histo == nullptr) {
            continue;
        }

        histo->SetLineColor(colors[i % colors.size()]);
        histo->SetMarkerColor(colors[i % colors.size()]);
        histo->SetMarkerStyle(markers[i % markers.size()]);
        histo->SetMarkerSize(0.5);
        histo->SetLineWidth(2);
        histo->SetMinimum(0.0);
        histo->SetMaximum(ymax > 0.0 ? ymax * 1.25 : 1.0);
        histo->DrawCopy(drew_one ? "E1 same" : "E1");
        drew_one = true;
    }

    draw_pad_label(pad_label);
    if (passed != nullptr) {
        draw_status_label(*passed);
    }
    if (draw_legend) {
        TLegend legend(0.52, 0.72, 0.92, 0.90);
        legend.SetBorderSize(0);
        legend.SetFillStyle(0);
        for (std::size_t i = 0; i < histos.size(); ++i) {
            if (histos[i] != nullptr) {
                legend.AddEntry(histos[i], labels[i].c_str(), "lep");
            }
        }
        legend.DrawClone();
    }
}

void draw_matrix(TCanvas *canvas, const std::vector<TH1 *> &histos,
                 const std::vector<std::string> &labels, int matrix)
{
    canvas->Divide(matrix, matrix, 0.001, 0.001);
    for (int component = 0; component < matrix * matrix; ++component) {
        canvas->cd(component + 1);
        gPad->SetGrid();
        gPad->SetTopMargin(0.12);
        draw_comparison_pad({histos[component]}, labels,
                            "C" + std::to_string(component + 1), component == 0);
    }
}

} // namespace

ECHistos::ECHistos(const std::string &label) :
    label_(label),
    safe_label_(sanitize_root_name(label))
{
    book();
}

void ECHistos::book()
{
    const auto layer_tag = "_l" + std::to_string(kFirstLayer);
    for (int component = 0; component < kComponents; ++component) {
        const auto c = std::to_string(component + 1);
        adc_[component] = std::make_unique<TH1D>(
            (safe_label_ + "_ec" + layer_tag + "_c" + c + "_adc").c_str(),
            ("EC layer " + std::to_string(kFirstLayer) + " component " + c + " ADC;ADC;hits").c_str(),
            kAdcBins,
            0.0,
            kAdcMax);
        adc_[component]->Sumw2();

        tdc_[component] = std::make_unique<TH1D>(
            (safe_label_ + "_ec" + layer_tag + "_c" + c + "_tdc").c_str(),
            ("EC layer " + std::to_string(kFirstLayer) + " component " + c + " TDC;TDC;hits").c_str(),
            kTdcBins,
            0.0,
            kTdcMax);
        tdc_[component]->Sumw2();
    }

    for (int sector = 0; sector < kSectors; ++sector) {
        const int s = sector + 1;
        occupancy_[sector] = std::make_unique<TH2D>(
            (safe_label_ + "_ec_s" + std::to_string(s) + "_occupancy").c_str(),
            ("EC sector " + std::to_string(s) + " occupancy;component;layer;occupancy [%]").c_str(),
            kComponents,
            0.5,
            kComponents + 0.5,
            kLayers,
            kLayerMin - 0.5,
            kLayerMax + 0.5);
        occupancy_[sector]->Sumw2();
    }
}

void ECHistos::fill(const hipo::bank &ecal_adc, const hipo::bank &ecal_tdc)
{
    ++events_;

    for (int row = 0; row < ecal_adc.getRows(); ++row) {
        const int sector = ecal_adc.getInt("sector", row);
        const int layer = ecal_adc.getInt("layer", row);
        const int component = ecal_adc.getInt("component", row);
        if (sector < 1 || sector > kSectors || layer < kLayerMin || layer > kLayerMax ||
            component < 1 || component > kComponents) {
            continue;
        }

        occupancy_[sector - 1]->Fill(component, layer);
        if (layer == kFirstLayer) {
            adc_[component - 1]->Fill(ecal_adc.getInt("ADC", row));
        }
    }

    for (int row = 0; row < ecal_tdc.getRows(); ++row) {
        const int layer = ecal_tdc.getInt("layer", row);
        const int component = ecal_tdc.getInt("component", row);
        if (layer != kFirstLayer || component < 1 || component > kComponents) {
            continue;
        }
        tdc_[component - 1]->Fill(ecal_tdc.getInt("TDC", row));
    }
}

void ECHistos::finalize()
{
    if (normalized_) {
        return;
    }
    normalized_ = true;

    if (events_ <= 0) {
        return;
    }

    // Each occupancy bin is a single channel (one component in one layer of one sector), so the per-channel
    // occupancy in percent is simply 100 * hits / events.
    const double occupancy_norm = 100.0 / static_cast<double>(events_);
    for (int sector = 0; sector < kSectors; ++sector) {
        occupancy_[sector]->Scale(occupancy_norm);
    }
}

void ECHistos::write(TDirectory *directory) const
{
    TDirectory *saved_dir = gDirectory;
    directory->cd();

    auto *subdir = directory->mkdir(safe_label_.c_str());
    subdir->cd();
    for (int component = 0; component < kComponents; ++component) {
        adc_[component]->Write();
        tdc_[component]->Write();
    }
    for (int sector = 0; sector < kSectors; ++sector) {
        occupancy_[sector]->Write();
    }
    saved_dir->cd();
}

void ECHistos::save_plots(const std::string &plot_dir) const
{
    const auto layer_label = "EC layer " + std::to_string(kFirstLayer);

    std::vector<TH1 *> adc_histos;
    std::vector<TH1 *> tdc_histos;
    for (int component = 0; component < kComponents; ++component) {
        adc_histos.push_back(adc_[component].get());
        tdc_histos.push_back(tdc_[component].get());
    }

    auto *adc_canvas = make_canvas("c_" + safe_label_ + "_ec_adc", label_ + " " + layer_label + " ADC",
                                   2000, 2000);
    draw_matrix(adc_canvas, adc_histos, {label_}, kMatrix);
    adc_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_ec_l" + std::to_string(kFirstLayer) + "_adc")
                           .c_str());
    show_canvas(adc_canvas);

    auto *tdc_canvas = make_canvas("c_" + safe_label_ + "_ec_tdc", label_ + " " + layer_label + " TDC",
                                   2000, 2000);
    draw_matrix(tdc_canvas, tdc_histos, {label_}, kMatrix);
    tdc_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_ec_l" + std::to_string(kFirstLayer) + "_tdc")
                           .c_str());
    show_canvas(tdc_canvas);

    auto *occupancy_canvas = make_canvas("c_" + safe_label_ + "_ec_occupancy",
                                         label_ + " EC occupancy", 2100, 1300);
    occupancy_canvas->Divide(3, 2, 0.001, 0.001);
    for (int sector = 0; sector < kSectors; ++sector) {
        occupancy_canvas->cd(sector + 1);
        gPad->SetGrid();
        gPad->SetRightMargin(0.15);
        gPad->SetTopMargin(0.10);
        occupancy_[sector]->DrawCopy("colz");
        draw_pad_label("S" + std::to_string(sector + 1) + " occupancy");
    }
    occupancy_canvas->SaveAs(plot_file(plot_dir, safe_label_ + "_ec_occupancy").c_str());
    show_canvas(occupancy_canvas);
}

std::vector<TH1 *> ECHistos::comparison_histos() const
{
    // The EC per-component ADC and TDC distributions are detail histograms compared through the custom
    // 6x6 grids in save_comparison_plots, so the generic 1D comparison list is intentionally empty.
    return {};
}

std::vector<std::string> ECHistos::comparison_names() const
{
    return {};
}

std::vector<TH2 *> ECHistos::comparison_2d_histos() const
{
    std::vector<TH2 *> histos;
    for (int sector = 0; sector < kSectors; ++sector) {
        histos.push_back(occupancy_[sector].get());
    }
    return histos;
}

std::vector<std::string> ECHistos::comparison_2d_names() const
{
    std::vector<std::string> names;
    for (int sector = 0; sector < kSectors; ++sector) {
        names.push_back("ec_s" + std::to_string(sector + 1) + "_occupancy");
    }
    return names;
}

std::vector<TH1 *> ECHistos::diagnostic_histos() const
{
    std::vector<TH1 *> histos;
    for (int component = 0; component < kComponents; ++component) {
        histos.push_back(adc_[component].get());
    }
    for (int component = 0; component < kComponents; ++component) {
        histos.push_back(tdc_[component].get());
    }
    return histos;
}

std::vector<std::string> ECHistos::diagnostic_names() const
{
    std::vector<std::string> names;
    const auto layer = std::to_string(kFirstLayer);
    for (int component = 0; component < kComponents; ++component) {
        names.push_back("ec_l" + layer + "_c" + std::to_string(component + 1) + "_adc");
    }
    for (int component = 0; component < kComponents; ++component) {
        names.push_back("ec_l" + layer + "_c" + std::to_string(component + 1) + "_tdc");
    }
    return names;
}

double ECHistos::diagnostic_scale(const std::string &name, bool normalize) const
{
    const bool normalizable = name.find("_adc") != std::string::npos ||
                              name.find("_tdc") != std::string::npos;
    if (!normalize || events_ <= 0 || !normalizable) {
        return 1.0;
    }
    return 1.0 / static_cast<double>(events_);
}

TH1D *ECHistos::adc_histo(int component) const
{
    if (component < 0 || component >= kComponents) {
        return nullptr;
    }
    return adc_[component].get();
}

TH1D *ECHistos::tdc_histo(int component) const
{
    if (component < 0 || component >= kComponents) {
        return nullptr;
    }
    return tdc_[component].get();
}

std::unique_ptr<SubsystemHistos> ECSubsystem::create_histos(const InputSpec &input,
                                                            const RunOptions &) const
{
    return std::make_unique<ECHistos>(input.label);
}

void ECSubsystem::process_file(const RunOptions &options, const InputSpec &input,
                               SubsystemHistos &histos) const
{
    auto *ec_histos = dynamic_cast<ECHistos *>(&histos);
    if (ec_histos == nullptr) {
        throw std::runtime_error("Internal error: EC subsystem received non-EC histogram storage.");
    }

    hipo::reader reader;
    reader.open(input.path.c_str());

    hipo::dictionary factory;
    reader.readDictionary(factory);

    for (const char *bank_name : {"ECAL::adc", "ECAL::tdc"}) {
        if (!factory.hasSchema(bank_name)) {
            throw std::runtime_error("Input file '" + input.path + "' does not contain bank " + bank_name);
        }
    }

    hipo::bank ecal_adc(factory.getSchema("ECAL::adc"));
    hipo::bank ecal_tdc(factory.getSchema("ECAL::tdc"));
    hipo::event event;

    long event_counter = 0;
    while (reader.next() && (options.max_events < 0 || event_counter < options.max_events)) {
        reader.read(event);
        event.getStructure(ecal_adc);
        event.getStructure(ecal_tdc);
        ec_histos->fill(ecal_adc, ecal_tdc);
        ++event_counter;

        if (options.print_interval > 0 && event_counter % options.print_interval == 0) {
            std::cout << "  " << input.label << ": processed " << event_counter << " events\n";
        }
    }

    std::cout << "  " << input.label << ": processed " << event_counter << " events\n";
}

void ECSubsystem::save_comparison_plots(const std::vector<SubsystemHistos *> &histos,
                                        const std::string &plot_dir, const std::string &header,
                                        bool normalize, const DiagnosticSummary &diagnostics) const
{
    static constexpr int matrix = 6;
    static constexpr int components = matrix * matrix;

    if (histos.size() != 2) {
        return;
    }

    std::vector<const ECHistos *> ec_histos;
    std::vector<std::string> labels;
    for (const auto *histo_set : histos) {
        const auto *ec_histo = dynamic_cast<const ECHistos *>(histo_set);
        if (ec_histo == nullptr) {
            return;
        }
        ec_histos.push_back(ec_histo);
        labels.push_back(ec_histo->label());
    }

    const auto layer = std::to_string(ECHistos::first_layer());

    struct MatrixSpec {
        std::string suffix;
        std::string title;
        TH1D *(ECHistos::*accessor)(int) const;
    };
    const std::array<MatrixSpec, 2> matrices = {
        MatrixSpec{"adc", "EC layer " + layer + " ADC comparison", &ECHistos::adc_histo},
        MatrixSpec{"tdc", "EC layer " + layer + " TDC comparison", &ECHistos::tdc_histo},
    };

    for (const auto &spec : matrices) {
        auto *canvas = make_canvas("c_ec_l" + layer + "_" + spec.suffix + "_compare", spec.title,
                                   2000, 2000);
        canvas->Divide(matrix, matrix, 0.001, 0.001);
        for (int component = 0; component < components; ++component) {
            canvas->cd(component + 1);
            gPad->SetGrid();
            gPad->SetTopMargin(0.12);

            std::vector<TH1 *> comparison;
            std::vector<std::unique_ptr<TH1>> scaled;
            for (const auto *ec_histo : ec_histos) {
                auto *histo = (ec_histo->*spec.accessor)(component);
                if (normalize && histo != nullptr && ec_histo->events() > 0) {
                    auto clone = std::unique_ptr<TH1>(static_cast<TH1 *>(histo->Clone()));
                    clone->SetDirectory(nullptr);
                    clone->Scale(1.0 / static_cast<double>(ec_histo->events()));
                    comparison.push_back(clone.get());
                    scaled.push_back(std::move(clone));
                } else {
                    comparison.push_back(histo);
                }
            }

            const auto name =
                "ec_l" + layer + "_c" + std::to_string(component + 1) + "_" + spec.suffix;
            const auto status = diagnostics.statuses.find(name);
            const bool has_status = status != diagnostics.statuses.end();
            const bool passed = has_status && status->second;
            draw_comparison_pad(comparison, labels, "C" + std::to_string(component + 1),
                                component == 0, has_status ? &passed : nullptr);
        }
        draw_canvas_header(canvas, header);
        canvas->SaveAs(plot_file(plot_dir, "compare_ec_l" + layer + "_" + spec.suffix).c_str());
        show_canvas(canvas);
    }
}
