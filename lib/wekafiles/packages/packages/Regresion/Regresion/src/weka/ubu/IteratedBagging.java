/*
 *    This program is free software; you can redistribute it and/or modify
 *    it under the terms of the GNU General Public License as published by
 *    the Free Software Foundation; either version 2 of the License, or
 *    (at your option) any later version.
 *
 *    This program is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU General Public License for more details.
 *
 *    You should have received a copy of the GNU General Public License
 *    along with this program; if not, write to the Free Software
 *    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

/*
 *    IteratedBagging.java
 *
 */

//package weka.classifiers.meta;
package weka.ubu;

import weka.classifiers.Classifier;
import weka.classifiers.RandomizableIteratedSingleClassifierEnhancer;
import weka.core.AdditionalMeasureProducer;
import weka.core.Instance;
import weka.core.Instances;
import weka.core.Option;
import weka.core.Randomizable;
import weka.core.RevisionUtils;
import weka.core.TechnicalInformation;
import weka.core.TechnicalInformationHandler;
import weka.core.Utils;
import weka.core.WeightedInstancesHandler;
import weka.core.TechnicalInformation.Field;
import weka.core.TechnicalInformation.Type;

import java.util.Enumeration;
import java.util.Random;
import java.util.Vector;

/**
 <!-- globalinfo-start -->
 * Class for bagging a classifier to reduce variance. Can do classification and regression depending on the base learner. <br/>
 * <br/>
 * For more information, see<br/>
 * <br/>
 * Leo Breiman (1996). IteratedBagging predictors. Machine Learning. 24(2):123-140.
 * <p/>
 <!-- globalinfo-end -->
 *
 <!-- technical-bibtex-start -->
 * BibTeX:
 * <pre>
 * &#64;article{Breiman1996,
 *    author = {Leo Breiman},
 *    journal = {Machine Learning},
 *    number = {2},
 *    pages = {123-140},
 *    title = {IteratedBagging predictors},
 *    volume = {24},
 *    year = {1996}
 * }
 * </pre>
 * <p/>
 <!-- technical-bibtex-end -->
 *
 <!-- options-start -->
 * Valid options are: <p/>
 * 
 * <pre> -P
 *  Size of each bag, as a percentage of the
 *  training set size. (default 100)</pre>
 * 
 * <pre> -O
 *  Calculate the out of bag error.</pre>
 * 
 * <pre> -S &lt;num&gt;
 *  Random number seed.
 *  (default 1)</pre>
 * 
 * <pre> -I &lt;num&gt;
 *  Number of iterations.
 *  (default 10)</pre>
 * 
 * <pre> -D
 *  If set, classifier is run in debug mode and
 *  may output additional info to the console</pre>
 * 
 * <pre> -W
 *  Full name of base classifier.
 *  (default: weka.classifiers.trees.REPTree)</pre>
 * 
 * <pre> 
 * Options specific to classifier weka.classifiers.trees.REPTree:
 * </pre>
 * 
 * <pre> -M &lt;minimum number of instances&gt;
 *  Set minimum number of instances per leaf (default 2).</pre>
 * 
 * <pre> -V &lt;minimum variance for split&gt;
 *  Set minimum numeric class variance proportion
 *  of train variance for split (default 1e-3).</pre>
 * 
 * <pre> -N &lt;number of folds&gt;
 *  Number of folds for reduced error pruning (default 3).</pre>
 * 
 * <pre> -S &lt;seed&gt;
 *  Seed for random data shuffling (default 1).</pre>
 * 
 * <pre> -P
 *  No pruning.</pre>
 * 
 * <pre> -L
 *  Maximum tree depth (default -1, no maximum)</pre>
 * 
 <!-- options-end -->
 *
 * Options after -- are passed to the designated classifier.<p>
 *
 * @author Eibe Frank (eibe@cs.waikato.ac.nz)
 * @author Len Trigg (len@reeltwo.com)
 * @author Richard Kirkby (rkirkby@cs.waikato.ac.nz)
 * @version $Revision: 1.41 $
 */
