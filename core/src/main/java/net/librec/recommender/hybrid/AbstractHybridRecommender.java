package net.librec.recommender.hybrid;

import it.unimi.dsi.fastutil.Hash;
import net.librec.common.LibrecException;
import net.librec.conf.HybridConfiguration;
import net.librec.data.model.AbstractDataModel;
import net.librec.data.structure.AbstractBaseDataEntry;
import net.librec.data.structure.LibrecDataList;
import net.librec.math.structure.DataSet;
import net.librec.math.structure.SequentialAccessSparseMatrix;
import net.librec.math.structure.SequentialSparseVector;
import net.librec.recommender.AbstractRecommender;
import net.librec.recommender.HybridContext;
import net.librec.recommender.item.*;

import java.util.*;

/**
 * @author Jan Tuitjer
 */
public abstract class AbstractHybridRecommender extends AbstractRecommender {
    protected ArrayList<AbstractRecommender> recommenders;
    protected HybridContext hybridContext;
    private RecommendedList recommendedItemList;
    private DataSet commonTestDataSet;
    HybridConfiguration hybridConf;

    public AbstractHybridRecommender(ArrayList<AbstractRecommender> _recommenders, HybridContext _hybridContext, HybridConfiguration _hybridConf) {
        recommenders = _recommenders;
        hybridContext = _hybridContext;
        hybridConf = _hybridConf;
    }

    public AbstractHybridRecommender(ArrayList<AbstractRecommender> _recommenders, HybridContext _hybridContext) {
        recommenders = _recommenders;
        hybridContext = _hybridContext;
    }

    public AbstractHybridRecommender() {
    }

    protected SequentialAccessSparseMatrix initCommonTestSetAndMatrix() throws LibrecException {
        SequentialAccessSparseMatrix preferenceMatrix = ((AbstractDataModel) recommenders.get(0).getDataModel()).getDataConvertor().getPreferenceMatrix();
        SequentialAccessSparseMatrix commonTestMatrix = initEmptyTestMatrixEntries(preferenceMatrix);
        RecommendedList recommendedItems = new RecommendedList(preferenceMatrix.rowSize());
        for (int i = 0; i < preferenceMatrix.rowSize(); i++) {
            recommendedItems.addList(new ArrayList<>());
        }
        fillCommonTestSetAndMatrix(recommendedItems, commonTestMatrix);
        commonTestMatrix.reshape();
        recommendedItems.sort();
        for (AbstractRecommender rec : recommenders) {
            rec.getRecommendedList(recommendedItems);
        }
        recommendedItemList = recommendedItems;
        return commonTestMatrix;
    }

    protected void fillCommonTestSetAndMatrix(RecommendedList _recommendedList, SequentialAccessSparseMatrix _commonTestMatrix) throws LibrecException {
        ArrayList<RecommendedItem> commonElements = new ArrayList<>();
        for (AbstractRecommender recommender : recommenders) {
            commonElements = handleRecommendedItems(recommender, commonElements);
        }
        commonElements.sort(new RecommendedItemComparator());
        int prevUser = -1;
        Map<Integer, List<KeyValue<Integer, Double>>> entryMap = new HashMap<>();
        List<KeyValue<Integer, Double>> itemValueList = new ArrayList<>();
        for (RecommendedItem commonItem : commonElements) {
            //save all relevant values with simple name
            //required to get the actual ratings in the test matrix -> using mapped user/item ids
            int user = recommenders.get(0).getDataModel().getUserMappingData().get(commonItem.getUserId());
            int item = recommenders.get(0).getDataModel().getItemMappingData().get(commonItem.getItemId());
            double realValue = recommenders.get(0).getDataModel().getDataSplitter().getTestData().get(user, item);
            double predictedValue = commonItem.getValue();
            // add test entry into common test matrix
            _commonTestMatrix.set(user, item, realValue);
            //save previous/first user id
            if (prevUser == -1) {
                prevUser = user;
                entryMap.put(user, itemValueList);
            }
            if (prevUser == user) {
                // add current common item into user list
                itemValueList.add(new KeyValue<>(item, predictedValue));
            } else {
                //new user -> write old list and create new empty list
//                _recommendedList.setList(prevUser, itemValueList);
                prevUser = user;
                itemValueList = new ArrayList<>();
                entryMap.put(user, itemValueList);
                itemValueList.add(new KeyValue<>(item, predictedValue));
            }
        }
        for (Integer user : entryMap.keySet()) {
            _recommendedList.setList(user, entryMap.get(user));
        }
        _commonTestMatrix.reshape();
        commonTestDataSet = _commonTestMatrix;
    }

