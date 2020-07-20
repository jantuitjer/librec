package net.librec.recommender.item;

import net.librec.recommender.item.RecommendedItem;

import java.util.Comparator;
/**
 * @author Jan Tuitjer
 */
public class RecommendedItemComparator implements Comparator<RecommendedItem> {
    @Override
    public int compare(RecommendedItem o1, RecommendedItem o2) {
        int userVal = Integer.compare(Integer.parseInt(o1.getUserId()), Integer.parseInt(o2.getUserId()));
        int itemVal = Integer.compare(Integer.parseInt(o1.getItemId()), Integer.parseInt(o2.getItemId()));
        if (userVal != 0){
            // users are the same
            return userVal;
        }
        return itemVal;
    }
}
