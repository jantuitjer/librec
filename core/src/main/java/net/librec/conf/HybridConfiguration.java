package net.librec.conf;

import org.apache.commons.cli.MissingArgumentException;
import sun.nio.ch.ThreadPool;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.concurrent.ForkJoinPool;

public class HybridConfiguration extends Configuration{
    private ArrayList<Configuration> configs;
    private HashMap<String, String> properties;
    private ArrayList<String> mandatoryProperties;

    public HybridConfiguration(String _pathToHybridConf) throws FileNotFoundException, MissingArgumentException {
        initDefaults();
        config.ConfigurationParser.parseHybridConfiguration(_pathToHybridConf, this);
        validateProperties();
        initConfigurations();
    }

    private void initConfigurations() throws FileNotFoundException {
        final String configPath = properties.get("data.hybrid.configs.path");
        File folder = new File(configPath);
        File[] listOfFiles = folder.listFiles();
        assert listOfFiles != null;
        for (File file : listOfFiles) {
            if (file.isFile()) {
                Configuration conf = new Configuration();
                config.ConfigurationParser.parse(file, conf);
                configs.add(conf);
            }
        }
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