    protected SequentialAccessSparseMatrix initEmptyTestMatrixEntries(SequentialAccessSparseMatrix preferenceMatrix) {
        SequentialAccessSparseMatrix commonTestMatrix = new SequentialAccessSparseMatrix(preferenceMatrix);
        for (int u = 0, um = preferenceMatrix.rowSize(); u < um; u++) {
            SequentialSparseVector items = preferenceMatrix.row(u);
            for (int j : items.getIndices()) {
                commonTestMatrix.set(u, j, 0.0);
            }
        }
        return commonTestMatrix;
    }


    @Override
    public void trainModel() throws LibrecException {
        for (int i = 0; i < recommenders.size(); i++) {
            recommenders.get(i).train(hybridContext.getContextFor(i));
        }
    }


    /*  @Override
      public void trainModel() throws LibrecException {
          ArrayList<Thread> trainTreads = new ArrayList<>(recommenders.size());
          for (int i = 0; i < recommenders.size(); i++) {
              final int counter = i;
              trainTreads.add(new Thread(() -> {
                  try {
                      recommenders.get(counter).train(hybridContext.getContextFor(counter));
                  } catch (LibrecException e) {
                      e.printStackTrace();
                  }
              }));
          }
          for (Thread t : trainTreads) {
              t.start();
          }
          for (Thread t : trainTreads) {
              try {
                  t.join();
              } catch (InterruptedException e) {
                  System.err.println("Critical error. A thread which was training a recommender was interrupted!.");
                  System.err.println(e);
              }
          }
      }*/
    @Override
    public RecommendedList recommendRating(DataSet predictDataSet) throws LibrecException {
        if (!getSyncMode()) {
            //default way
            SequentialAccessSparseMatrix commonTestMatrix = initCommonTestSetAndMatrix();
            commonTestMatrix.reshape();
            commonTestDataSet = commonTestMatrix;
            recommendedItemList.sort();
        } else {
            ArrayList<RecommendedList> recommendations = new ArrayList<>();
            for (AbstractRecommender rec : recommenders) {
                recommendations.add(rec.recommendRating(rec.getDataModel().getTestDataSet()));
            }
//            recommendedItemList = new RecommendedList(recommenders.get(0).getDataModel().getUserMappingData().size());
            recommendedItemList = recommendations.get(0);
            ArrayList<Iterator<ContextKeyValueEntry>> iterators = new ArrayList<>(recommendations.size());
            for (RecommendedList listy : recommendations) {
                iterators.add(listy.iterator());
            }
            combineRecommendedLists(iterators);
        }
        return recommendedItemList;
    }

    private void combineRecommendedLists(ArrayList<Iterator<ContextKeyValueEntry>> iterators) {
        int prevUser = -1;
        Map<Integer, List<KeyValue<Integer, Double>>> entryMap = new HashMap<>();
        List<KeyValue<Integer, Double>> itemValueList = new ArrayList<>();
        prevUser = -1;
        while (iterators.get(0).hasNext()) {
            double currentPrediction = 0.0;
            int user = -1;
            int item = -1;
            for (int i = 0; i < iterators.size(); i++) {
                ContextKeyValueEntry ckve = iterators.get(i).next();
                user = ckve.getContextIdx();
                item = ckve.getKey();
                currentPrediction += handleSingleRecommendedItem(i, ckve.getValue());
            }
            if (prevUser == -1) {
                prevUser = user;
                entryMap.put(user, itemValueList);
            }
            if (prevUser == user) {
                // add current common item into user list
                itemValueList.add(new KeyValue<>(item, currentPrediction));
            } else {
//                    new user -> write old list and create new empty list
//                _recommendedList.setList(prevUser, itemValueList);
                prevUser = user;
                itemValueList = new ArrayList<>();
                entryMap.put(user, itemValueList);
                itemValueList.add(new KeyValue<>(item, currentPrediction));
            }
        }
        for (Integer user : entryMap.keySet()) {
            recommendedItemList.setList(user, entryMap.get(user));
        }
    }

