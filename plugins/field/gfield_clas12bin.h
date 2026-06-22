#pragma once

// gemc gfield framework
#include "gemc/gfields/gfield.h"

// David Heddle's cMag library (C). The headers are wrapped in extern "C" so the
// C++ plugin links the C symbols without name mangling.
extern "C" {
#include "magfield.h"
#include "magfieldio.h"
#include "magfieldutil.h"
}

#include <string>

/**
 * \brief CLAS12 binary mapped magnetic field plugin (solenoid + torus).
 *
 * This is the GEMC3 port of clas12Tags `gclas12BinaryMappedField`. It reads the CLAS12
 * solenoid and torus binary field maps through the cMag library and returns the composite
 * field value at a point. The field is exposed as the plugin `gfieldclas12-cmagFactory`, so
 * a field definition selects it with `type: clas12-cmag`.
 *
 * Parameters (all forwarded as scalar strings through the generic `gfields` option node):
 * - `solenoid`        : solenoid map base name (the `.dat` extension is added). Empty disables it.
 * - `torus`           : torus map base name (the `.dat` extension is added). Empty disables it.
 * - `dir`             : directory holding the `.dat` maps. Optional override; when empty the maps are
 *                       read from the `fields` directory installed next to this plugin (see
 *                       field_maps_directory()). No environment variable is consulted.
 * - `solenoid_scale`  : scale factor applied to the solenoid map (default 1).
 * - `torus_scale`     : scale factor applied to the torus map (default 1).
 * - `solenoid_vx/vy/vz` : solenoid map displacement (Geant4 length units, default 0).
 * - `torus_vx/vy/vz`    : torus map displacement (Geant4 length units, default 0).
 * - `vx/vy/vz`        : overall map origin subtracted before lookup (Geant4 length units, default 0).
 * - `rx/ry/rz`        : overall map rotation (Geant4 angle units, default 0).
 * - `interpolation`   : `linear` (interpolated) or `none` (nearest neighbour). Default `linear`.
 *
 * Units: cMag map coordinates are in cm and field values in kilogauss; both are converted to
 * Geant4 units here. Threading: GEMC3 builds the field registry per worker thread, so each thread
 * owns its own cMag map pointers (whose probe cells are mutated during evaluation) — this keeps
 * cMag thread-safe at the cost of loading the maps once per thread.
 */
class GField_Clas12BinFactory : public GField {

public:
	explicit GField_Clas12BinFactory(const std::shared_ptr<GOptions>& gopt) : GField(gopt) {}
	~GField_Clas12BinFactory() override;

	/// Compute the composite (solenoid + torus) field at the lab-frame point `pos`.
	void GetFieldValue(const double pos[3], G4double* bfield) const override;

	/// Parse parameters, load the solenoid/torus maps and cache rotation trigonometry.
	void load_field_definitions(GFieldDefinition gfd) override;

private:
	// Map pointers owned by this instance (per thread). nullptr when the map is not configured.
	MagneticFieldPtr solenoidPtr = nullptr;
	MagneticFieldPtr torusPtr    = nullptr;
	FieldValuePtr    combinedValuePtr = nullptr;

	// Overall map placement (lab frame). Origin in Geant4 length units, rotation in radians.
	G4double mapOrigin[3]   = {0.0, 0.0, 0.0};
	G4double mapRotation[3] = {0.0, 0.0, 0.0};

	// Cached rotation trigonometry (set from mapRotation in load_field_definitions).
	double sinAlpha = 0.0, cosAlpha = 1.0; // about X
	double sinBeta  = 0.0, cosBeta  = 1.0; // about Y
	double sinGamma = 0.0, cosGamma = 1.0; // about Z

	// Rotate the field vector (not the point): each rotation is the inverse of the point rotation.
	void RotateField(double* bfield) const;

	// Convenience parameter accessors with defaults (the generic node only guarantees name/type).
	std::string param_string(const std::string& key, const std::string& dflt) const;
	double      param_g4number(const std::string& key, const std::string& dflt) const;

	// Default field-map directory, derived from this plugin's own on-disk location:
	// <plugin_dir>/../fields (the layout produced by `meson install`). No env var is used.
	std::string field_maps_directory() const;
};
