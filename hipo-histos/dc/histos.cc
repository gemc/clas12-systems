#include "dc/histos.h"

#include "TCanvas.h"
#include "TDirectory.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TLatex.h"
#include "TLegend.h"
#include "TPad.h"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <stdexcept>

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

enum class LayerMode {
    Invalid,
    LayerGlobal,
    SlGlobal,
    SlAndLocalLayer,
};

struct LayerColumns {
    int layer = -1;
    int sl = -1;
    LayerMode mode = LayerMode::Invalid;
};

std::pair<int, int> column_range(const hipo::bank &bank, int column)
{
    int min_value = 1000000;
    int max_value = -1000000;
    for (int row = 0; row < bank.getRows(); ++row) {
        const int value = bank.getInt(column, row);
        min_value = std::min(min_value, value);
        max_value = std::max(max_value, value);
    }
    return {min_value, max_value};
}

bool has_global_layer_range(const std::pair<int, int> &range)
{
    return range.first >= 1 && range.second > 6 && range.second <= 36;
}

bool has_local_layer_range(const std::pair<int, int> &range)
{
    return range.first >= 1 && range.second >= 1 && range.second <= 6;
}

LayerColumns select_layer_columns(hipo::bank &dc_tdc)
{
    LayerColumns columns;
    auto &schema = dc_tdc.getSchema();

    if (schema.exists("layer")) {
        columns.layer = schema.getEntryOrder("layer");
    }
    if (schema.exists("sl")) {
        columns.sl = schema.getEntryOrder("sl");
    } else if (schema.exists("superlayer")) {
        columns.sl = schema.getEntryOrder("superlayer");
    }

    if (dc_tdc.getRows() <= 0) {
        columns.mode = LayerMode::LayerGlobal;
        return columns;
    }

    const auto layer_range = columns.layer >= 0 ? column_range(dc_tdc, columns.layer) :
                                                  std::pair<int, int>{0, 0};
    const auto sl_range = columns.sl >= 0 ? column_range(dc_tdc, columns.sl) :
                                            std::pair<int, int>{0, 0};

    if (has_global_layer_range(sl_range)) {
        columns.mode = LayerMode::SlGlobal;
    } else if (has_global_layer_range(layer_range)) {
        columns.mode = LayerMode::LayerGlobal;
    } else if (has_local_layer_range(sl_range) && has_local_layer_range(layer_range)) {
        columns.mode = LayerMode::SlAndLocalLayer;
    } else if (columns.layer >= 0) {
        columns.mode = LayerMode::LayerGlobal;
    }

    return columns;
}

int global_layer(const hipo::bank &dc_tdc, int row, const LayerColumns &columns)
{
    if (columns.mode == LayerMode::LayerGlobal && columns.layer >= 0) {
        return dc_tdc.getInt(columns.layer, row);
    }
    if (columns.mode == LayerMode::SlGlobal && columns.sl >= 0) {
        return dc_tdc.getInt(columns.sl, row);
    }
    if (columns.mode == LayerMode::SlAndLocalLayer && columns.sl >= 0 && columns.layer >= 0) {
        return (dc_tdc.getInt(columns.sl, row) - 1) * 6 + dc_tdc.getInt(columns.layer, row);
    }
    return -1;
}

void draw_pad_label(const std::string &label)
{
    TLatex latex;
    latex.SetNDC(true);
    latex.SetTextFont(43);
    latex.SetTextSize(20);
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
        histo->SetMarkerSize(0.55);
        histo->SetLineWidth(2);
        histo->SetMinimum(0.0);
        histo->SetMaximum(ymax > 0.0 ? ymax * 1.25 : 1.0);
        histo->Draw(drew_one ? "E1 same" : "E1");
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
        legend.Draw();
    }
}

} // namespace

DCHistos::DCHistos(const std::string &label, double time_window_ns) :
    label_(label),
    safe_label_(sanitize_root_name(label)),
    time_window_ns_(time_window_ns)
{
    book();
}

