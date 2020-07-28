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
//        final int RUNS = 50;
//        double mae_sum=0.0;
//        for (int i = 0; i < RUNS; i++) {
//            mae_sum+= hybridRun();
//        }
//        System.out.println("mae_sum/RUNS = " + mae_sum/RUNS);
//        testy();
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

    private static void testy() throws FileNotFoundException, LibrecException {
        Configuration conf1 = new Configuration();
        config.ConfigurationParser.parse(FILE_PATH_USER, conf1);
        Configuration conf2 = new Configuration();
        config.ConfigurationParser.parse(FILE_PATH_ITEM, conf2);
        AbstractDataModel d1 = new TextDataModel(conf1);
        d1.buildDataModel();
        AbstractDataModel d2 = new TextDataModel(conf2);
        d2.buildDataModel();
        d1.hasNextFold();
        d1.nextFold();
        d2.hasNextFold();
        d2.nextFold();
        RecommenderSimilarity s1 = new CosineSimilarity();
        RecommenderSimilarity s2 = new CosineSimilarity();
        s1.buildSimilarityMatrix(d1);
        s2.buildSimilarityMatrix(d2);
        AbstractRecommender r1 = new UserKNNRecommender();
        AbstractRecommender r2 = new ItemKNNRecommender();
        RecommenderContext c1 = new RecommenderContext(conf1, d1, s1);
        RecommenderContext c2 = new RecommenderContext(conf2, d2, s2);
        r1.train(c1);
//        r2.train(c2);
        ArrayList<RecommendedItem> rl1 = (ArrayList<RecommendedItem>) r1.getRecommendedList();
//        ArrayList<RecommendedItem> rl2 = (ArrayList<RecommendedItem>) r2.getRecommendedList();
        System.out.println("r1.getDataModel().getTestDataSet().size() = " + r1.getDataModel().getTestDataSet().size());
//        System.out.println("r2.getDataModel().getTestDataSet().size() = " + r2.getDataModel().getTestDataSet().size());
        System.out.println("rl1.size() = " + rl1.size());
//        System.out.println("rl2.size() = " + rl2.size());

        if (d1.getTestDataSet().size() == d2.getTestDataSet().size()) {
            for (int i = 0; i < d1.getTestDataSet().size(); i++) {
                d1.getDataConvertor().getPreferenceMatrix();
            }
        }
        System.exit(1);
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

    private static double hybridRun() throws FileNotFoundException, LibrecException {
        Configuration confUser = new Configuration();
        Configuration confItem = new Configuration();
        config.ConfigurationParser.parse(FILE_PATH_USER, confUser);
        config.ConfigurationParser.parse(FILE_PATH_ITEM, confItem);
        ArrayList<Configuration> confs = new ArrayList<Configuration>() {
            {
                add(confUser);
                add(confItem);
            }
        };
        DataModel userData = new TextDataModel(confUser);
        DataModel itemData = new TextDataModel(confItem);
        userData.buildDataModel();
        itemData.buildDataModel();
        ArrayList<DataModel> models = new ArrayList<DataModel>() {
            {
                add(userData);
                add(itemData);
            }
        };
        RecommenderSimilarity userSim = new CosineSimilarity();
        RecommenderSimilarity itemSim = new PCCSimilarity();
        userSim.buildSimilarityMatrix(userData);
        itemSim.buildSimilarityMatrix(itemData);
        ArrayList<RecommenderSimilarity> sims = new ArrayList<RecommenderSimilarity>() {
            {
                add(userSim);
                add(itemSim);
            }
        };
        AbstractRecommender userRec = new UserKNNRecommender();
        AbstractRecommender itemRec = new ItemKNNRecommender();
        ArrayList<AbstractRecommender> recommdenders = new ArrayList<AbstractRecommender>() {
            {
                add(userRec);
                add(itemRec);
            }
        };
        HybridContext hybridContext = new HybridContext(confs, models, sims);
        WeightedHybridRecommender whr = new WeightedHybridRecommender(recommdenders, hybridContext);
        whr.trainModel();
        RecommenderEvaluator eval = new MAEEvaluator();
        double mae = whr.evaluate(eval);
        System.out.println("mae = " + mae);
        return mae;
    }

    private static void test() throws FileNotFoundException, LibrecException {
        Configuration conf = new Configuration();
        config.ConfigurationParser.parse(FILE_PATH_ITEM, conf);
        TextDataModel data = new TextDataModel(conf);
        data.buildDataModel();
        System.out.println("data = " + data.getDataConvertor().getPreferenceMatrix().rowSize());
        System.out.println("data = " + data.getDataConvertor().getPreferenceMatrix().columnSize());
        RecommenderSimilarity sim = new PCCSimilarity();
        sim.buildSimilarityMatrix(data);
        System.out.println("sim.getSimilarityMatrix().toSparseMatrix().rowSize() = " + sim.getSimilarityMatrix().getDim());
        System.out.println("sim.getSimilarityMatrix().toSparseMatrix().columnSize() = " + sim.getSimilarityMatrix().row(sim.getSimilarityMatrix().getDim()).size());
        RecommenderContext context = new RecommenderContext(conf, data, sim);
        AbstractRecommender rec = new ItemKNNRecommender();
        rec.train(context);
        rec.recommendRank();
        rec.getRecommendedList();
    }
}
