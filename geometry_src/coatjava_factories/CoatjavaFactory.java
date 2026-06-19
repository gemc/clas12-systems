import java.io.FileWriter;
import java.io.IOException;
import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.util.Map;

public final class CoatjavaFactory {
    private CoatjavaFactory() {}

    public static void main(String[] args) throws Exception {
        Options options = Options.parse(args);
        Object factory = createFactory(options);

        try (FileWriter writer = new FileWriter(options.outputFile())) {
            writer.write(factory.toString());
        }

        if (options.system.equals("bst")) {
            writeBstParameters(factory, options.variation);
        }
    }

    private static Object createFactory(Options options) throws Exception {
        return switch (options.system) {
            case "dc" -> createDcFactory(options);
            case "ec" -> createTableProviderFactory(
                "org.jlab.detector.geant4.v2.ECGeant4Factory",
                options,
                "/geometry/ec/ec",
                "/geometry/ec/uview",
                "/geometry/ec/vview",
                "/geometry/ec/wview",
                "/geometry/ec/alignment"
            );
            case "pcal" -> createTableProviderFactory(
                "org.jlab.detector.geant4.v2.PCALGeant4Factory",
                options,
                "/geometry/pcal/pcal",
                "/geometry/pcal/Uview",
                "/geometry/pcal/Wview",
                "/geometry/pcal/alignment"
            );
            case "ftof" -> createConstantProviderFactory(
                "org.jlab.detector.geant4.v2.FTOFGeant4Factory",
                "FTOF",
                options
            );
            case "ctof" -> createConstantProviderFactory(
                "org.jlab.detector.geant4.v2.CTOFGeant4Factory",
                "CTOF",
                options
            );
            case "muvt" -> createRunVariationFactory(
                "org.jlab.detector.geant4.v2.MPGD.MUVT.MUVTGeant4Factory",
                options
            );
            case "urwt" -> createRunVariationFactory(
                "org.jlab.detector.geant4.v2.MPGD.URWT.URWTGeant4Factory",
                options
            );
            case "recoil" -> createRecoilFactory(options);
            case "bst" -> createBstFactory(options);
            default -> throw new IllegalArgumentException("Unsupported system: " + options.system);
        };
    }

    private static Object createDcFactory(Options options) throws Exception {
        Object cp = constants("DC", options.runNumber, options.variation);
        Class<?> factoryClass = Class.forName("org.jlab.detector.geant4.v2.DCGeant4Factory");
        Class<?> cpClass = Class.forName("org.jlab.geom.base.ConstantProvider");
        Class<?> ministaggerClass = Class.forName(
            "org.jlab.detector.geant4.v2.DCGeant4Factory$MinistaggerStatus"
        );
        Class<?> feedthroughsClass = Class.forName(
            "org.jlab.detector.geant4.v2.DCGeant4Factory$FeedthroughsStatus"
        );
        Object ministagger = enumValue(ministaggerClass, "NOTONREFWIRE");
        Object feedthroughs = enumValue(feedthroughsClass, "OFF");
        Constructor<?> constructor = factoryClass.getConstructor(
            cpClass,
            ministaggerClass,
            feedthroughsClass,
            boolean.class,
            double[][].class
        );
        return constructor.newInstance(cp, ministagger, feedthroughs, false, null);
    }

    private static Object createConstantProviderFactory(
        String className,
        String detectorType,
        Options options
    ) throws Exception {
        Object cp = constants(detectorType, options.runNumber, options.variation);
        Class<?> cpClass = Class.forName("org.jlab.geom.base.ConstantProvider");
        return Class.forName(className).getConstructor(cpClass).newInstance(cp);
    }

    private static Object createTableProviderFactory(
        String className,
        Options options,
        String... tables
    ) throws Exception {
        Object cp = constants(options.runNumber, options.variation, tables);
        Class<?> cpClass = Class.forName("org.jlab.geom.base.ConstantProvider");
        return Class.forName(className).getConstructor(cpClass).newInstance(cp);
    }

    private static Object createRunVariationFactory(String className, Options options) throws Exception {
        return Class.forName(className)
            .getConstructor(int.class, String.class)
            .newInstance(options.runNumber, options.variation);
    }

    private static Object createRecoilFactory(Options options) throws Exception {
        Object cp = constants("DC", options.runNumber, "default");
        Class<?> cpClass = Class.forName("org.jlab.geom.base.ConstantProvider");
        return Class.forName("org.jlab.detector.geant4.v2.recoil.RecoilGeant4Factory")
            .getConstructor(cpClass, int.class)
            .newInstance(cp, options.numberOfRegion);
    }