void DCHistos::book()
{
    for (int region = 0; region < kRegions; ++region) {
        const int r = region + 1;
        const auto prefix = safe_label_ + "_dc_r" + std::to_string(r);

        z_vertex_[region] = std::make_unique<TH1D>(
            (prefix + "_z_vertex").c_str(),
            ("DC region " + std::to_string(r) + " z vertex;z [mm];events").c_str(),
            kBins / 2,
            z_min_[region],
            z_max_[region]);
        z_vertex_[region]->Sumw2();

        rz_vertex_[region] = std::make_unique<TH2D>(
            (prefix + "_rz_vertex").c_str(),
            ("DC region " + std::to_string(r) + " r vs z;z [mm];r [mm]").c_str(),
            kBins,
            z_min_[region],
            z_max_[region],
            kBins,
            r_min_[region],
            r_max_[region]);
        rz_vertex_[region]->Sumw2();

        occupancy_summary_[region] = std::make_unique<TH1D>(
            (prefix + "_occupancy_summary").c_str(),
            ("DC region " + std::to_string(r) + " occupancy;sector;occupancy [%]").c_str(),
            kSectors,
            0.5,
            kSectors + 0.5);
        occupancy_summary_[region]->Sumw2();

        for (int sector = 0; sector < kSectors; ++sector) {
            const int s = sector + 1;
            const auto name = prefix + "_s" + std::to_string(s) + "_tdc";
            tdc_[region][sector] = std::make_unique<TH1D>(
                name.c_str(),
                ("DC region " + std::to_string(r) + " sector " + std::to_string(s) + " TDC;TDC [ns];hits")
                    .c_str(),
                200,
                0.0,
                1000.0);
            tdc_[region][sector]->Sumw2();
        }
    }

    layer_wire_ = std::make_unique<TH2D>(
        (safe_label_ + "_dc_layer_wire_occupancy").c_str(),
        "DC layer-wire occupancy;wire;layer;occupancy [%]",
        kWires,
        0.5,
        kWires + 0.5,
        kLayers,
        0.5,
        kLayers + 0.5);
    layer_wire_->Sumw2();
}

void DCHistos::fill(const hipo::bank &mc_true, hipo::bank &dc_tdc)
{
    ++events_;

    const int ntrue = mc_true.getRows();
    const int ntdc = dc_tdc.getRows();

    // Event-local totals are used only for error propagation. DC hit entries in the same generated event are
    // correlated, so z-vertex event counts and occupancy summaries need event-to-event fluctuations rather
    // than per-hit sqrt(N) errors.
    std::array<std::array<double, kZBins>, kRegions> event_z_vertex = {};
    std::array<std::array<double, kSectors>, kRegions> event_occupancy = {};
    const auto layer_columns = select_layer_columns(dc_tdc);
    if (!warned_local_layers_ && ntdc > 0 && layer_columns.mode == LayerMode::Invalid) {
        std::cerr << "warning: could not derive a DC global layer in 1..36 from DC::tdc; "
                  << "R2/R3 occupancy plots cannot be derived reliably.\n";
        warned_local_layers_ = true;
    }

    for (int row = 0; row < ntdc; ++row) {
        const int sector = dc_tdc.getInt("sector", row);
        const int layer = global_layer(dc_tdc, row, layer_columns);
        const int region = (layer - 1) / 12;
        if (sector < 1 || sector > kSectors || layer < 1 || layer > kLayers ||
            region < 0 || region >= kRegions) {
            continue;
        }
        tdc_[region][sector - 1]->Fill(dc_tdc.getInt("TDC", row));
    }

    for (int row = 0; row < ntrue; ++row) {
        if (mc_true.getInt("detector", row) != kDetectorId) {
            continue;
        }

        const int hit_index = mc_true.getInt("hitn", row) - 1;
        if (hit_index < 0 || hit_index >= ntdc) {
            continue;
        }

        const int sector = dc_tdc.getInt("sector", hit_index);
        const int layer = global_layer(dc_tdc, hit_index, layer_columns);
        const int wire = dc_tdc.getInt("component", hit_index);
        const int region = (layer - 1) / 12;
        if (sector < 1 || sector > kSectors || layer < 1 || layer > kLayers ||
            region < 0 || region >= kRegions) {
            continue;
        }

        const double total_edep = mc_true.getDouble("totEdep", row);
        if (total_edep <= thresholds_mev_[region]) {
            continue;
        }

        const double vx = mc_true.getDouble("vx", row);
        const double vy = mc_true.getDouble("vy", row);
        const double vz = mc_true.getDouble("vz", row);
        const double radius = std::sqrt(vx * vx + vy * vy);
        const double occupancy_weight =
            std::max(time_window_ns_, electronics_window_ns_[region]) / time_window_ns_;

        // The z-vertex histogram is an event-count histogram. One event may produce many correlated DC hits, so
        // set an event-local presence flag for the z bin instead of filling once per hit.
        const int zbin = z_vertex_[region]->FindFixBin(vz);
        if (zbin >= 1 && zbin <= z_vertex_[region]->GetNbinsX()) {
            event_z_vertex[region][zbin - 1] = 1.0;
        }
        rz_vertex_[region]->Fill(vz, radius);
        occupancy_summary_[region]->Fill(sector, occupancy_weight);
        // Occupancy is corrected for the larger electronics integration window in R2/R3. The same weighted
        // event contribution is accumulated here for event-level occupancy errors.
        event_occupancy[region][sector - 1] += occupancy_weight;
        layer_wire_->Fill(wire, layer, occupancy_weight);
    }

    // Store sum(x_i^2) for each bin, where x_i is this event's total bin contribution. Together with the
    // histogram's sum(x_i), this is enough to compute the unbiased event variance during finalize().
    for (int region = 0; region < kRegions; ++region) {
        for (int zbin = 0; zbin < kZBins; ++zbin) {
            const double event_weight = event_z_vertex[region][zbin];
            z_vertex_[region]->AddBinContent(zbin + 1, event_weight);
            z_vertex_event_sum_sq_[region][zbin] += event_weight * event_weight;
        }
        for (int sector = 0; sector < kSectors; ++sector) {
            const double event_weight = event_occupancy[region][sector];
            occupancy_event_sum_sq_[region][sector] += event_weight * event_weight;
        }
    }
}

