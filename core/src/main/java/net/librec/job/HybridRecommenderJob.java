package net.librec.job;

import net.librec.common.LibrecException;
import net.librec.conf.Configuration;
import net.librec.conf.HybridConfiguration;
import net.librec.data.DataModel;
import net.librec.data.DataSplitter;
import net.librec.data.splitter.KCVDataSplitter;
import net.librec.data.splitter.LOOCVDataSplitter;
import net.librec.eval.EvalContext;
import net.librec.eval.Measure;
import net.librec.eval.RecommenderEvaluator;
import net.librec.math.algorithm.Randoms;
import net.librec.recommender.AbstractRecommender;
import net.librec.recommender.HybridContext;
import net.librec.recommender.Recommender;
import net.librec.recommender.RecommenderContext;
import net.librec.recommender.hybrid.AbstractHybridRecommender;
import net.librec.recommender.hybrid.WeightedHybridRecommender;
import net.librec.recommender.item.RecommendedItem;
import net.librec.similarity.RecommenderSimilarity;
import net.librec.util.DriverClassUtil;
import net.librec.util.ReflectionUtil;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * @author Jan Tuitjer
 */
public class HybridRecommenderJob extends RecommenderJob{
    private HybridConfiguration hybridConfig;
    private HybridContext hybridContext;

    private ArrayList<DataModel> dataModels;
    private ArrayList<RecommenderContext> contexts;
    private AbstractHybridRecommender hybridRecommender;

    public HybridRecommenderJob(HybridConfiguration hybridConfiguration) throws LibrecException, IOException, ClassNotFoundException {
        super(new Configuration());
        hybridConfig = hybridConfiguration;
        assert (hybridConfig.getConfigs().size() > 1);
        initalizeComponents();
    }

    private void initalizeComponents() throws LibrecException, IOException, ClassNotFoundException {
        Long seed = hybridConfig.getLong("rec.random.seed");
        if (seed != null) {
            Randoms.seed(seed);
        }
        //setJobId(JobUtil.generateNewJobId());
        initHybridRecommender();
        initializeDataModels();
        initHybridContext();
    }

    private void initHybridContext() {
        hybridContext = new HybridContext(hybridConfig.getConfigs(), dataModels);
        hybridRecommender.setHybridContext(hybridContext);
        contexts = new ArrayList<>(hybridConfig.getConfigs().size());
    }

    public void runJob() throws LibrecException, IOException, ClassNotFoundException {
        assert(sameFolds());
        cvEvalResults = new HashMap<>();
        while(haveNextFolds()){
            nextDataModel();
            nextSimilarities();
            trainHybridRecommender();
            evaluateHybrid(hybridRecommender, hybridContext);
        }
        printCVAverageResult();
        boolean isRanking = hybridConfig.getBoolean("rec.recommender.isranking");
        List<RecommendedItem> recommendedList = null;
        if (isRanking){
            recommendedList = hybridRecommender.getRecommendedList(hybridRecommender.recommendRank());
        } else {
            recommendedList = hybridRecommender.getRecommendedList(hybridRecommender.recommendRating(hybridRecommender.getCommonTestDataSet()));
        }
        recommendedList = filterResult(recommendedList);
        saveResult(recommendedList);
    }

    private void evaluateHybrid(AbstractHybridRecommender hybridRecommender, HybridContext hybridContext) throws LibrecException, IOException, ClassNotFoundException {
        EvalContext evalContext = new EvalContext(hybridConfig, hybridRecommender, hybridRecommender.getCommonTestDataSet());
        evaluatedMap = new HashMap<>();
        boolean isRanking = hybridConfig.getBoolean("rec.recommender.isranking");
        int topN = 10;
        if (isRanking) {
            topN = hybridConfig.getInt("rec.recommender.ranking.topn", 10);
            if (topN <= 0) {
                throw new IndexOutOfBoundsException("rec.recommender.ranking.topn should be more than 0!");
            }
        }
        List<Measure.MeasureValue> measureValueList = Measure.getMeasureEnumList(isRanking, topN);
        if (measureValueList != null) {
            for (Measure.MeasureValue measureValue : measureValueList) {
                RecommenderEvaluator evaluator = ReflectionUtil
                        .newInstance(measureValue.getMeasure().getEvaluatorClass());
                if (isRanking && measureValue.getTopN() != null && measureValue.getTopN() > 0) {
                    evaluator.setTopN(measureValue.getTopN());
                }
                double evaluatedValue = evaluator.evaluate(evalContext);
                evaluatedMap.put(measureValue, evaluatedValue);
            }
        }
        if (evaluatedMap.size() > 0) {
            for (Map.Entry<Measure.MeasureValue, Double> entry : evaluatedMap.entrySet()) {
                String evalName = null;
                if (entry != null && entry.getKey() != null) {
                    if (entry.getKey().getTopN() != null && entry.getKey().getTopN() > 0) {
                        LOG.info("Evaluator value:" + entry.getKey().getMeasure() + " top " + entry.getKey().getTopN() + " is " + entry.getValue());
                        evalName = entry.getKey().getMeasure() + " top " + entry.getKey().getTopN();
                    } else {
                        LOG.info("Evaluator value:" + entry.getKey().getMeasure() + " is " + entry.getValue());
                        evalName = entry.getKey().getMeasure() + "";
                    }
                    if (null != cvEvalResults) {
                        collectCVResults(evalName, entry.getValue());
                    }
                }
            }
        }
    }

