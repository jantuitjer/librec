package net.librec.conf;

import net.librec.conf.Configuration;
import net.librec.conf.HybridConfiguration;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

/**
 * @author Jan Tuitjer
 */
public class ConfigurationParser {
    public static void parseHybridConfiguration(String path, HybridConfiguration hybridConf) throws FileNotFoundException {
        parseHybridConfiguration(new File(path), hybridConf);
    }

    public static void parseHybridConfiguration(File file, HybridConfiguration hybridConfiguration) throws FileNotFoundException {
        Scanner lineScanner = new Scanner(file);
        String[] arr;
        String line;
        while (lineScanner.hasNext()) {
            line = lineScanner.nextLine();
            if(line.equals("") || line.startsWith("#") || line.startsWith("//")){
                continue;
            }
            arr = line.split("=");
            hybridConfiguration.getProperties().put(arr[0], arr[1]);
        }
        lineScanner.close();
    }

    public static void parse(String path, Configuration conf) throws FileNotFoundException {
        parse(new File(path),conf);
    }

    public static void parse(File f, Configuration conf) throws FileNotFoundException {
        Scanner lineScanner = new Scanner(f);
        String[] arr;
        String line;
        while (lineScanner.hasNext()) {
            line = lineScanner.nextLine();
            if(line.equals("") || line.startsWith("#") || line.startsWith("//")){
                continue;
            }
            arr = line.split("=");
            conf.set(arr[0],arr[1]);
        }
        lineScanner.close();
    }
}
