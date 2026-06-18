// dladdr (used to locate this plugin's own path) needs _GNU_SOURCE on glibc.
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

// plugin header
#include "gfield_clas12bin.h"

// gemc gfield framework
#include "gemc/gfields/gfieldConventions.h"

// CLHEP units
#include "CLHEP/Units/SystemOfUnits.h"

// c++
#include <cmath>
#include <cstdlib>
#include <dlfcn.h>
#include <fstream>

using namespace CLHEP;

// Tells the loader how to create a GField in this plugin .so/.dylib.
extern "C" GField* GFieldFactory(const std::shared_ptr<GOptions>& g) {
	return static_cast<GField*>(new GField_Clas12BinFactory(g));
}


GField_Clas12BinFactory::~GField_Clas12BinFactory() {
	// cMag maps and the scratch value are heap allocated; release them when the field goes away.
	if (combinedValuePtr != nullptr) { free(combinedValuePtr); }
	// Note: cMag does not expose a public map-destroy entry point matching initializeSolenoid/Torus,
	// so the map buffers are intentionally left for process teardown (mirrors clas12Tags behaviour).
}


std::string GField_Clas12BinFactory::param_string(const std::string& key, const std::string& dflt) const {
	auto it = gfield_definitions.field_parameters.find(key);
	return (it != gfield_definitions.field_parameters.end() && !it->second.empty()) ? it->second : dflt;
}

double GField_Clas12BinFactory::param_g4number(const std::string& key, const std::string& dflt) const {
	return gutilities::getG4Number(param_string(key, dflt));
}

std::string GField_Clas12BinFactory::field_maps_directory() const {
	// Locate this plugin's own shared object on disk and point at the sibling "fields" directory
	// (<plugin_dir>/../fields). This mirrors the `meson install` layout: plugins land in <prefix>/lib
	// and the downloaded maps in <prefix>/fields. No environment variable is consulted.
	Dl_info info;
	if (dladdr(reinterpret_cast<const void*>(&GFieldFactory), &info) != 0 && info.dli_fname != nullptr) {
		const std::string plugin_path = info.dli_fname;
		const auto        slash       = plugin_path.find_last_of('/');
		if (slash != std::string::npos) { return plugin_path.substr(0, slash) + "/../fields"; }
	}
	log->warning("GField_Clas12BinFactory: could not resolve plugin path; using ./fields for field maps.");
	return "fields";
}


void GField_Clas12BinFactory::load_field_definitions(GFieldDefinition gfd) {
	gfield_definitions = gfd;

	// Resolve the directory holding the .dat maps: explicit "dir" parameter, else the "fields"
	// directory installed next to this plugin.
	std::string field_dir = param_string("dir", "");
	if (field_dir.empty()) { field_dir = field_maps_directory(); }

	const std::string solenoid_name = param_string("solenoid", "");
	const std::string torus_name    = param_string("torus", "");

	if (solenoid_name.empty() && torus_name.empty()) {
		log->error(ERR_WRONG_FIELD_NOT_FOUND,
		           "GField_Clas12BinFactory: neither 'solenoid' nor 'torus' map specified for field <",
		           gfield_definitions.name, ">. Exiting.");
	}

	// Interpolation: linear (default) interpolates the grid; "none" uses nearest neighbour.
	const std::string interpolation = param_string("interpolation", "linear");
	setAlgorithm(interpolation == "none" ? NEAREST_NEIGHBOR : INTERPOLATION);

	// Scratch value reused at every GetFieldValue call.
	combinedValuePtr = static_cast<FieldValuePtr>(malloc(sizeof(FieldValue)));

	// Load the solenoid map (optional).
	if (!solenoid_name.empty()) {
		const std::string path = field_dir + "/" + solenoid_name + ".dat";
		if (!std::ifstream(path).good()) {
			log->error(ERR_WRONG_FIELD_NOT_FOUND, "GField_Clas12BinFactory: solenoid map not found: ", path);
		}
		log->info(1, "Loading CLAS12 solenoid map: ", path);
		solenoidPtr = initializeSolenoid(path.c_str());
		solenoidPtr->scale  = param_g4number("solenoid_scale", "1");
		solenoidPtr->shiftX = param_g4number("solenoid_vx", "0") / cm;
		solenoidPtr->shiftY = param_g4number("solenoid_vy", "0") / cm;
		solenoidPtr->shiftZ = param_g4number("solenoid_vz", "0") / cm;
	}

	// Load the torus map (optional).
	if (!torus_name.empty()) {
		const std::string path = field_dir + "/" + torus_name + ".dat";
		if (!std::ifstream(path).good()) {
			log->error(ERR_WRONG_FIELD_NOT_FOUND, "GField_Clas12BinFactory: torus map not found: ", path);
		}
		log->info(1, "Loading CLAS12 torus map: ", path);
		torusPtr = initializeTorus(path.c_str());
		torusPtr->scale  = param_g4number("torus_scale", "1");
		torusPtr->shiftX = param_g4number("torus_vx", "0") / cm;
		torusPtr->shiftY = param_g4number("torus_vy", "0") / cm;
		torusPtr->shiftZ = param_g4number("torus_vz", "0") / cm;
	}

	// Overall map placement (applied in GetFieldValue / RotateField).
	mapOrigin[0]   = param_g4number("vx", "0");
	mapOrigin[1]   = param_g4number("vy", "0");
	mapOrigin[2]   = param_g4number("vz", "0");
	mapRotation[0] = param_g4number("rx", "0*deg");
	mapRotation[1] = param_g4number("ry", "0*deg");
	mapRotation[2] = param_g4number("rz", "0*deg");

	// Cache rotation trigonometry so GetFieldValue stays cheap.
	sinAlpha = sin(mapRotation[0]); cosAlpha = cos(mapRotation[0]);
	sinBeta  = sin(mapRotation[1]); cosBeta  = cos(mapRotation[1]);
	sinGamma = sin(mapRotation[2]); cosGamma = cos(mapRotation[2]);

	log->info(1, "CLAS12 binary field <", gfield_definitions.name,
	          "> loaded. interpolation: ", interpolation,
	          ", solenoid: ", solenoid_name.empty() ? "(none)" : solenoid_name,
	          ", torus: ", torus_name.empty() ? "(none)" : torus_name);
}


