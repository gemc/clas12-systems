#include "dc/histos.h"

#include "TDirectory.h"
#include "TH1D.h"
#include "TH2D.h"

#include <cmath>
#include <iostream>
#include <stdexcept>

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
            ("DC region " + std::to_string(r) + " z vertex;z [mm];rate [MHz]").c_str(),
            kBins / 2,
            z_min_[region],
            z_max_[region]);

        rz_vertex_[region] = std::make_unique<TH2D>(
            (prefix + "_rz_vertex").c_str(),
            ("DC region " + std::to_string(r) + " r vs z;z [mm];r [mm]").c_str(),
            kBins,
            z_min_[region],
            z_max_[region],
            kBins,
            r_min_[region],
            r_max_[region]);

        occupancy_summary_[region] = std::make_unique<TH1D>(
            (prefix + "_occupancy_summary").c_str(),
            ("DC region " + std::to_string(r) + " occupancy;sector;occupancy [%]").c_str(),
            kSectors,
            0.5,
            kSectors + 0.5);
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
}

void DCHistos::fill(const hipo::bank &mc_true, const hipo::bank &dc_tdc)
{
    ++events_;

    const int ntrue = mc_true.getRows();
    const int ntdc = dc_tdc.getRows();

    for (int row = 0; row < ntrue; ++row) {
        if (mc_true.getInt("detector", row) != kDetectorId) {
            continue;
        }

        const int hit_index = mc_true.getInt("hitn", row) - 1;
        if (hit_index < 0 || hit_index >= ntdc) {
            continue;
        }

        const int sector = dc_tdc.getInt("sector", hit_index);
        const int layer = dc_tdc.getInt("layer", hit_index);
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

        z_vertex_[region]->Fill(vz);
        rz_vertex_[region]->Fill(vz, radius);
        occupancy_summary_[region]->Fill(sector, occupancy_weight);
        layer_wire_->Fill(wire, layer, occupancy_weight);
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
    const double rate_norm = total_time_us > 0.0 ? 1.0 / total_time_us : 1.0;
    const double occupancy_norm = 100.0 / events_;
    const double region_channels = static_cast<double>(kWires * 12);

    for (int region = 0; region < kRegions; ++region) {
        z_vertex_[region]->Scale(rate_norm / kSectors);
        rz_vertex_[region]->Scale(rate_norm / kSectors);
        occupancy_summary_[region]->Scale(occupancy_norm / region_channels);
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
    }
    layer_wire_->Write();
    saved_dir->cd();
}

void DCHistos::save_plots(const std::string &plot_dir) const
{
    for (int region = 0; region < kRegions; ++region) {
        const int r = region + 1;
        const auto base = plot_dir + "/" + safe_label_ + "_dc_r" + std::to_string(r);
        draw_overlay({z_vertex_[region].get()}, {label_}, "DC z vertex region " + std::to_string(r),
                     base + "_z_vertex.png", true);
        draw_overlay({occupancy_summary_[region].get()}, {label_}, "DC occupancy region " + std::to_string(r),
                     base + "_occupancy_summary.png", false);
        draw_2d(rz_vertex_[region].get(), "DC r vs z region " + std::to_string(r),
                base + "_rz_vertex.png");
    }
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