public class IteratedBagging
  extends RandomizableIteratedSingleClassifierEnhancer 
  implements WeightedInstancesHandler, AdditionalMeasureProducer,
             TechnicalInformationHandler {

  /** for serialization */
  static final long serialVersionUID = 3316027656290182749L;

  /** The size of each bag sample, as a percentage of the training size */
  protected int m_BagSizePercent = 100;

  /** The out of bag error that has been calculated */
  protected double m_OutOfBagError;  

  protected int m_BaggingIterations = 5;

  protected double m_Threshold = 1.1;

  /**
   * Constructor.
   */
  public IteratedBagging() {
    
    m_Classifier = new weka.classifiers.trees.REPTree();
  }
  
  /**
   * Returns a string describing classifier
   * @return a description suitable for
   * displaying in the explorer/experimenter gui
   */
  public String globalInfo() {
 
    return "Class for bagging a classifier to reduce variance. Can do classification "
      + "and regression depending on the base learner. \n\n"
      + "For more information, see\n\n"
      + getTechnicalInformation().toString();
  }

  /**
   * Returns an instance of a TechnicalInformation object, containing 
   * detailed information about the technical background of this class,
   * e.g., paper reference or book this class is based on.
   * 
   * @return the technical information about this class
   */
  public TechnicalInformation getTechnicalInformation() {
    TechnicalInformation 	result;
    
    result = new TechnicalInformation(Type.ARTICLE);
    result.setValue(Field.AUTHOR, "Leo Breiman");
    result.setValue(Field.YEAR, "1996");
    result.setValue(Field.TITLE, "IteratedBagging predictors");
    result.setValue(Field.JOURNAL, "Machine Learning");
    result.setValue(Field.VOLUME, "24");
    result.setValue(Field.NUMBER, "2");
    result.setValue(Field.PAGES, "123-140");
    
    return result;
  }

  /**
   * String describing default classifier.
   * 
   * @return the default classifier classname
   */
  protected String defaultClassifierString() {
    
    return "weka.classifiers.trees.REPTree";
  }

  /**
   * Returns an enumeration describing the available options.
   *
   * @return an enumeration of all the available options.
   */
  public Enumeration listOptions() {

    Vector newVector = new Vector(3);

    newVector.addElement(new Option(
              "\tSize of each bag, as a percentage of the\n" 
              + "\ttraining set size. (default 100)",
              "P", 1, "-P"));
    newVector.addElement(new Option(
              "\tNumber of iterations for each Bagging\n" 
              + "\t(default 5)",
              "N", 1, "-N"));
    newVector.addElement(new Option(
              "\tThreshold multiplier\n" 
              + "\t(default 1.1)",
              "M", 1, "-M"));

    Enumeration enu = super.listOptions();
    while (enu.hasMoreElements()) {
      newVector.addElement(enu.nextElement());
    }
    return newVector.elements();
  }


  /**
   * Parses a given list of options. <p/>
   *
   <!-- options-start -->
   * Valid options are: <p/>
   * 
   * <pre> -P
   *  Size of each bag, as a percentage of the
   *  training set size. (default 100)</pre>
   * 
   * <pre> -O
   *  Calculate the out of bag error.</pre>
   * 
   * <pre> -S &lt;num&gt;
   *  Random number seed.
   *  (default 1)</pre>
   * 
   * <pre> -I &lt;num&gt;
   *  Number of iterations.
   *  (default 10)</pre>
   * 
   * <pre> -D
   *  If set, classifier is run in debug mode and
   *  may output additional info to the console</pre>
   * 
   * <pre> -W
   *  Full name of base classifier.
   *  (default: weka.classifiers.trees.REPTree)</pre>
   * 
   * <pre> 
   * Options specific to classifier weka.classifiers.trees.REPTree:
   * </pre>
   * 
   * <pre> -M &lt;minimum number of instances&gt;
   *  Set minimum number of instances per leaf (default 2).</pre>
   * 
   * <pre> -V &lt;minimum variance for split&gt;
   *  Set minimum numeric class variance proportion
   *  of train variance for split (default 1e-3).</pre>
   * 
   * <pre> -N &lt;number of folds&gt;
   *  Number of folds for reduced error pruning (default 3).</pre>
   * 
   * <pre> -S &lt;seed&gt;
   *  Seed for random data shuffling (default 1).</pre>
   * 
   * <pre> -P
   *  No pruning.</pre>
   * 
   * <pre> -L
   *  Maximum tree depth (default -1, no maximum)</pre>
   * 
   <!-- options-end -->
   *
   * Options after -- are passed to the designated classifier.<p>
   *
   * @param options the list of options as an array of strings
   * @throws Exception if an option is not supported
   */
  public void setOptions(String[] options) throws Exception {

    String bagSize = Utils.getOption('P', options);
    if (bagSize.length() != 0) {
      setBagSizePercent(Integer.parseInt(bagSize));
    } else {
      setBagSizePercent(100);
    }

    String threshold = Utils.getOption('M', options);
    if (threshold.length() != 0) {
      setThreshold(Double.parseDouble(threshold));
    } else {
      setThreshold(1.1);
    }

    String bagIterations = Utils.getOption('N', options);
    if (bagIterations.length() != 0) {
      setBaggingIterations(Integer.parseInt(bagIterations));
    } else {
      setBaggingIterations(5);
    }

    super.setOptions(options);
  }

  /**
   * Gets the current settings of the Classifier.
   *
   * @return an array of strings suitable for passing to setOptions
   */
  public String [] getOptions() {


    String [] superOptions = super.getOptions();
    String [] options = new String [superOptions.length + 6];

    int current = 0;
    options[current++] = "-P"; 
    options[current++] = "" + getBagSizePercent();

    options[current++] = "-V"; 
    options[current++] = "" + getThreshold();

    options[current++] = "-N"; 
    options[current++] = "" + getBaggingIterations();

    System.arraycopy(superOptions, 0, options, current, 
		     superOptions.length);

    current += superOptions.length;
    while (current < options.length) {
      options[current++] = "";
    }
    return options;
  }

  /**
   * Returns the tip text for this property
   * @return tip text for this property suitable for
   * displaying in the explorer/experimenter gui
   */
  public String bagSizePercentTipText() {
    return "Size of each bag, as a percentage of the training set size.";
  }

  /**
   * Gets the size of each bag, as a percentage of the training set size.
   *
   * @return the bag size, as a percentage.
   */
  public int getBagSizePercent() {

    return m_BagSizePercent;
  }
  
  /**
   * Sets the size of each bag, as a percentage of the training set size.
   *
   * @param newBagSizePercent the bag size, as a percentage.
   */
  public void setBagSizePercent(int newBagSizePercent) {

    m_BagSizePercent = newBagSizePercent;
  }

  public String numBaggingIterationsTipText() {
    return "Number of iterations for each Bagging.";
  }

  public int getBaggingIterations() {
    return m_BaggingIterations;
  }

  public void setBaggingIterations(int num) {
    m_BaggingIterations = num;
  }

  public String thresholdTipText() {
    return "Threshold for the mean sum of squares.";
  }

  public double getThreshold() {
    return m_Threshold;
  }

  public void setThreshold(double num) {
    m_Threshold = num;
  }

  /**
   * Gets the out of bag error that was calculated as the classifier
   * was built.
   *
   * @return the out of bag error 
   */
  public double measureOutOfBagError() {
    
    return m_OutOfBagError;
  }
  
  /**
   * Returns an enumeration of the additional measure names.
   *
   * @return an enumeration of the measure names
   */
  public Enumeration enumerateMeasures() {
    
    Vector newVector = new Vector(1);
    newVector.addElement("measureOutOfBagError");
    return newVector.elements();
  }
  
  /**
   * Returns the value of the named measure.
   *
   * @param additionalMeasureName the name of the measure to query for its value
   * @return the value of the named measure
   * @throws IllegalArgumentException if the named measure is not supported
   */
  public double getMeasure(String additionalMeasureName) {
    
    if (additionalMeasureName.equalsIgnoreCase("measureOutOfBagError")) {
      return measureOutOfBagError();
    }
    else {throw new IllegalArgumentException(additionalMeasureName 
					     + " not supported (IteratedBagging)");
    }
  }

  /**
   * Creates a new dataset of the same size using random sampling
   * with replacement according to the given weight vector. The
   * weights of the instances in the new dataset are set to one.
   * The length of the weight vector has to be the same as the
   * number of instances in the dataset, and all weights have to
   * be positive.
   *
   * @param data the data to be sampled from
   * @param random a random number generator
   * @param sampled indicating which instance has been sampled
   * @return the new dataset
   * @throws IllegalArgumentException if the weights array is of the wrong
   * length or contains negative weights.
   */
  public final Instances resampleWithWeights(Instances data,
					     Random random, 
					     boolean[] sampled) {

    double[] weights = new double[data.numInstances()];
    for (int i = 0; i < weights.length; i++) {
      weights[i] = data.instance(i).weight();
    }
    Instances newData = new Instances(data, data.numInstances());
    if (data.numInstances() == 0) {
      return newData;
    }
    double[] probabilities = new double[data.numInstances()];
    double sumProbs = 0, sumOfWeights = Utils.sum(weights);
    for (int i = 0; i < data.numInstances(); i++) {
      sumProbs += random.nextDouble();
      probabilities[i] = sumProbs;
    }
    Utils.normalize(probabilities, sumProbs / sumOfWeights);

    // Make sure that rounding errors don't mess things up
    probabilities[data.numInstances() - 1] = sumOfWeights;
    int k = 0; int l = 0;
    sumProbs = 0;
    while ((k < data.numInstances() && (l < data.numInstances()))) {
      if (weights[l] < 0) {
	throw new IllegalArgumentException("Weights have to be positive.");
      }
      sumProbs += weights[l];
      while ((k < data.numInstances()) &&
	     (probabilities[k] <= sumProbs)) { 
	newData.add(data.instance(l));
	sampled[l] = true;
	newData.instance(k).setWeight(1);
	k++;
      }
      l++;
    }
    return newData;
  }

  /**
   * IteratedBagging method.
   *
   * @param data the training data to be used for generating the
   * bagged classifier.
   * @throws Exception if the classifier could not be built successfully
   */
  public void buildClassifier(Instances data) throws Exception {

    // can classifier handle the data?
    getCapabilities().testWithFail(data);

    // remove instances with missing class
    data = new Instances(data);
    data.deleteWithMissingClass();
    
    super.buildClassifier(data);

/*
    if (m_CalcOutOfBag && (m_BagSizePercent != 100)) {
      throw new IllegalArgumentException("Bag size needs to be 100% if " +
					 "out-of-bag error is to be calculated!");
    }
*/

    int bagSize = data.numInstances() * m_BagSizePercent / 100;
    Random random = data.getRandomNumberGenerator(m_Seed);
    
    boolean[][] inBag = null;
    inBag = new boolean[m_Classifiers.length][];
   
    double bestOutOfBagError = Double.POSITIVE_INFINITY;
    int bestIteration = 0;

    for (int i = 0, j = 0; j < m_Classifiers.length; j++) {
      Instances bagData = null;

      // create the in-bag dataset
      inBag[j] = new boolean[data.numInstances()];
      bagData = resampleWithWeights(data, random, inBag[j]);
      
      if (m_Classifier instanceof Randomizable) {
	((Randomizable) m_Classifiers[j]).setSeed(random.nextInt());
      }
      
      // build the classifier
      m_Classifiers[j].buildClassifier(bagData);

      i++;
      if( i == m_BaggingIterations || j == m_Classifiers.length - 1) {
        double outOfBagCount = 0.0;
        double errorSum = 0.0;
        for (int k = 0; k < data.numInstances(); k++) {
	  Instance instance = data.instance(k);
          double vote = 0.0;
          int voteCount = 0;
          for (int l = j - i + 1; l <= j; l++) {
            if (inBag[l][k])
	      continue;
	    voteCount++;
	    vote += m_Classifiers[l].classifyInstance(instance);
	  }
	  double residue;
          if (voteCount == 0) {
	    // The instance was in all the Bags, the oob predictions cannot
	    // be used. The prediction is obtained from all the classifiers.
            for (int l = j - i + 1; l <= j; l++) {
	      voteCount++;
	      vote += m_Classifiers[l].classifyInstance(instance);
	    }
            vote /= voteCount;
	    residue = instance.classValue() - vote;
	  }
	  else {
            vote /= voteCount;
	    residue = instance.classValue() - vote;
	    outOfBagCount += instance.weight();
	    // errorSum += instance.weight() * StrictMath.abs( residue );
	    errorSum += instance.weight() * residue * residue;
	  }
	  instance.setClassValue( residue );
	}
	double outOfBagError = errorSum / outOfBagCount;
	//System.err.println( "outOfBagError:" + outOfBagError + "\n" );
	if( outOfBagError < bestOutOfBagError ) {
	  bestOutOfBagError = outOfBagError;
	  bestIteration = j;
	}
	else if( outOfBagError > m_Threshold * bestOutOfBagError ) {
	  break;
	}
        i = 0;
      }
      
    }
    if( bestIteration < m_Classifiers.length ) {
      Classifier [] classifiers = new Classifier[ bestIteration + 1 ];
      System.arraycopy( m_Classifiers, 0, classifiers, 0, bestIteration + 1 );
      m_Classifiers = classifiers;
    }
   
  }

  public double classifyInstance(Instance instance) throws Exception {
    double globalSum = 0.0;
    double sum = 0.0;
    for (int i = 0, j = 0; i < m_Classifiers.length; i++) {
      sum += m_Classifiers[i].classifyInstance(instance);
      j++;
      if( j == m_BaggingIterations || i == m_Classifiers.length - 1 ) {
        sum /= j;
	globalSum += sum;
	sum = 0.0;
        j = 0;
      }
    }
    return globalSum;
  }

  /**
   * Returns description of the bagged classifier.
   *
   * @return description of the bagged classifier as a string
   */
  public String toString() {
    
    if (m_Classifiers == null) {
      return "IteratedBagging: No model built yet.";
    }
    StringBuffer text = new StringBuffer();
    text.append( m_Classifiers.length + " base classifiers.\n");
    text.append("All the base classifiers: \n\n");
    for (int i = 0; i < m_Classifiers.length; i++) {
      text.append( "\nBase classifier " + i + ":\n");
      text.append(m_Classifiers[i].toString() + "\n\n");
    }
    
    return text.toString();
  }
  
  /**
   * Returns the revision string.
   * 
   * @return		the revision
   */
  public String getRevision() {
    return RevisionUtils.extract("$Revision: 1.41 $");
  }

  /**
   * Main method for testing this class.
   *
   * @param argv the options
   */
  public static void main(String [] argv) {
    runClassifier(new IteratedBagging(), argv);
  }
}
