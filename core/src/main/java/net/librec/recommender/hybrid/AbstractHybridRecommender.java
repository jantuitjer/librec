package net.librec.recommender.hybrid;

import net.librec.common.LibrecException;
import net.librec.conf.HybridConfiguration;
import net.librec.data.model.AbstractDataModel;
import net.librec.data.structure.AbstractBaseDataEntry;
import net.librec.data.structure.BaseDataList;
import net.librec.data.structure.BaseRatingDataEntry;
import net.librec.data.structure.LibrecDataList;
import net.librec.eval.RecommenderEvaluator;
import net.librec.eval.rating.MAEEvaluator;
import net.librec.math.structure.DataSet;
import net.librec.math.structure.SequentialAccessSparseMatrix;
import net.librec.math.structure.SequentialSparseVector;
import net.librec.recommender.AbstractRecommender;
import net.librec.recommender.HybridContext;
import net.librec.recommender.MatrixRecommender;
import net.librec.recommender.TensorRecommender;
import net.librec.recommender.item.*;
import sun.reflect.generics.reflectiveObjects.NotImplementedException;

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
        if (!hybridConf.getBoolean("data.model.sync", false)) {
            //default way
            SequentialAccessSparseMatrix commonTestMatrix = initCommonTestSetAndMatrix();
            commonTestMatrix.reshape();
            commonTestDataSet = commonTestMatrix;
            recommendedItemList.sort();
        } else {
            if (null == commonTestDataSet) {
                commonTestDataSet = recommenders.get(0).getDataModel().getTestDataSet();
            }
            ArrayList<RecommendedList> recommendations = new ArrayList<>();
            for (AbstractRecommender rec : recommenders) {
                recommendations.add(rec.recommendRating(predictDataSet));
            }
//            recommendedItemList = new RecommendedList(recommenders.get(0).getDataModel().getUserMappingData().size());
            recommendedItemList = recommendations.get(0);
            ArrayList<Iterator<ContextKeyValueEntry>> iterators = new ArrayList<>(recommendations.size());
            for (RecommendedList listy : recommendations){
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
        prevUser =-1;
        while(iterators.get(0).hasNext()){
            double currentPrediction = 0.0;
            int user =-1;
            int item =-1;
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

    @Override
    public RecommendedList recommendRating(LibrecDataList<AbstractBaseDataEntry> dataList) throws LibrecException {
        throw new NotImplementedException();
    }

    @Override
    public RecommendedList recommendRank() throws LibrecException {
        throw new NotImplementedException();

    }

    @Override
    public RecommendedList recommendRank(LibrecDataList<AbstractBaseDataEntry> dataList) throws LibrecException {
        throw new NotImplementedException();
    }

    public RecommendedList recommendRating() throws LibrecException {
        RecommendedList recList = new RecommendedList(recommenders.get(0).getDataModel().getUserMappingData().size());
        for (AbstractRecommender rec : recommenders) {
            Iterator it = rec.recommendRating(rec.getDataModel().getTestDataSet()).iterator();
            while (it.hasNext()) {
                ContextKeyValueEntry entry = (ContextKeyValueEntry) it.next();
                recList.add(entry.getContextIdx(), entry.getKeyIdx(), entry.getValue());
            }
        }
        return recList;
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
            if (null == commonTestDataSet) {
                commonTestDataSet = recommenders.get(0).getDataModel().getTestDataSet();
            }
        }
        return commonTestDataSet;
    }

    public void setHybridConfiguration(HybridConfiguration hybridConfig) {
        this.hybridConf = hybridConfig;
    }

    protected abstract double handleSingleRecommendedItem(int i, double value);

    protected abstract ArrayList<RecommendedItem> handleRecommendedItems(AbstractRecommender recommender, ArrayList<RecommendedItem> commonElements) throws LibrecException;
}