void DCHistos::finalize()
{
    if (normalized_) {
        return;
    }
    normalized_ = true;

    if (events_ <= 0) {
        return;
    }

    const double total_time_us = events_ * time_window_ns_ / 1000.0;

    // r-z content is stored as MHz per sector:
    //   raw hits / (events * time_window_ns / 1000 us) / 6 sectors.
    // The 1D z-vertex content is intentionally not rate-normalized; it remains a raw event count.
    const double rate_norm = total_time_us > 0.0 ? 1.0 / total_time_us : 1.0;

    // Occupancy content is stored as percent:
    //   weighted hits * 100 / events / channels,
    // where each region has 12 layers * 112 wires per sector.
    const double occupancy_norm = 100.0 / events_;

    const double region_channels = static_cast<double>(kWires * 12);

    for (int region = 0; region < kRegions; ++region) {
        std::array<double, kZBins> z_vertex_errors = {};
        for (int zbin = 0; zbin < kZBins; ++zbin) {
            const int bin = zbin + 1;
            const double sum = z_vertex_[region]->GetBinContent(bin);
            const double sum_sq = z_vertex_event_sum_sq_[region][zbin];
            if (events_ > 1) {
                // Unbiased variance of per-event bin totals:
                //   var = (sum(x_i^2) - sum(x_i)^2 / N) / (N - 1).
                // The histogram content is a raw event total, so the error is the standard deviation of the
                // total: sqrt(N * var). Comparison normalization by 1/N later turns it into sqrt(var / N).
                const double variance =
                    std::max((sum_sq - sum * sum / static_cast<double>(events_)) /
                                 static_cast<double>(events_ - 1),
                             0.0);
                z_vertex_errors[zbin] = std::sqrt(variance * static_cast<double>(events_));
            }
        }
        const double occupancy_scale = occupancy_norm / region_channels;

        // Occupancy errors are also standard errors of the mean event contribution, then scaled to percent
        // per region channel. This is intentionally larger than per-hit sqrt(N) when events contain
        // correlated hits.
        const double occupancy_mean_scale = 100.0 / region_channels;
        for (int zbin = 0; zbin < kZBins; ++zbin) {
            z_vertex_[region]->SetBinError(zbin + 1, z_vertex_errors[zbin]);
        }
        rz_vertex_[region]->Scale(rate_norm / kSectors);
        std::array<double, kSectors> occupancy_errors = {};
        for (int sector = 0; sector < kSectors; ++sector) {
            const int bin = sector + 1;
            const double sum = occupancy_summary_[region]->GetBinContent(bin);
            const double sum_sq = occupancy_event_sum_sq_[region][sector];
            if (events_ > 1) {
                // Same event-level variance formula as z-vertex, using weighted occupancy event totals.
                const double variance =
                    std::max((sum_sq - sum * sum / static_cast<double>(events_)) /
                                 static_cast<double>(events_ - 1),
                             0.0);
                occupancy_errors[sector] =
                    std::sqrt(variance / static_cast<double>(events_)) * occupancy_mean_scale;
            }
        }
        occupancy_summary_[region]->Scale(occupancy_scale);
        for (int sector = 0; sector < kSectors; ++sector) {
            occupancy_summary_[region]->SetBinError(sector + 1, occupancy_errors[sector]);
        }
        occupancy_summary_[region]->SetMinimum(0.0);
    }
    layer_wire_->Scale(occupancy_norm / kSectors);
}

