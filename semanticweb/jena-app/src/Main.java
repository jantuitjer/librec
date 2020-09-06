import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.reasoner.Reasoner;
import org.apache.jena.reasoner.rulesys.GenericRuleReasoner;
import org.apache.jena.reasoner.rulesys.Rule;
import org.apache.jena.riot.RDFDataMgr;
import org.apache.jena.riot.RDFFormat;

public class Main {
	final static String FUSEKI_URL = "http://localhost:3030/movielens-2k";
	final static String FUSEKI_USER = "admin";
	final static String FUSEKI_PASSWORD = "admin";

	public static void main(String[] args) throws IOException {
		if (args.length == 0) {
			System.out.println("Need an operation mode.");
			System.out.println("'Data' to extend ttl-files");
			System.out.println("'Query' to execute queries");
			System.exit(-1);
		} else {
			if (args[0].toLowerCase().contentEquals("basis")) {
				executeBasisExpansion();
			} else if (args[0].toLowerCase().contentEquals("likes")) {
				processLikes();
			} else if (args[0].toLowerCase().contentEquals("recommend")) {
				executeRuleRecommend();
			} else {
				System.out.println("given mode is not supported!");
				System.exit(-1);
			}
		}
		System.out.println("Done");

	}
	/**
	 * estimates the likes of every user
	 * @throws IOException
	 */
	private static void processLikes() throws IOException {
		processLikesFile("file:abox/movielens-2k-genre.ttl", "abox/likes_genre.ttl");
		processLikesFile("file:abox/movielens-2k-region.ttl", "abox/likes_region.ttl");
		processLikesFile("file:abox/movielens-2k-director_smaller.ttl", "abox/likes_director_smaller.ttl");
	}
	
	private static void processLikesFile(String input, String output) throws IOException {
		Reasoner recommendRules = new GenericRuleReasoner(Rule.rulesFromURL("file:rules/likes_rules.jena"));
		recommendRules.setDerivationLogging(true);
		Model extendedModel = ModelFactory.createDefaultModel();
		extendedModel.read(input, "TURTLE");
		Model tBox = ModelFactory.createDefaultModel();
		tBox.read("file:tbox/tbox.ttl", "TURTLE"); 
		Model ruleModel = ModelFactory.createRDFSModel(tBox, extendedModel);
		Model recommendedModel = ModelFactory.createInfModel(recommendRules, ruleModel);
		Model dif = recommendedModel.difference(extendedModel);
		OutputStream os = new FileOutputStream(output);
		RDFDataMgr.write(os, dif, RDFFormat.TTL);
		os.close();
	}
/**
 * genereate recommendations for every user
 * @throws IOException
 */
	private static void executeRuleRecommend() throws IOException {
		Reasoner recommendRules = new GenericRuleReasoner(Rule.rulesFromURL("file:rules/recommend_rules.jena"));
		recommendRules.setDerivationLogging(true);
		Model extendedModel = ModelFactory.createDefaultModel();
		extendedModel.read("file:abox/likes_genre.ttl", "TURTLE");
		extendedModel.read("file:abox/likes_region.ttl", "TURTLE");
		extendedModel.read("file:abox/likes_director_smaller.ttl", "TURTLE");
		extendedModel.read("file:abox/movie_info_extended.ttl", "TURTLE");
		OutputStream os = new FileOutputStream("abox/likes_model.ttl");
		RDFDataMgr.write(os, extendedModel, RDFFormat.TTL);
		os.close();
		extendedModel.read("file:abox/test.ttl", "TURTLE");
		Model tBox = ModelFactory.createDefaultModel();
		tBox.read("file:tbox/tbox.ttl", "TURTLE"); 
		Model ruleModel = ModelFactory.createRDFSModel(tBox, extendedModel);
		System.out.println("start recommending");
		Model recommendedModel = ModelFactory.createInfModel(recommendRules, ruleModel);
		os = new FileOutputStream("results/recommendations.ttl");
		RDFDataMgr.write(os, recommendedModel, RDFFormat.TTL);
		os.close();
	}

	private static void executeBasisExpansion() throws IOException {
		// load basic film rules
		Reasoner filmRules = new GenericRuleReasoner(Rule.rulesFromURL("file:rules/rs_basic_film_rules.jena"));
		filmRules.setDerivationLogging(true);
		// init tBox
		Model tBox = ModelFactory.createDefaultModel();
		tBox.read("file:tbox/tbox.ttl", "TURTLE");
		// init abox
		Model aBox = ModelFactory.createDefaultModel();
		aBox.read("file:abox/movie_info.ttl", "TURTLE");
		// apply rules
		Model ruleModel = ModelFactory.createInfModel(filmRules, aBox);
		// infer knowledge
		Model fullBasisModel = ModelFactory.createRDFSModel(tBox, ruleModel);
		// dump to file
		OutputStream os = new FileOutputStream("abox/movie_info_extended.ttl");
		RDFDataMgr.write(os, fullBasisModel, RDFFormat.TTL);
		os.close();
	}
}
