package net.librec.eval;

import net.librec.common.LibrecException;
import net.librec.conf.Configuration;
import net.librec.math.structure.DataSet;
import net.librec.math.structure.SequentialAccessSparseMatrix;
import net.librec.math.structure.SparseTensor;
import net.librec.math.structure.SymmMatrix;
import net.librec.recommender.Recommender;
import net.librec.recommender.TensorRecommender;
import net.librec.recommender.hybrid.AbstractHybridRecommender;
import net.librec.recommender.item.RecommendedList;
import net.librec.similarity.RecommenderSimilarity;

import java.util.Map;

public class HybridEvalContext extends EvalContext {
    private AbstractHybridRecommender hybridRecommender;

    public HybridEvalContext(Configuration conf, RecommendedList recommendedList, SequentialAccessSparseMatrix testMatrix, SymmMatrix similarityMatrix, Map<String, RecommenderSimilarity> similarities) {
        super(conf, recommendedList, testMatrix, similarityMatrix, similarities);
        System.out.println("DAFUQ");
    }

    public HybridEvalContext(Configuration conf, RecommendedList recommendedList, SequentialAccessSparseMatrix testMatrix) {
        super(conf, recommendedList, testMatrix);
        System.out.println("DAFUQ");
    }

    public HybridEvalContext(Configuration conf, Recommender recommender, DataSet testDataset) throws LibrecException {
        super(conf, recommender, testDataset);
        System.out.println("DAFUQ");
        initHybridRecommender(recommender);
    }

    public HybridEvalContext(Configuration conf, Recommender recommender, DataSet testDataset, SymmMatrix similarityMatrix, Map<String, RecommenderSimilarity> similarities) throws LibrecException {
        super(conf, recommender, testDataset, similarityMatrix, similarities);
        initHybridRecommender(recommender);
        System.out.println("DAFUQ");
    }

    private void initHybridRecommender(Recommender recommender) {
        System.out.println("HybridEvalContext.initHybridRecommender");
        if (recommender instanceof AbstractHybridRecommender) {
            hybridRecommender = (AbstractHybridRecommender) recommender;
        } else {
            throw new IllegalArgumentException("The given recommender for a HybridEvalContext object must be subtype of AbstractHybridRecommender");
        }
    }

    @Override
    public RecommendedList getGroundTruthListFromDataSet(DataSet dataset) {
        if (this.getRecommender() instanceof AbstractHybridRecommender) {
            hybridRecommender = (AbstractHybridRecommender) this.getRecommender();
            if (hybridRecommender.getHybridConf().getBoolean("data.model.sync", false)) {
                if (hybridRecommender.getRecommenders().get(0) instanceof TensorRecommender) {
                    return getGroundTruthListFromSparseTensor((SparseTensor) dataset);
                } else {
                    return getGroundTruthListFromSparseMatrix((SequentialAccessSparseMatrix) dataset);
                }
            } else {
                // to implement this feature the hybrid recommender must extract the ground truth entries of each contained
                // recommender. In this case it must be decided if every entry or only the common entries of the test data set
                // (the 'dataset' parameter) are of interest.
                throw new UnsupportedOperationException("The usage of unsynchronized data sets is not supported yet.");
            }
        } else {
            throw new IllegalArgumentException("The given recommender for a HybridEvalContext object must be subtype of AbstractHybridRecommender");
        }
    }
}