void DCHistos::write(TDirectory *directory) const
{
    TDirectory *saved_dir = gDirectory;
    directory->cd();

    auto *subdir = directory->mkdir(safe_label_.c_str());
    subdir->cd();
    for (int region = 0; region < kRegions; ++region) {
        z_vertex_[region]->Write();
        rz_vertex_[region]->Write();
        occupancy_summary_[region]->Write();
        for (int sector = 0; sector < kSectors; ++sector) {
            tdc_[region][sector]->Write();
        }
    }
    layer_wire_->Write();
    saved_dir->cd();
}

void DCHistos::save_plots(const std::string &plot_dir) const
{
    auto *canvas = make_canvas("c_" + safe_label_ + "_dc_summary", label_ + " DC summary", 1800, 1400);
    canvas->Divide(3, 3, 0.001, 0.001);

    for (int region = 0; region < kRegions; ++region) {
        const int r = region + 1;
        const auto region_label = "R" + std::to_string(r);

        canvas->cd(region + 1);
        gPad->SetGrid();
        gPad->SetTopMargin(0.10);
        occupancy_summary_[region]->SetMarkerStyle(20);
        occupancy_summary_[region]->SetMarkerSize(0.7);
        occupancy_summary_[region]->SetMaximum(
            std::max(max_bin_content_with_error(occupancy_summary_[region].get()) * 1.25, 1.0));
        occupancy_summary_[region]->Draw("E1");
        draw_pad_label(region_label + " occupancy");

        canvas->cd(kRegions + region + 1);
        gPad->SetGrid();
        gPad->SetTopMargin(0.10);
        gPad->SetRightMargin(0.15);
        rz_vertex_[region]->Draw("colz");
        draw_pad_label(region_label + " r vs z");

        canvas->cd(2 * kRegions + region + 1);
        gPad->SetGrid();
        gPad->SetLogy(z_vertex_[region]->GetMaximum() > 0.0);
        gPad->SetTopMargin(0.10);
        if (z_vertex_[region]->GetMaximum() > 0.0) {
            z_vertex_[region]->SetMinimum(0.1);
        }
        z_vertex_[region]->SetMarkerStyle(20);
        z_vertex_[region]->SetMarkerSize(0.6);
        z_vertex_[region]->SetMaximum(
            std::max(max_bin_content_with_error(z_vertex_[region].get()) * 5.0, 1.0));
        z_vertex_[region]->Draw("E1");
        draw_pad_label(region_label + " z vertex");
    }

    canvas->SaveAs((plot_dir + "/" + safe_label_ + "_dc_summary.png").c_str());
    show_canvas(canvas);

    auto *tdc_canvas = make_canvas("c_" + safe_label_ + "_dc_tdc", label_ + " DC TDC", 2200, 1200);
    tdc_canvas->Divide(6, 3, 0.001, 0.001);
    for (int region = 0; region < kRegions; ++region) {
        for (int sector = 0; sector < kSectors; ++sector) {
            tdc_canvas->cd(region * kSectors + sector + 1);
            gPad->SetGrid();
            gPad->SetTopMargin(0.12);
            draw_comparison_pad({tdc_[region][sector].get()}, {label_},
                                "R" + std::to_string(region + 1) + " S" + std::to_string(sector + 1),
                                region == 0 && sector == 0);
        }
    }
    tdc_canvas->SaveAs((plot_dir + "/" + safe_label_ + "_dc_tdc.png").c_str());
    show_canvas(tdc_canvas);

    draw_2d(layer_wire_.get(), "DC layer-wire occupancy",
            plot_dir + "/" + safe_label_ + "_dc_layer_wire_occupancy.png");
}