    protected void combineRecommendedListsRanking(ArrayList<Iterator<ContextKeyValueEntry>> iterators){
        int prevUser = -1;
        //iteratorIndex, user, item, value
        Map<Integer, Map<Integer, List<KeyValue<Integer, Double>>>> entryMap = new HashMap<>();
        double[] maxValues = new double[iterators.size()];
        while (iterators.get(0).hasNext()) {
            int[] users = new int[iterators.size()];
            int[] items = new int[iterators.size()];
            double[] values = new double[iterators.size()];
            for (int i = 0; i < iterators.size(); i++) {
                ContextKeyValueEntry ckve = iterators.get(i).next();
                users[i] = ckve.getContextIdx(); //users should always be the same
                items[i] = ckve.getKey(); //items can differ due to score
                values[i] = ckve.getValue();
                if (Double.compare(values[i], maxValues[i]) > 0){
                    maxValues[i] = values[i];
                }
            }
            if (users[0] != users[1]) {
                System.err.println("ERROR: Not the same users in evaluation!");
                System.exit(-9);
            }
            if (prevUser == users[0]){
                for (int iteratorIndex = 0; iteratorIndex < iterators.size(); iteratorIndex++) {
                    entryMap.get(iteratorIndex).get(users[iteratorIndex]).add(new KeyValue<>(items[iteratorIndex], values[iteratorIndex]));
                }
            }else{
                for (int iteratorIndex = 0; iteratorIndex < iterators.size(); iteratorIndex++) {
                    if (prevUser == -1){
                        Map<Integer,List<KeyValue<Integer, Double>>> userItemsValueMap = new HashMap<>();
                        entryMap.put(iteratorIndex, userItemsValueMap);
                    }
                    List<KeyValue<Integer, Double>> tmpList = new ArrayList<>();
                    tmpList.add(new KeyValue<>(items[iteratorIndex], values[iteratorIndex]));
                    entryMap.get(iteratorIndex).put(users[iteratorIndex], tmpList);
                }
                prevUser = users[0];
            }
        }
//        System.out.println("entryMap.size() = " + entryMap.size());
//        System.out.println("entryMap.get(0) = " + entryMap.get(0));
//        System.out.println("entryMap = " + entryMap.get(0).size());
        for(Integer user_index : entryMap.get(0).keySet()){
            Map<Integer, Double> item_values = new HashMap<>();
            for (int i = 0; i < iterators.size(); i++) {
                List<KeyValue<Integer, Double>> list =  entryMap.get(i).get(user_index);
                for (KeyValue<Integer, Double> item : list) {
                    double normalized_value = handleSingleRecommendedItem(i, item.getValue()) / maxValues[i];
                    if(item_values.containsKey(item.getKey())){
//                        double val = item_values.get(item.getKey()) + handleSingleRecommendedItem(i, item.getValue());
                        double val = item_values.get(item.getKey()) + normalized_value;
                        item_values.put(item.getKey(), val);
                    }else{
//                        item_values.put(item.getKey(), handleSingleRecommendedItem(i, item.getValue()));
                        item_values.put(item.getKey(), normalized_value);
                    }
                }
            }
            List<KeyValue<Integer, Double>> result_list = new ArrayList<>();
            for (Integer item : item_values.keySet()) {
                result_list.add(new KeyValue<>(item, item_values.get(item)));
            }
            recommendedItemList.setList(user_index, result_list);
        }
    }