void GField_Clas12BinFactory::GetFieldValue(const double x[3], G4double* bfield) const {
	bfield[0] = bfield[1] = bfield[2] = 0;

	if (std::isnan(x[0]) || std::isnan(x[1]) || std::isnan(x[2])) {
		log->warning("GField_Clas12BinFactory: field coordinates requested are nan.");
		return;
	}

	// cMag expects coordinates in cm, in the map frame (origin-subtracted).
	const double rpoint[3] = {
		(x[0] - mapOrigin[0]) / cm,
		(x[1] - mapOrigin[1]) / cm,
		(x[2] - mapOrigin[2]) / cm
	};

	// Composite field: torus first, solenoid second (matches clas12Tags ordering).
	getCompositeFieldValue(combinedValuePtr, rpoint[0], rpoint[1], rpoint[2], torusPtr, solenoidPtr);

	bfield[0] = combinedValuePtr->b1 * kilogauss;
	bfield[1] = combinedValuePtr->b2 * kilogauss;
	bfield[2] = combinedValuePtr->b3 * kilogauss;

	RotateField(bfield);

	log->info(2, "CLAS12 binary field at (",
	          x[0] / cm, ", ", x[1] / cm, ", ", x[2] / cm, ") cm = (",
	          bfield[0] / gauss, ", ", bfield[1] / gauss, ", ", bfield[2] / gauss, ") gauss");
}


void GField_Clas12BinFactory::RotateField(double* bfield) const {
	// Rotate the field axes, not the point: each rotation is the inverse of the point rotation.
	if (mapRotation[0] != 0) {
		const double yPrime =  bfield[1] * cosAlpha + bfield[2] * sinAlpha;
		const double zPrime = -bfield[1] * sinAlpha + bfield[2] * cosAlpha;
		bfield[1] = yPrime;
		bfield[2] = zPrime;
	}
	if (mapRotation[1] != 0) {
		const double xPrime = bfield[0] * cosBeta - bfield[2] * sinBeta;
		const double zPrime = bfield[0] * sinBeta + bfield[2] * cosBeta;
		bfield[0] = xPrime;
		bfield[2] = zPrime;
	}
	if (mapRotation[2] != 0) {
		const double xPrime =  bfield[0] * cosGamma + bfield[1] * sinGamma;
		const double yPrime = -bfield[0] * sinGamma + bfield[1] * cosGamma;
		bfield[0] = xPrime;
		bfield[1] = yPrime;
	}
}
