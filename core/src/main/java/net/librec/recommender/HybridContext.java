package net.librec.recommender;
import net.librec.common.AbstractContext;
import net.librec.conf.Configuration;
import net.librec.data.DataModel;
import net.librec.similarity.RecommenderSimilarity;
import java.util.ArrayList;
import java.util.List;

/**
 * @author Jan Tuitjer
 */

public class HybridContext extends AbstractContext {
    private List<RecommenderSimilarity> similarityList;
    private List<DataModel> dataModelList;
    private List<Configuration> configurations;

    public HybridContext(){
        super();
    }

    public HybridContext(Configuration _conf){
        super();
        this.similarityList = new ArrayList<>();
        this.dataModelList = new ArrayList<>();
        this.conf = _conf;
        configurations = new ArrayList<Configuration>();
        configurations.add(this.conf);
    }

    public HybridContext(Configuration _conf, ArrayList<DataModel> _dataModelList, ArrayList<RecommenderSimilarity> _similarityList) {
        super();
        this.conf = _conf;
        this.dataModelList = _dataModelList;
        this.similarityList = _similarityList;
        configurations = new ArrayList<Configuration>();
        configurations.add(this.conf);
    }

    public HybridContext(ArrayList<Configuration> _configurations, ArrayList<DataModel> _dataModelList) {
        super();
        this.conf = _configurations.get(0);
        this.dataModelList = _dataModelList;
        this.similarityList = new ArrayList<>();
        configurations = _configurations;
    }

    public HybridContext(ArrayList<Configuration> _configurations, ArrayList<DataModel> _dataModelList, ArrayList<RecommenderSimilarity> _similarityList) {
        super();
        this.conf = _configurations.get(0);
        this.dataModelList = _dataModelList;
        this.similarityList = _similarityList;
        configurations = _configurations;
    }

    public RecommenderContext getContextFor(int _index){
        if(this.configurations.size()==1)
            return new RecommenderContext(conf, dataModelList.get(_index), similarityList.get(_index));
        return new RecommenderContext(this.configurations.get(_index), dataModelList.get(_index), similarityList.get(_index));
    }

    public void setSimilarityList(List<RecommenderSimilarity> _list){
        this.similarityList = _list;
    }

    public List<RecommenderSimilarity> getSimilarityList() {
        return similarityList;
    }

    public List<DataModel> getDataModelList() {
        return dataModelList;
    }

    public void setDataModelList(List<DataModel> dataModelList) {
        this.dataModelList = dataModelList;
    }

    public Configuration getConfiguration() {
        return this.conf;
    }

    public void setConfiguration(Configuration configuration) {
        this.conf = configuration;
    }

    public ArrayList<RecommenderContext> getContexts() {
        ArrayList<RecommenderContext> arr = new ArrayList<>(configurations.size());
        for (Configuration configuration : configurations) {
            arr.add(new RecommenderContext(configuration));
        }
        return arr;
    }

    @Override
    public String toString(){
        return "Configurations: " + configurations.size()+"\t DataModels: "+dataModelList.size()+" \tSimilarites: "+similarityList.size();
    }
}