std::vector<TH1 *> DCHistos::comparison_histos() const
{
    return {
        z_vertex_[0].get(),
        z_vertex_[1].get(),
        z_vertex_[2].get(),
        occupancy_summary_[0].get(),
        occupancy_summary_[1].get(),
        occupancy_summary_[2].get(),
    };
}

TH1D *DCHistos::tdc_histo(int region, int sector) const
{
    if (region < 0 || region >= kRegions || sector < 0 || sector >= kSectors) {
        return nullptr;
    }
    return tdc_[region][sector].get();
}

std::vector<std::string> DCHistos::comparison_names() const
{
    return {
        "dc_r1_z_vertex",
        "dc_r2_z_vertex",
        "dc_r3_z_vertex",
        "dc_r1_occupancy_summary",
        "dc_r2_occupancy_summary",
        "dc_r3_occupancy_summary",
    };
}

double DCHistos::comparison_plot_scale(const std::string &name, bool normalize) const
{
    if (events_ <= 0) {
        return 1.0;
    }
    if (normalize && name.find("z_vertex") != std::string::npos) {
        return 1.0 / static_cast<double>(events_);
    }
    if (normalized_ || name.find("occupancy_summary") == std::string::npos) {
        return 1.0;
    }

    return 100.0 / static_cast<double>(events_) / static_cast<double>(kWires * 12);
}

std::vector<TH1 *> DCHistos::diagnostic_histos() const
{
    auto histos = comparison_histos();
    for (int region = 0; region < kRegions; ++region) {
        for (int sector = 0; sector < kSectors; ++sector) {
            histos.push_back(tdc_[region][sector].get());
        }
    }
    return histos;
}

std::vector<std::string> DCHistos::diagnostic_names() const
{
    auto names = comparison_names();
    for (int region = 0; region < kRegions; ++region) {
        for (int sector = 0; sector < kSectors; ++sector) {
            names.push_back("dc_r" + std::to_string(region + 1) + "_s" +
                            std::to_string(sector + 1) + "_tdc");
        }
    }
    return names;
}

double DCHistos::diagnostic_scale(const std::string &name, bool normalize) const
{
    const bool normalizable = name.find("z_vertex") != std::string::npos ||
                              name.find("_tdc") != std::string::npos;
    if (!normalize || events_ <= 0 || !normalizable) {
        return 1.0;
    }
    return 1.0 / static_cast<double>(events_);
}

std::vector<TH2 *> DCHistos::comparison_2d_histos() const
{
    return {
        rz_vertex_[0].get(),
        rz_vertex_[1].get(),
        rz_vertex_[2].get(),
        layer_wire_.get(),
    };
}

std::vector<std::string> DCHistos::comparison_2d_names() const
{
    return {
        "dc_r1_rz_vertex",
        "dc_r2_rz_vertex",
        "dc_r3_rz_vertex",
        "dc_layer_wire_occupancy",
    };
}

std::unique_ptr<SubsystemHistos> DCSubsystem::create_histos(const InputSpec &input,
                                                            const RunOptions &options) const
{
    return std::make_unique<DCHistos>(input.label, options.time_window_ns);
}

