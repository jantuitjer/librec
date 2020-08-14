package net.librec.conf;

import org.apache.commons.cli.MissingArgumentException;
import org.apache.commons.io.comparator.NameFileComparator;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.HashMap;

public class HybridConfiguration extends Configuration{
    private ArrayList<Configuration> configs;
    private HashMap<String, String> properties;
    private ArrayList<String> mandatoryProperties;

    public HybridConfiguration(String _pathToHybridConf) throws FileNotFoundException, MissingArgumentException {
        initDefaults();
        ConfigurationParser.parseHybridConfiguration(_pathToHybridConf, this);
        validateProperties();
        initConfigurations();
    }

    private void initConfigurations() throws FileNotFoundException {
        final String configPath = properties.get("data.hybrid.configs.path");
        ArrayList<File> configFiles = new ArrayList<>();
        File folder = new File(configPath);
        File[] listOfFiles = folder.listFiles();
        assert listOfFiles != null;
        for (File file : listOfFiles) {
            if (file.isFile()) {
                configFiles.add(file);
            }
        }
        //needed to achieve the desired order of configurations
        //in windows and linux systems, which produce different orders by default
        configFiles.sort(new NameFileComparator());
        for(File confFile : configFiles) {
            Configuration conf = new Configuration();
            ConfigurationParser.parse(confFile, conf);
            configs.add(conf);
        }
        System.exit(9);
    }

    private void validateProperties() throws MissingArgumentException {
        for(String key : mandatoryProperties){
            if (!properties.containsKey(key)){
                throw new MissingArgumentException("HybridConfiguration files must contain the key: " + key);
            }
        }
    }

    private void initDefaults() {
        configs = new ArrayList<>();
        properties = new HashMap<>();
        mandatoryProperties = new ArrayList<>();
        mandatoryProperties.add("rec.hybrid.class");
        mandatoryProperties.add("data.hybrid.configs.path");
        mandatoryProperties.add("data.model.sync");
    }

    public HashMap<String, String> getProperties(){
        return properties;
    }

    public void setConfigs(ArrayList<Configuration> _confs){
        this.configs = _confs;
    }
    public ArrayList<Configuration> getConfigs(){
        return configs;
    }

    public String get(String s) {
        return properties.get(s);
    }
}
