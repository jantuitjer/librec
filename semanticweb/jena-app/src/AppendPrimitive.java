import org.apache.jena.reasoner.rulesys.BindingEnvironment;
import org.apache.jena.reasoner.rulesys.RuleContext;
import org.apache.jena.reasoner.rulesys.builtins.BaseBuiltin;
import org.apache.jena.graph.Node;
import org.apache.jena.graph.NodeFactory;
import org.apache.jena.reasoner.rulesys.Util;

public class AppendPrimitive extends BaseBuiltin {

	@Override
	public String getName() {
		return "append";
	}
	
	@Override
	public int getArgLength() {
		return 3;
	}
	
	  @Override
	  public void headAction(Node[] args, int length, RuleContext context) {
	    doUserRequiredAction(args, length, context);
	  }  
	  
	  @Override
	  public boolean bodyCall(Node[] args, int length, RuleContext context) {
	    return doUserRequiredAction(args, length, context);
	  }
	  
	  private boolean doUserRequiredAction(Node[] args, int length, RuleContext context) {
	    // Check we received the correct number of parameters
	    checkArgs(length, context);

	    boolean success = false;
	    
	    // Retrieve the input arguments
	    Node user = getArg(0, args, context);
	    Node genre = getArg(1, args, context);
	    Node userGenreInterest = null;
	    String user_string = user.getLocalName();
	    String genre_string = genre.getLocalName();
	    if(!user_string.contains("u_")|| !genre_string.contains("g_")) {
	    	throw new IllegalArgumentException("Parameters of append builtin must be a user and genre. Elements must have 'u_' or 'g_' in their local name!");
	    }
	    String user_genre_string = user_string+genre_string;
	    userGenreInterest = NodeFactory.createURI(user_genre_string);
	    // Binding the output parameter to the node
	    BindingEnvironment env = context.getEnv();
	    success = env.bind(args[2], userGenreInterest);
	     
	     
	    return success;
	  }
	}