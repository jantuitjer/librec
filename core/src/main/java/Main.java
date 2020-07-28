import net.librec.common.LibrecException;
import net.librec.conf.Configuration;
import net.librec.conf.HybridConfiguration;
import net.librec.data.DataModel;
import net.librec.data.model.AbstractDataModel;
import net.librec.data.model.TextDataModel;
import net.librec.eval.RecommenderEvaluator;
import net.librec.eval.rating.MAEEvaluator;
import net.librec.job.HybridRecommenderJob;
import net.librec.job.RecommenderJob;
import net.librec.math.structure.SequentialAccessSparseMatrix;
import net.librec.recommender.AbstractRecommender;
import net.librec.recommender.HybridContext;
import net.librec.recommender.RecommenderContext;
import net.librec.recommender.cf.ItemKNNRecommender;
import net.librec.recommender.cf.UserKNNRecommender;
import net.librec.recommender.hybrid.WeightedHybridRecommender;
import net.librec.recommender.item.RecommendedItem;
import net.librec.recommender.item.RecommendedList;
import net.librec.similarity.CosineSimilarity;
import net.librec.similarity.PCCSimilarity;
import net.librec.similarity.RecommenderSimilarity;
import org.apache.commons.cli.MissingArgumentException;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;

/**
 * @author Jan Tuitjer
 */
public class Main {
    static final String FILE_PATH_USER = "conf/hybridConfigs/1.userknn-test.properties";
    static final String FILE_PATH_ITEM = "conf/hybridConfigs/2.itemknn-test.properties";
    private static HybridConfiguration HybridConfiguration;

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
        HybridRecommenderJob hrj = new HybridRecommenderJob(hybridConf);
        hrj.runJob();
    }
}
