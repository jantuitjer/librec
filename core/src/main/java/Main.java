import net.librec.common.LibrecException;
import net.librec.conf.Configuration;
import net.librec.conf.HybridConfiguration;
import net.librec.job.HybridRecommenderJob;
import net.librec.job.RecommenderJob;
import org.apache.commons.cli.MissingArgumentException;

import java.io.IOException;

/**
 * @author Jan Tuitjer
 */
public class Main {
    static final String FILE_PATH_USER = "conf/hybridConfigs/1.userknn-test.properties";
    static final String FILE_PATH_ITEM = "conf/hybridConfigs/2.itemknn-test.properties";
    public static void main(String[] args) throws LibrecException, IOException, ClassNotFoundException, MissingArgumentException {
        if (args.length == 1) {
            run(args[0]);
        } else {
            System.out.println("Starting HybridRecommender:");
            hybridJobExecution("conf/hybridconfig.properties");
//        System.out.println("Starting single UserKNN:");
//        jobExecution(FILE_PATH_USER);
//        System.out.println("Starting solo ItemKNN:");
//        jobExecution(FILE_PATH_ITEM);
        }
    }

    private static void run(String configFile) throws MissingArgumentException, ClassNotFoundException, LibrecException, IOException {
        if (configFile.contains("hybrid")) {
            hybridJobExecution(configFile);
        } else {
            jobExecution(configFile);
        }
    }

    private static void jobExecution(String _path) throws LibrecException, IOException, ClassNotFoundException {
        Configuration conf = new Configuration();
        config.ConfigurationParser.parse(_path, conf);
        RecommenderJob job = new RecommenderJob(conf);
        job.runJob();

    }

    private static void hybridJobExecution(String _pathToHybridConfiguration) throws IOException, MissingArgumentException, LibrecException, ClassNotFoundException {
        net.librec.conf.HybridConfiguration hybridConf = new HybridConfiguration(_pathToHybridConfiguration);
        System.err.println("ranking: "+hybridConf.get("rec.recommender.isranking"));
        System.err.println("weights = " + hybridConf.get("rec.hybrid.weights"));
        HybridRecommenderJob hrj = new HybridRecommenderJob(hybridConf);
        hrj.runJob();
    }
}
