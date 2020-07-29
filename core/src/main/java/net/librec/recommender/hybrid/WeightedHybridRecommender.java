package net.librec.recommender.hybrid;

import net.librec.common.LibrecException;
import net.librec.recommender.AbstractRecommender;
import net.librec.recommender.HybridContext;
import net.librec.recommender.item.GenericRecommendedItem;
import net.librec.recommender.item.RecommendedItem;

import java.util.ArrayList;
import java.util.Arrays;

/**
 * @Author Jan Tuitjer
 *
 */

public class WeightedHybridRecommender extends AbstractHybridRecommender {
    protected double[] weights;
    public WeightedHybridRecommender(){
        super();
    }

    public WeightedHybridRecommender(ArrayList<AbstractRecommender> _recommenders, HybridContext _hybridContext) {
        super(_recommenders, _hybridContext);
    }

    /**
     * Constructor ensures that each recommender in _recommenders has it's own weight
     * the sum of all weights in _weights must be equal to 1
     * @param _recommenders
     * @param _hybridContext
     * @param _weights
     */
    public WeightedHybridRecommender(ArrayList<AbstractRecommender> _recommenders, HybridContext _hybridContext, double[] _weights) {
        super(_recommenders, _hybridContext);
        if (_weights.length != _recommenders.size()) {
            throw new IllegalArgumentException(getClass().getSimpleName() + " :Each given recommender must have it's own weight!");
        }
        double totalWeight = 0.0;
        for (double w : _weights) {
            totalWeight += w;
        }
        if (Double.compare(1.0, totalWeight) != 0) {
            throw new IllegalArgumentException(getClass().getSimpleName() + " :The combined weights must have a value of 1.0");
        }
        weights = _weights;
    }

    @Override
    protected ArrayList<RecommendedItem> handleRecommendedItems(AbstractRecommender _recommender, ArrayList<RecommendedItem> _commonElements) throws LibrecException {
        if (null == weights) {
            return handleRecommendedItemsSameWeights(_recommender, _commonElements);
        } else {
            return handleRecommendedItemsWithWeights(_recommender, _commonElements);
        }
    }

    //TODO: remove contain check if hybrid Config contains sync flag
    private ArrayList<RecommendedItem> handleRecommendedItemsWithWeights(AbstractRecommender _recommender, ArrayList<RecommendedItem> _commonElements) throws LibrecException {
        ArrayList<RecommendedItem> toRemove = new ArrayList<>();
        int recommenderIndex = recommenders.indexOf(_recommender);
        ArrayList<RecommendedItem> recommenderItems = (ArrayList<RecommendedItem>) _recommender.getRecommendedList();
        if (_recommender == recommenders.get(0)) {
            // first recommender -> can add all elements
            for (RecommendedItem recItem : recommenderItems) {
                ((GenericRecommendedItem) recItem).setValue(recItem.getValue() * weights[recommenderIndex]);
                _commonElements.add(recItem);
            }
            return _commonElements;
        } else {
            for (RecommendedItem item : _commonElements) {
                if (!recommenderItems.contains(item)) {
                    //item is not in the recommendedItem list
                    toRemove.add(item);
                } else {
                    //item is in recommendedItem list
                    ((GenericRecommendedItem) item).setValue(item.getValue() + weights[recommenderIndex] * recommenderItems.get(recommenderItems.indexOf(item)).getValue());
                }
            }
            _commonElements.removeAll(toRemove);
            System.out.println("toRemove = " + toRemove.size());
        }
        return _commonElements;
    }
    //TODO: remove contain check if hybrid Config contains sync flag
    private ArrayList<RecommendedItem> handleRecommendedItemsSameWeights(AbstractRecommender _recommender, ArrayList<RecommendedItem> _commonElements) throws LibrecException {
        ArrayList<RecommendedItem> toRemove = new ArrayList<>();
        if (_recommender == recommenders.get(0)) {
            // first recommender -> can add all elements
            _commonElements.addAll(_recommender.getRecommendedList());
            return _commonElements;
        }
        ArrayList<RecommendedItem> tmpList = (ArrayList<RecommendedItem>) _recommender.getRecommendedList();
        for (RecommendedItem item : _commonElements) {
            if (!tmpList.contains(item)) {
                //item is not in the recommendedItem list
                toRemove.add(item);
            } else {
                //item is a common element
                if (_recommender != recommenders.get(recommenders.size() - 1)) {
                    // recommender is not the last recommender in recommenders
                    ((GenericRecommendedItem) item).setValue(item.getValue() + tmpList.get(tmpList.indexOf(item)).getValue());
                } else {
                    // recommender is last recommender in recommenders
                    ((GenericRecommendedItem) item).setValue(
                            (item.getValue() +tmpList.get(tmpList.indexOf(item)).getValue()) / recommenders.size());
                }
            }
        }
        _commonElements.removeAll(toRemove);
        System.out.println("toRemove = " + toRemove.size());
        return _commonElements;
    }

    public double[] getWeights() {
        return weights;
    }

    public void setWeights(double[] _weights) {
        if(_weights.length != recommenders.size()){
            throw new IllegalArgumentException(getClass().getSimpleName() + " :Each given recommender must have it's own weight!");
        }
        double totalWeight = 0.0;
        for (double w : _weights) {
            totalWeight += w;
        }
        if (Double.compare(1.0, totalWeight) != 0) {
            throw new IllegalArgumentException(getClass().getSimpleName() + " :The combined weights must have a value of 1.0. Given: " + Arrays.toString(weights));
        }
        this.weights = _weights;
    }
}