void DCSubsystem::process_file(const RunOptions &options, const InputSpec &input,
                               SubsystemHistos &histos) const
{
    auto *dc_histos = dynamic_cast<DCHistos *>(&histos);
    if (dc_histos == nullptr) {
        throw std::runtime_error("Internal error: DC subsystem received non-DC histogram storage.");
    }

    hipo::reader reader;
    reader.open(input.path.c_str());

    hipo::dictionary factory;
    reader.readDictionary(factory);

    for (const char *bank_name : {"MC::True", "DC::tdc"}) {
        if (!factory.hasSchema(bank_name)) {
            throw std::runtime_error("Input file '" + input.path + "' does not contain bank " + bank_name);
        }
    }

    hipo::bank mc_true(factory.getSchema("MC::True"));
    hipo::bank dc_tdc(factory.getSchema("DC::tdc"));
    hipo::event event;

    long event_counter = 0;
    while (reader.next() && (options.max_events < 0 || event_counter < options.max_events)) {
        reader.read(event);
        event.getStructure(mc_true);
        event.getStructure(dc_tdc);
        dc_histos->fill(mc_true, dc_tdc);
        ++event_counter;

        if (options.print_interval > 0 && event_counter % options.print_interval == 0) {
            std::cout << "  " << input.label << ": processed " << event_counter << " events\n";
        }
    }

    std::cout << "  " << input.label << ": processed " << event_counter << " events\n";
}

void DCSubsystem::save_comparison_plots(const std::vector<SubsystemHistos *> &histos,
                                        const std::string &plot_dir, const std::string &header,
                                        bool normalize, const DiagnosticSummary &diagnostics) const
{
    static constexpr int regions = 3;
    static constexpr int sectors = 6;

    if (histos.size() != 2) {
        return;
    }

    std::vector<const DCHistos *> dc_histos;
    std::vector<std::string> labels;
    for (const auto *histo_set : histos) {
        const auto *dc_histo = dynamic_cast<const DCHistos *>(histo_set);
        if (dc_histo == nullptr) {
            return;
        }
        dc_histos.push_back(dc_histo);
        labels.push_back(dc_histo->label());
    }

    auto *canvas = make_canvas("c_dc_tdc_compare", "DC TDC comparison", 2200, 1250);

    const double canvas_left = 0.02;
    const double canvas_right = 0.995;
    const double canvas_bottom = 0.04;
    const double canvas_top = 0.925;
    const double col_width = (canvas_right - canvas_left) / sectors;
    const double row_height = (canvas_top - canvas_bottom) / regions;

    for (int region = 0; region < regions; ++region) {
        for (int sector = 0; sector < sectors; ++sector) {
            canvas->cd();
            const double left = canvas_left + sector * col_width + 0.006;
            const double right = canvas_left + (sector + 1) * col_width - 0.006;
            const double top = canvas_top - region * row_height - 0.014;
            const double bottom = canvas_top - (region + 1) * row_height + 0.022;
            auto *pad = new TPad(
                ("p_dc_tdc_compare_r" + std::to_string(region + 1) + "_s" +
                 std::to_string(sector + 1))
                    .c_str(),
                "",
                left,
                bottom,
                right,
                top);
            pad->Draw();
            pad->cd();
            gPad->SetGrid();
            gPad->SetTopMargin(0.12);
            std::vector<TH1 *> comparison;
            std::vector<std::unique_ptr<TH1>> normalized;
            for (const auto *dc_histo : dc_histos) {
                auto *tdc = dc_histo->tdc_histo(region, sector);
                if (normalize && tdc != nullptr && dc_histo->events() > 0) {
                    auto clone = std::unique_ptr<TH1>(static_cast<TH1 *>(tdc->Clone()));
                    clone->SetDirectory(nullptr);
                    clone->Scale(1.0 / static_cast<double>(dc_histo->events()));
                    comparison.push_back(clone.get());
                    normalized.push_back(std::move(clone));
                } else {
                    comparison.push_back(tdc);
                }
            }
            const auto name = "dc_r" + std::to_string(region + 1) + "_s" +
                              std::to_string(sector + 1) + "_tdc";
            const auto status = diagnostics.statuses.find(name);
            const bool has_status = status != diagnostics.statuses.end();
            const bool passed = has_status && status->second;
            draw_comparison_pad(comparison, labels,
                                "R" + std::to_string(region + 1) + " S" + std::to_string(sector + 1),
                                region == 0 && sector == 0, has_status ? &passed : nullptr);
        }
    }

    draw_canvas_header(canvas, header);
    canvas->SaveAs((plot_dir + "/compare_dc_tdc.png").c_str());
    show_canvas(canvas);
}