    private void collectCVResults(String _evalName, double _value){
        DataSplitter splitter = dataModels.get(0).getDataSplitter();
        if (splitter != null && (splitter instanceof KCVDataSplitter || splitter instanceof LOOCVDataSplitter)) {
            if (cvEvalResults.containsKey(_evalName)) {
                cvEvalResults.get(_evalName).add(_value);
            } else {
                List<Double> newList = new ArrayList<>();
                newList.add(_value);
                cvEvalResults.put(_evalName, newList);
            }
        }
    }

    private void printCVAverageResult(){
        DataSplitter splitter = dataModels.get(0).getDataSplitter();
        if (splitter != null && (splitter instanceof KCVDataSplitter || splitter instanceof LOOCVDataSplitter)) {
            LOG.info("Average Evaluation Result of Cross Validation:");
            for (Map.Entry<String, List<Double>> entry : cvEvalResults.entrySet()) {
                String evalName = entry.getKey();
                List<Double> evalList = entry.getValue();
                double sum = 0.0;
                for (double value : evalList) {
                    sum += value;
                }
                double avgEvalResult = sum / evalList.size();
                LOG.info("Evaluator value:" + evalName + " is " + avgEvalResult);
            }
        }
    }

    private void trainHybridRecommender() throws LibrecException {
        hybridRecommender.trainModel();
    }

    private void initHybridRecommender() throws IOException, ClassNotFoundException {
        hybridRecommender = (AbstractHybridRecommender) ReflectionUtil.newInstance((Class<Recommender>) getRecommenderClass(), hybridConfig);
        ArrayList<AbstractRecommender> usedRecommenders = new ArrayList<>();
        for(Configuration c : hybridConfig.getConfigs()){
            AbstractRecommender rec = ReflectionUtil.newInstance((Class<AbstractRecommender>) getRecommenderClass(c));
            usedRecommenders.add(rec);
        }
        hybridRecommender.setRecommenders(usedRecommenders);
        if(hybridRecommender instanceof WeightedHybridRecommender){
            if (null != hybridConfig.get("rec.hybrid.weights")){
                String[] weights = hybridConfig.get("rec.hybrid.weights").split(":");
                double[] realWeights = new double[weights.length];
                for (int i = 0; i < weights.length ; i++) {
                    realWeights[i] = Double.parseDouble(weights[i]);
                }
                assert(realWeights.length == hybridRecommender.getRecommenders().size());
                ((WeightedHybridRecommender)hybridRecommender).setWeights(realWeights);
            }
        }
    }

    @Override
    public Class<? extends Recommender> getRecommenderClass() throws ClassNotFoundException, IOException {
        return (Class<? extends Recommender>) DriverClassUtil.getClass(hybridConfig.get("rec.hybrid.class"));
    }
    private Class<? extends Recommender> getRecommenderClass(Configuration _c) throws ClassNotFoundException, IOException {
        return (Class<? extends Recommender>) DriverClassUtil.getClass(_c.get("rec.recommender.class"));
    }

