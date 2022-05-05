package weka.ubu;

import weka.classifiers.trees.REPTree;
import weka.core.Instances;
import weka.core.Randomizable;

import java.util.Random;

public class RandomREPTree extends REPTree implements Randomizable {

  static final long serialVersionUID = 6710515739446441536L;

  public void buildClassifier(Instances data) throws Exception {
    Random r = data.getRandomNumberGenerator( getSeed() );
    setSeed( r.nextInt() );
    super.buildClassifier( data );
  }

  public static void main(String[] argv) {
    runClassifier(new RandomREPTree(), argv);
  }

}