    @Override
    public RecommendedList recommendRank() throws LibrecException {
        if (!getSyncMode()) {
            throw new UnsupportedOperationException("Ranking of unsynchronized data sets is not implemented yet");
        }else {
            ArrayList<RecommendedList> recommendationLists = new ArrayList<>(recommenders.size());
            for (AbstractRecommender rec : recommenders) {
                if(hybridConf.getBoolean("rec.rating.rank", true)) {
                    recommendationLists.add(rec.recommendRating(rec.getDataModel().getTestDataSet()));
                }else {
                    recommendationLists.add(rec.recommendRank());
                }
            }
//            recommendedItemList = new RecommendedList(recommenders.get(0).getDataModel().getUserMappingData().size());
            recommendedItemList = recommendationLists.get(0);
            ArrayList<Iterator<ContextKeyValueEntry>> iterators = new ArrayList<>(recommendationLists.size());
            for (RecommendedList listy : recommendationLists) {
                iterators.add(listy.iterator());
            }
            if(hybridConf.getBoolean("rec.rating.rank", true)) {
                combineRecommendedLists(iterators);
            }else{
                combineRecommendedListsRanking(iterators);
            }
            recommendedItemList.topNRank(hybridConf.getInt("rec.recommender.ranking.topn", 10));
            return  recommendedItemList;
        }
    }

    @Override
    public RecommendedList recommendRating(LibrecDataList<AbstractBaseDataEntry> dataList) throws LibrecException {
        ArrayList<RecommendedList> recommendationLists = new ArrayList<>(recommenders.size());
        for (AbstractRecommender rec : recommenders) {
            recommendationLists.add(rec.recommendRating(dataList));
        }
        return recommendationLists.get(0);
    }

    @Override
    public RecommendedList recommendRank(LibrecDataList<AbstractBaseDataEntry> dataList) throws LibrecException {
        ArrayList<RecommendedList> recommendationLists = new ArrayList<>(recommenders.size());
        for (AbstractRecommender rec : recommenders) {
            recommendationLists.add(rec.recommendRank(dataList));
        }
        return recommendationLists.get(0);
    }

    public ArrayList<AbstractRecommender> getRecommenders() {
        return recommenders;
    }

    public void setRecommenders(ArrayList<AbstractRecommender> usedRecommenders) {
        recommenders = usedRecommenders;
    }

    public void setHybridContext(HybridContext hybridContext) {
        this.hybridContext = hybridContext;
    }

    public DataSet getCommonTestDataSet() throws LibrecException {
        if (!hybridConf.getBoolean("data.model.sync", false)) {
            initCommonTestSetAndMatrix();
        } else {
//            initCommomTestSet();
            commonTestDataSet = recommenders.get(0).getDataModel().getTestDataSet();
        }
        return commonTestDataSet;
    }

    public void initCommomTestSet() {
        SequentialAccessSparseMatrix preferenceMatrix = ((AbstractDataModel) recommenders.get(0).getDataModel()).getDataConvertor().getPreferenceMatrix();
        SequentialAccessSparseMatrix commonTestMatrix = initEmptyTestMatrixEntries(preferenceMatrix);
        SequentialAccessSparseMatrix tmp = (SequentialAccessSparseMatrix) recommenders.get(0).getDataModel().getTestDataSet();
        for (int i = 0; i < tmp.rowSize(); i++) {
            for (int j = 0; j < tmp.columnSize(); j++) {
                commonTestMatrix.set(i, j, tmp.get(i, j));
            }
        }
        commonTestDataSet = commonTestMatrix;
    }

    public void setHybridConfiguration(HybridConfiguration hybridConfig) {
        this.hybridConf = hybridConfig;
    }

    private boolean getSyncMode() {
        return hybridConf.getBoolean("data.model.sync", false);
    }

    public HybridConfiguration getHybridConf(){
        return hybridConf;
    }

    protected abstract double handleSingleRecommendedItem(int i, double value);

    protected abstract ArrayList<RecommendedItem> handleRecommendedItems(AbstractRecommender recommender, ArrayList<RecommendedItem> commonElements) throws LibrecException;
}