    private void initializeDataModels() throws ClassNotFoundException, IOException, LibrecException {
        if (null == dataModels) {
            dataModels = new ArrayList<>();
            for (int i = 0; i < hybridConfig.getConfigs().size(); i++) {
                if(hybridConfig.getBoolean("data.model.sync")) {
                    Long seed = hybridConfig.getLong("rec.random.seed", 42l);
                    if (seed != null) {
                        Randoms.seed(seed);
                    }
                }
                DataModel data = ReflectionUtil.newInstance((Class<DataModel>) this.getDataModelClass(i), hybridConfig.getConfigs().get(i));
                data.buildDataModel();
                dataModels.add(data);
            }
        }
    }
//    private void initializeDataModels() throws ClassNotFoundException, IOException, LibrecException {
//        if (null == dataModels) {
//            dataModels = new ArrayList<>();
//            if (hybridConfig.getBoolean("data.model.sync")) {
//                for (int i = 0; i < hybridConfig.getConfigs().size();i++) {
//                    Configuration curConf = hybridConfig.getConfigs().get(i);
//                    String curDataFormat = curConf.get("data.model.format");
//                    DataModel data = ReflectionUtil.newInstance((Class<DataModel>) this.getDataModelClass(i), curConf);
//                    dataModels.add(data);
//                }
//                syncDataModels();
//                for (DataModel dat : dataModels){
//                    dat.buildDataModel();
//                }
//            } else {
//                for (int i = 0; i < hybridConfig.getConfigs().size(); i++) {
//                    Long seed = hybridConfig.getLong("rec.random.seed");
//                    if (seed != null) {
//                        Randoms.seed(seed);
//                    }
//                    DataModel data = ReflectionUtil.newInstance((Class<DataModel>) this.getDataModelClass(i), hybridConfig.getConfigs().get(i));
//                    data.buildDataModel();
//                    dataModels.add(data);
//                }
//            }
//        }
//    }

    private void syncDataModels() {

    }

    public Class<? extends DataModel> getDataModelClass(int _index) throws ClassNotFoundException, IOException {
        return (Class<? extends DataModel>) DriverClassUtil.getClass(hybridConfig.getConfigs().get(_index).get("data.model.format"));
    }

    private boolean haveNextFolds() {
        boolean folds = true;
        for (DataModel model: dataModels){
            folds &= model.hasNextFold();
        }
        return folds;
    }

    private void nextSimilarities() {
        contexts= hybridContext.getContexts();
        ArrayList<RecommenderSimilarity> similarities = new ArrayList<>();
        for (int i = 0; i < contexts.size(); i++) {
            contexts.get(i).setDataModel(dataModels.get(i));
            generateSimilarity(contexts.get(i));
            similarities.add(contexts.get(i).getSimilarity());
        }
        hybridContext.setSimilarityList(similarities);
    }

    public Class<? extends RecommenderSimilarity> getSimilarityClass(Configuration _conf) {
        try {
            return (Class<? extends RecommenderSimilarity>) DriverClassUtil.getClass(_conf.get("rec.similarity.class"));
        } catch (ClassNotFoundException e) {
            return null;
        }
    }

    private void generateSimilarity(RecommenderContext context) {
        context.resetSimilarities();
        int index = contexts.indexOf(context);
        Configuration conf = hybridConfig.getConfigs().get(index);
        String[] similarityKeys = conf.getStrings("rec.recommender.similarities");
        if (similarityKeys != null && similarityKeys.length > 0) {
            for (int i = 0; i < similarityKeys.length; i++) {
                if (getSimilarityClass(conf) != null) {
                    RecommenderSimilarity similarity = ReflectionUtil.newInstance(getSimilarityClass(conf), conf);
                    conf.set("rec.recommender.similarity.key", similarityKeys[i]);
                    similarity.buildSimilarityMatrix(dataModels.get(index));
                  if (i == 0) {
                        context.setSimilarity(similarity);
                    }
                    context.addSimilarities(similarityKeys[i], similarity);
                }
            }
        }
    }

    private void nextDataModel() throws LibrecException {
        for(DataModel model : dataModels){
            model.nextFold();
        }
        hybridContext.setDataModelList(dataModels);
    }

    private boolean sameFolds() {
        int[] numFolds = new int[hybridConfig.getConfigs().size()];
        for (int i = 0; i < numFolds.length; i++) {
            numFolds[i] = Integer.parseInt(hybridConfig.getConfigs().get(i).get("data.splitter.cv.number"));
        }
        boolean check;
        int len = numFolds.length;
        int a = 0;
        while(a < len && numFolds[a]==numFolds[0]) {
            a++;
        }
        check=(a==len);
        return check;
    }
}