    private static Object createBstFactory(Options options) throws Exception {
        Object cp = Class.forName("org.jlab.detector.calib.utils.DatabaseConstantProvider")
            .getConstructor(int.class, String.class)
            .newInstance(options.runNumber, options.variation);
        Class<?> constantsClass = Class.forName("org.jlab.detector.geant4.v2.SVT.SVTConstants");
        Class<?> cpClass = Class.forName("org.jlab.geom.base.ConstantProvider");
        constantsClass.getField("VERBOSE").setBoolean(null, true);
        constantsClass.getMethod("connect", cpClass).invoke(null, cp);

        Object factory = Class.forName("org.jlab.detector.geant4.v2.SVT.SVTVolumeFactory")
            .getConstructor(cpClass, boolean.class)
            .newInstance(cp, false);
        factory.getClass().getField("BUILDSENSORS").setBoolean(factory, true);
        factory.getClass().getField("HALFBOXES").setBoolean(factory, true);
        factory.getClass().getMethod("makeVolumes").invoke(factory);
        return factory;
    }

    private static Object constants(String detectorType, int runNumber, String variation) throws Exception {
        Class<?> detectorTypeClass = Class.forName("org.jlab.detector.base.DetectorType");
        Object detector = enumValue(detectorTypeClass, detectorType);
        return Class.forName("org.jlab.detector.base.GeometryFactory")
            .getMethod("getConstants", detectorTypeClass, int.class, String.class)
            .invoke(null, detector, runNumber, variation);
    }

    private static Object constants(int runNumber, String variation, String... tables) throws Exception {
        Object provider = Class.forName("org.jlab.detector.calib.utils.DatabaseConstantProvider")
            .getConstructor(int.class, String.class)
            .newInstance(runNumber, variation);
        Method loadTable = provider.getClass().getMethod("loadTable", String.class);
        for (String table : tables) {
            loadTable.invoke(provider, table);
        }
        provider.getClass().getMethod("disconnect").invoke(provider);
        return provider;
    }

    @SuppressWarnings({ "unchecked", "rawtypes" })
    private static Object enumValue(Class<?> enumClass, String value) {
        return Enum.valueOf((Class<Enum>) enumClass, value);
    }

    private static void writeBstParameters(Object factory, String variation) throws Exception {
        Method putParameters = factory.getClass().getMethod("putParameters");
        Method getParameters = factory.getClass().getMethod("getParameters");
        Method getProperty = factory.getClass().getMethod("getProperty", String.class);
        putParameters.invoke(factory);

        @SuppressWarnings("unchecked")
        Map<String, String> parameters = (Map<String, String>) getParameters.invoke(factory);

        try (FileWriter writer = new FileWriter("bst__parameters_" + variation + ".txt")) {
            for (Map.Entry<String, String> entry : parameters.entrySet()) {
                String unit = "na";
                if (!entry.getKey().startsWith("n") && !entry.getKey().startsWith("b")) {
                    unit = (String) getProperty.invoke(factory, "unit_length");
                }
                writer.write(String.format(
                    "%s | %s | %s | %s | %s | %s%n",
                    entry.getKey(),
                    entry.getValue(),
                    unit,
                    getProperty.invoke(factory, "author"),
                    getProperty.invoke(factory, "email"),
                    getProperty.invoke(factory, "date")
                ));
            }
        }
    }

    private static final class Options {
        private String system = "dc";
        private String variation = "default";
        private int runNumber = 11;
        private int numberOfRegion = 3;
        private String output;

        private static Options parse(String[] args) {
            Options options = new Options();
            for (int i = 0; i < args.length; i++) {
                switch (args[i]) {
                    case "--system" -> options.system = args[++i];
                    case "--variation" -> options.variation = args[++i];
                    case "--runnumber" -> options.runNumber = Integer.parseInt(args[++i]);
                    case "--number-of-region", "--number_of_Region" -> {
                        options.numberOfRegion = Integer.parseInt(args[++i]);
                    }
                    case "--output" -> options.output = args[++i];
                    default -> throw new IllegalArgumentException("Unknown argument: " + args[i]);
                }
            }
            options.system = options.system.toLowerCase();
            return options;
        }

        private String outputFile() {
            if (output != null) {
                return output;
            }
            return system + "__volumes_" + variation + ".txt";
        }
    }
}
