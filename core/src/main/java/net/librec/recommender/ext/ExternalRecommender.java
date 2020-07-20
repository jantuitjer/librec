package net.librec.recommender.ext;

import com.clearspring.analytics.util.Lists;
import com.google.common.collect.Maps;
import net.librec.annotation.ModelData;
import net.librec.common.LibrecException;
import net.librec.recommender.MatrixRecommender;

import java.util.List;
import java.util.Map;

/**
 * Suppose that you have some predictive ratings (in "pred.txt") generated by an external recommender (e.g., some
 * recommender of MyMediaLite). The predictions are in the format of user-item-prediction. These predictions are
 * corresponding to a test set "test.txt" (user-item-held_out_rating). This class (ExternalRecommender) provides you
 * with the ability to compute predictive performance by setting the training set as "pred.txt" and the test set as
 * "test.txt". <br>
 * <br>
 * <p>
 * <strong>NOTE:</strong> This approach is not applicable to item recommendation. Thank {@literal Marcel Ackermann} for
 * bringing this demand to my attention.
 *
 * @author Guo Guibing and Keqiang Wang
 */
@ModelData({"isRating", "external", "trainMatrix"})
public class ExternalRecommender extends MatrixRecommender {
    List<Map<Integer, Integer>> userItemsPosList = Lists.newArrayList();

    @Override
    public void trainModel() throws LibrecException {
        // plus to adapt to 3.0
        for (int userIdx = 0; userIdx < numUsers; userIdx++) {
            Map<Integer, Integer> itemIndexPosMap = Maps.newHashMap();
            int[] itemIndices = trainMatrix.row(userIdx).getIndices();
            for (int i = 0; i < itemIndices.length; i++) {
                itemIndexPosMap.put(itemIndices[i], i);
            }
            userItemsPosList.add(itemIndexPosMap);
        }
    }

    /**
     * predict a specific rating for user userIdx on item itemIdx.
     *
     * @param userIdx user index
     * @param itemIdx item index
     * @return predictive rating for user userIdx on item itemIdx
     * @throws LibrecException if error occurs
     */
    @Override
    protected double predict(int userIdx, int itemIdx) throws LibrecException {
        Map<Integer, Integer> currItemIndexPosMap = userItemsPosList.get(userIdx);

        return currItemIndexPosMap.get(itemIdx) != null ? currItemIndexPosMap.get(itemIdx) : 0.0;
    }
}
