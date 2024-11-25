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
 *    AdaBoostR2.java
 *
 */

// package weka.classifiers.meta;
package weka.ubu;

import weka.classifiers.Classifier;
import weka.classifiers.Evaluation;
import weka.classifiers.RandomizableIteratedSingleClassifierEnhancer;
import weka.core.Capabilities;
import weka.core.Instance;
import weka.core.Instances;
import weka.core.Option;
import weka.core.Randomizable;
import weka.core.RevisionUtils;
import weka.core.SelectedTag;
import weka.core.Tag;
import weka.core.TechnicalInformation;
import weka.core.TechnicalInformationHandler;
import weka.core.Utils;
import weka.core.WeightedInstancesHandler;
import weka.core.Capabilities.Capability;
import weka.core.TechnicalInformation.Field;
import weka.core.TechnicalInformation.Type;

import java.util.Arrays;
import java.util.Comparator;
import java.util.Enumeration;
import java.util.Random;
import java.util.Vector;

/**
 <!-- globalinfo-start -->
 * Class for boosting a nominal class classifier using the Adaboost M1 method. Only nominal class problems can be tackled. Often dramatically improves performance, but sometimes overfits.<br/>
 * <br/>
 * For more information, see<br/>
 * <br/>
 * Yoav Freund, Robert E. Schapire: Experiments with a new boosting algorithm. In: Thirteenth International Conference on Machine Learning, San Francisco, 148-156, 1996.
 * <p/>
 <!-- globalinfo-end -->
 *
 <!-- technical-bibtex-start -->
 * BibTeX:
 * <pre>
 * &#64;inproceedings{Freund1996,
 *    address = {San Francisco},
 *    author = {Yoav Freund and Robert E. Schapire},
 *    booktitle = {Thirteenth International Conference on Machine Learning},
 *    pages = {148-156},
 *    publisher = {Morgan Kaufmann},
 *    title = {Experiments with a new boosting algorithm},
 *    year = {1996}
 * }
 * </pre>
 * <p/>
 <!-- technical-bibtex-end -->
 *
 <!-- options-start -->
 * Valid options are: <p/>
 * 
 * <pre> -P &lt;num&gt;
 *  Percentage of weight mass to base training on.
 *  (default 100, reduce to around 90 speed up)</pre>
 * 
 * <pre> -Q
 *  Use resampling for boosting.</pre>
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
 *  (default: weka.classifiers.trees.DecisionStump)</pre>
 * 
 * <pre> 
 * Options specific to classifier weka.classifiers.trees.DecisionStump:
 * </pre>
 * 
 * <pre> -D
 *  If set, classifier is run in debug mode and
 *  may output additional info to the console</pre>
 * 
 <!-- options-end -->
 *
 * Options after -- are passed to the designated classifier.<p>
 *
 * @author Eibe Frank (eibe@cs.waikato.ac.nz)
 * @author Len Trigg (trigg@cs.waikato.ac.nz)
 * @version $Revision: 1.40 $ 
 */
public class AdaBoostR2 
  extends RandomizableIteratedSingleClassifierEnhancer 
  implements WeightedInstancesHandler, TechnicalInformationHandler {

  /** for serialization */
  static final long serialVersionUID = -8151872680081662092L;

  /** Max num iterations tried to find classifier with non-zero error. */ 
  private static int MAX_NUM_RESAMPLING_ITERATIONS = 10;
  
  /** Array for storing the weights for the votes. */
  protected double [] m_Betas;

  /** The number of successfully generated base classifiers. */
  protected int m_NumIterationsPerformed;

  /** Weight Threshold. The percentage of weight mass used in training */
  protected int m_WeightThreshold = 100;

  /** Use boosting with reweighting? */
  protected boolean m_UseResampling;

  /** a ZeroR model in case no model can be built from the data */
  protected Classifier m_ZeroR;

  public static final int LOSS_LINEAR = 0;
  public static final int LOSS_SQUARE = 1;
  public static final int LOSS_EXPONENTIAL = 2;

  public static final Tag[] TAGS_LOSS_FUNCTION  = {
    new Tag(LOSS_LINEAR, "linear"),
    new Tag(LOSS_SQUARE, "square"),
    new Tag(LOSS_EXPONENTIAL, "exponential" )
  };

  protected int m_LossFunction = LOSS_LINEAR;

  public void setLossFunction(SelectedTag value) {
    if (value.getTags() == TAGS_LOSS_FUNCTION)
      m_LossFunction = value.getSelectedTag().getID();
  }

  public SelectedTag getLossFunction() {
    return new SelectedTag(m_LossFunction, TAGS_LOSS_FUNCTION);
  
  }
  public String LossFunctionTipText() {
    return "The loss function to use.";
  }

  /**
   * Constructor.
   */
  public AdaBoostR2() {
    
    m_Classifier = new weka.classifiers.trees.DecisionStump();
  }
    
  /**
   * Returns a string describing classifier
   * @return a description suitable for
   * displaying in the explorer/experimenter gui
   */
  public String globalInfo() {
 
    return "Class for boosting a nominal class classifier using the Adaboost "
      + "M1 method. Only nominal class problems can be tackled. Often "
      + "dramatically improves performance, but sometimes overfits.\n\n"
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
    
    result = new TechnicalInformation(Type.INPROCEEDINGS);
    result.setValue(Field.AUTHOR, "Yoav Freund and Robert E. Schapire");
    result.setValue(Field.TITLE, "Experiments with a new boosting algorithm");
    result.setValue(Field.BOOKTITLE, "Thirteenth International Conference on Machine Learning");
    result.setValue(Field.YEAR, "1996");
    result.setValue(Field.PAGES, "148-156");
    result.setValue(Field.PUBLISHER, "Morgan Kaufmann");
    result.setValue(Field.ADDRESS, "San Francisco");
    
    return result;
  }

  /**
   * String describing default classifier.
   * 
   * @return the default classifier classname
   */
  protected String defaultClassifierString() {
    
    return "weka.classifiers.trees.DecisionStump";
  }

  /**
   * Select only instances with weights that contribute to 
   * the specified quantile of the weight distribution
   *
   * @param data the input instances
   * @param quantile the specified quantile eg 0.9 to select 
   * 90% of the weight mass
   * @return the selected instances
   */
  protected Instances selectWeightQuantile(Instances data, double quantile) { 

    int numInstances = data.numInstances();
    Instances trainData = new Instances(data, numInstances);
    double [] weights = new double [numInstances];

    double sumOfWeights = 0;
    for(int i = 0; i < numInstances; i++) {
      weights[i] = data.instance(i).weight();
      sumOfWeights += weights[i];
    }
    double weightMassToSelect = sumOfWeights * quantile;
    int [] sortedIndices = Utils.sort(weights);

    // Select the instances
    sumOfWeights = 0;
    for(int i = numInstances - 1; i >= 0; i--) {
      Instance instance = (Instance)data.instance(sortedIndices[i]).copy();
      trainData.add(instance);
      sumOfWeights += weights[sortedIndices[i]];
      if ((sumOfWeights > weightMassToSelect) && 
	  (i > 0) && 
	  (weights[sortedIndices[i]] != weights[sortedIndices[i - 1]])) {
	break;
      }
    }
    if (m_Debug) {
      System.err.println("Selected " + trainData.numInstances()
			 + " out of " + numInstances);
    }
    return trainData;
  }

  /**
   * Returns an enumeration describing the available options.
   *
   * @return an enumeration of all the available options.
   */
  public Enumeration listOptions() {

    Vector newVector = new Vector();

    newVector.addElement(new Option(
	"\tPercentage of weight mass to base training on.\n"
	+"\t(default 100, reduce to around 90 speed up)",
	"P", 1, "-P <num>"));
    
    newVector.addElement(new Option(
	"\tUse resampling for boosting.",
	"Q", 0, "-Q"));

    newVector.addElement(new Option(
    	"\tSet loss function (default: 0)\n"
	+ "\t\t 0 = linear\n"
	+ "\t\t 1 = square\n"
	+ "\t\t 2 = exponential",
	"L", 1, "-L <int>"));

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
   * <pre> -P &lt;num&gt;
   *  Percentage of weight mass to base training on.
   *  (default 100, reduce to around 90 speed up)</pre>
   * 
   * <pre> -Q
   *  Use resampling for boosting.</pre>
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
   *  (default: weka.classifiers.trees.DecisionStump)</pre>
   * 
   * <pre> 
   * Options specific to classifier weka.classifiers.trees.DecisionStump:
   * </pre>
   * 
   * <pre> -D
   *  If set, classifier is run in debug mode and
   *  may output additional info to the console</pre>
   * 
   <!-- options-end -->
   *
   * Options after -- are passed to the designated classifier.<p>
   *
   * @param options the list of options as an array of strings
   * @throws Exception if an option is not supported
   */
  public void setOptions(String[] options) throws Exception {

    String thresholdString = Utils.getOption('P', options);
    if (thresholdString.length() != 0) {
      setWeightThreshold(Integer.parseInt(thresholdString));
    } else {
      setWeightThreshold(100);
    }
      
    setUseResampling(Utils.getFlag('Q', options));

    String lossStr = Utils.getOption('L', options);
    if (lossStr.length() != 0)
      setLossFunction(
          new SelectedTag(Integer.parseInt(lossStr), TAGS_LOSS_FUNCTION));
    else
      setLossFunction(
          new SelectedTag(LOSS_LINEAR, TAGS_LOSS_FUNCTION));

    super.setOptions(options);
  }

  /**
   * Gets the current settings of the Classifier.
   *
   * @return an array of strings suitable for passing to setOptions
   */
  public String[] getOptions() {
    Vector        result;
    String[]      options;
    int           i;
    
    result = new Vector();

    if (getUseResampling())
      result.add("-Q");

    result.add("-P");
    result.add("" + getWeightThreshold());
    
    result.add("-L");
    result.add("" + m_LossFunction);

    options = super.getOptions();
    for (i = 0; i < options.length; i++)
      result.add(options[i]);

    return (String[]) result.toArray(new String[result.size()]);
  }
  
  /**
   * Returns the tip text for this property
   * @return tip text for this property suitable for
   * displaying in the explorer/experimenter gui
   */
  public String weightThresholdTipText() {
    return "Weight threshold for weight pruning.";
  }

  /**
   * Set weight threshold
   *
   * @param threshold the percentage of weight mass used for training
   */
  public void setWeightThreshold(int threshold) {

    m_WeightThreshold = threshold;
  }

  /**
   * Get the degree of weight thresholding
   *
   * @return the percentage of weight mass used for training
   */
  public int getWeightThreshold() {

    return m_WeightThreshold;
  }
  
  /**
   * Returns the tip text for this property
   * @return tip text for this property suitable for
   * displaying in the explorer/experimenter gui
   */
  public String useResamplingTipText() {
    return "Whether resampling is used instead of reweighting.";
  }

  /**
   * Set resampling mode
   *
   * @param r true if resampling should be done
   */
  public void setUseResampling(boolean r) {

    m_UseResampling = r;
  }

  /**
   * Get whether resampling is turned on
   *
   * @return true if resampling output is on
   */
  public boolean getUseResampling() {

    return m_UseResampling;
  }

  /**
   * Returns default capabilities of the classifier.
   *
   * @return      the capabilities of this classifier
   */
  public Capabilities getCapabilities() {
    Capabilities result = super.getCapabilities();

    // class
    result.disableAllClasses();
    result.disableAllClassDependencies();
    if (super.getCapabilities().handles(Capability.NUMERIC_CLASS))
      result.enable(Capability.NUMERIC_CLASS);
    
    return result;
  }

  /**
   * Boosting method.
   *
   * @param data the training data to be used for generating the
   * boosted classifier.
   * @throws Exception if the classifier could not be built successfully
   */

  public void buildClassifier(Instances data) throws Exception {

    super.buildClassifier(data);

    // can classifier handle the data?
    getCapabilities().testWithFail(data);

    // remove instances with missing class
    data = new Instances(data);
    data.deleteWithMissingClass();
    
    m_ZeroR = null;
    
    if ((!m_UseResampling) && 
	(m_Classifier instanceof WeightedInstancesHandler)) {
      buildClassifierWithWeights(data);
    } else {
      buildClassifierUsingResampling(data);
    }
  }

  protected double [] calculateDifferences( Classifier c, Instances instances ) throws Exception {
    double [] differences = new double[ instances.numInstances() ];
    for( int i = 0; i < differences.length; i++ ) {
      Instance inst = instances.instance( i );
      double p = c.classifyInstance( inst );
      differences[ i ] = Math.abs( p - inst.classValue() );
      // System.err.println( "\ti:" + i + ", p: " + p + ", dif: " + differences[ i ] );
    }
    return differences;
  }

  public double lossFunction( double dif, double maxDif ) {
    switch( m_LossFunction ) {
      case LOSS_LINEAR: 
        return dif / maxDif;
      case LOSS_SQUARE: 
        double r = dif / maxDif;
        return r * r; 
      case LOSS_EXPONENTIAL: 
        return 1 - Math.exp( - dif / maxDif );
    }
    return 0;
  }

  public double lossFunction( double [] difs, double maxDif, 
      Instances instances, double [] losses ) {
    double loss = 0.0;
    for( int i = 0; i < difs.length; i++ ) {
      losses[ i ] = lossFunction( difs[ i ], maxDif );
      loss += losses[ i ] * instances.instance( i ).weight();
    }
    return loss;
  }


  /**
   * Boosting method. Boosts using resampling
   *
   * @param data the training data to be used for generating the
   * boosted classifier.
   * @throws Exception if the classifier could not be built successfully
   */
  protected void buildClassifierUsingResampling(Instances data) 
    throws Exception {

    Instances trainData, sample, training;
    double epsilon, reweight, sumProbs;
    Evaluation evaluation;
    int numInstances = data.numInstances();
    Random randomInstance = data.getRandomNumberGenerator(m_Seed);
    int resamplingIterations = 0;

    // Initialize data
    m_Betas = new double [m_Classifiers.length];
    m_NumIterationsPerformed = 0;
    // Create a copy of the data so that when the weights are diddled
    // with it doesn't mess up the weights for anyone else
    training = new Instances(data, 0, numInstances);
    double [] losses = new double[ numInstances ];

    sumProbs = training.sumOfWeights();
    for (int i = 0; i < training.numInstances(); i++) {
      training.instance(i).setWeight(training.instance(i).
				      weight() / sumProbs);
    }
    
    // Do boostrap iterations
    for (m_NumIterationsPerformed = 0; m_NumIterationsPerformed < m_Classifiers.length; 
	 m_NumIterationsPerformed++) {
      if (m_Debug) {
	System.err.println("Training classifier " + (m_NumIterationsPerformed + 1));
      }

      // Select instances to train the classifier on
      if (m_WeightThreshold < 100) {
	trainData = selectWeightQuantile(training, 
					 (double)m_WeightThreshold / 100);
      } else {
	trainData = new Instances(training);
      }
      
      // Resample
      resamplingIterations = 0;
      double[] weights = new double[trainData.numInstances()];
      for (int i = 0; i < weights.length; i++) {
	weights[i] = trainData.instance(i).weight();
      }
      double loss = 0.0;
      do {
	sample = trainData.resampleWithWeights(randomInstance, weights);

	// Build and evaluate classifier
	m_Classifiers[m_NumIterationsPerformed].buildClassifier(sample);

        // Evaluate the classifier
        double [] differences = calculateDifferences( m_Classifiers[m_NumIterationsPerformed], training );
        double maxDif = differences[ Utils.maxIndex( differences ) ];
        loss = lossFunction( differences, maxDif, training, losses );
	loss /= training.sumOfWeights();
	// System.err.println( loss );

	resamplingIterations++;
      } while (Utils.eq(loss, 0) && Utils.grOrEq(loss, 0.5) &&
	      (resamplingIterations < MAX_NUM_RESAMPLING_ITERATIONS));

      if ( Utils.eq(loss, 0)) {
        loss = 1e-10;
      }
      else if (Utils.grOrEq(loss, 0.5)) {
	if (m_NumIterationsPerformed == 0) {
	  m_NumIterationsPerformed = 1; // If we're the first we have to to use it
	}
	break;
      }

      // Determine the weight to assign to this model
      m_Betas[m_NumIterationsPerformed] = loss / (1 - loss);
      if (m_Debug) {
	System.err.println("\tloss = " + loss
			   +"  beta = " + m_Betas[m_NumIterationsPerformed]);
      }
 
      // Update instance weights
      setWeights(training, m_Betas[m_NumIterationsPerformed], losses);
      m_Betas[ m_NumIterationsPerformed ] = Math.log( 1 / m_Betas[ m_NumIterationsPerformed ]);
       	
    }
  }

  /**
   * Sets the weights for the next iteration.
   * 
   * @param training the training instances
   * @param reweight the reweighting factor
   * @throws Exception if something goes wrong
   */
  protected void setWeights(Instances training, double beta, double [] losses) 
    throws Exception {

    double oldSumOfWeights, newSumOfWeights;

    oldSumOfWeights = training.sumOfWeights();
    Enumeration enu = training.enumerateInstances();
    for (int i = 0; enu.hasMoreElements(); i++) {
      Instance instance = (Instance) enu.nextElement();
      instance.setWeight(instance.weight() * Math.pow( beta, 1 - losses[ i ] ) );
    }
    
    // Renormalize weights
    newSumOfWeights = training.sumOfWeights();
    enu = training.enumerateInstances();
    while (enu.hasMoreElements()) {
      Instance instance = (Instance) enu.nextElement();
      instance.setWeight(instance.weight() * oldSumOfWeights 
			 / newSumOfWeights);
    }
  }

  /**
   * Boosting method. Boosts any classifier that can handle weighted
   * instances.
   *
   * @param data the training data to be used for generating the
   * boosted classifier.
   * @throws Exception if the classifier could not be built successfully
   */
  protected void buildClassifierWithWeights(Instances data) 
    throws Exception {

    Instances trainData, training;
    double epsilon, reweight;
    Evaluation evaluation;
    int numInstances = data.numInstances();
    Random randomInstance = new Random(m_Seed);

    // Initialize data
    m_Betas = new double [m_Classifiers.length];
    m_NumIterationsPerformed = 0;

    // Create a copy of the data so that when the weights are diddled
    // with it doesn't mess up the weights for anyone else
    training = new Instances(data, 0, numInstances);
    double [] losses = new double[ numInstances ];
    
    // Do boostrap iterations
    for (m_NumIterationsPerformed = 0; m_NumIterationsPerformed < m_Classifiers.length; 
	 m_NumIterationsPerformed++) {
      if (m_Debug) {
	System.err.println("Training classifier " + (m_NumIterationsPerformed + 1));
      }
      // Select instances to train the classifier on
      if (m_WeightThreshold < 100) {
	trainData = selectWeightQuantile(training, 
					 (double)m_WeightThreshold / 100);
      } else {
	trainData = new Instances(training, 0, numInstances);
      }

      // Build the classifier
      if (m_Classifiers[m_NumIterationsPerformed] instanceof Randomizable)
	((Randomizable) m_Classifiers[m_NumIterationsPerformed]).setSeed(randomInstance.nextInt());
      // System.err.println(trainData);	
      m_Classifiers[m_NumIterationsPerformed].buildClassifier(trainData);

      // Evaluate the classifier
      double [] differences = calculateDifferences( m_Classifiers[m_NumIterationsPerformed], training );
      double maxDif = differences[ Utils.maxIndex( differences ) ];
      // System.err.println( "maxDif:" + maxDif );
      double loss = lossFunction( differences, maxDif, training, losses );
      loss /= training.sumOfWeights();

      if ( Utils.eq(loss, 0)) {
        loss = 1e-10;
      }
      else if (Utils.grOrEq(loss, 0.5)) {
	if (m_NumIterationsPerformed == 0) {
	  m_NumIterationsPerformed = 1; // If we're the first we have to to use it
	}
	break;
      }
      // Determine the weight to assign to this model
      m_Betas[m_NumIterationsPerformed] = loss / (1 - loss);
      if (m_Debug) {
	System.err.println("\tloss = " + loss
			   +"  beta = " + m_Betas[m_NumIterationsPerformed]);
      }

      // System.err.println( "loss: " + loss + ", maxDif:" + maxDif + ", beta:" + m_Betas[m_NumIterationsPerformed] );
 
      // Update instance weights
      setWeights(training, m_Betas[m_NumIterationsPerformed], losses);
      m_Betas[ m_NumIterationsPerformed ] = Math.log( 1 / m_Betas[ m_NumIterationsPerformed ]);
    }
  }


  static Pair [] m_Predictions = null;
  static PairComparator m_PairComparator = new PairComparator();

  public double classifyInstance(Instance instance) 
    throws Exception {
      
    // default model?
    if (m_ZeroR != null) {
      return m_ZeroR.classifyInstance(instance);
    }
    
    if (m_NumIterationsPerformed == 0) {
      throw new Exception("No model built");
    }
    
    if (m_NumIterationsPerformed == 1) {
      return m_Classifiers[0].classifyInstance(instance);
    } 

    if( m_Predictions == null || m_Predictions.length != 
        m_NumIterationsPerformed ) {
      m_Predictions = new Pair[m_NumIterationsPerformed]; 
      for (int i = 0; i < m_NumIterationsPerformed; i++) {
        m_Predictions[ i ] = new Pair();
      }
    }

    for (int i = 0; i < m_NumIterationsPerformed; i++) {
      m_Predictions[i].prediction = m_Classifiers[i].classifyInstance(instance);
      m_Predictions[i].weight = m_Betas[ i ];
    }

    Arrays.sort( m_Predictions, m_PairComparator );

    /*
    double s = 0;
    for (int i = 0; i < m_NumIterationsPerformed; i++) {
      s +=  predictions[ i ].weight;
      System.err.println( i + ", " + predictions[ i ].prediction + ", " + predictions[ i ].weight + ", " + s );
    }
    */

    double halfWeights = Utils.sum( m_Betas ) / 2.0;
    double sumWeights = 0;
    int i;
    for (i = 0; i < m_NumIterationsPerformed && sumWeights < halfWeights; i++) {
      sumWeights += m_Predictions[ i ].weight;
    }
    if( i > 0 ) {
      i--;
    }
    double p =  m_Predictions[ i ].prediction;
    if( sumWeights > halfWeights && i > 0 ) {
      p = ( p + m_Predictions[ i - 1 ].prediction ) / 2;
    }

    /*
    System.err.println( "i: " + i + ", sw: " + sumWeights + ", hw: " + halfWeights + ", p: " + p );
    System.err.println( );
    */

    return p;
  }

  class Pair {
    double prediction;
    double weight;
  }

  static class PairComparator implements Comparator<Pair> {
    public int compare( Pair p1, Pair p2 ) {
      if( p1.prediction >= p2.prediction ) {
        if( p1.prediction == p2.prediction )
	  return 0;
	return 1;
      }
      return -1;
    }
  }

  /**
   * Returns the boosted model as Java source code.
   *
   * @param className the classname of the generated class
   * @return the tree as Java source code
   * @throws Exception if something goes wrong
   */
  /*
  public String toSource(String className) throws Exception {
  /*
    if (m_NumIterationsPerformed == 0) {
      throw new Exception("No model built yet");
    }
    if (!(m_Classifiers[0] instanceof Sourcable)) {
      throw new Exception("Base learner " + m_Classifier.getClass().getName()
			  + " is not Sourcable");
    }

    StringBuffer text = new StringBuffer("class ");
    text.append(className).append(" {\n\n");

    text.append("  public static double classify(Object[] i) {\n");

    if (m_NumIterationsPerformed == 1) {
      text.append("    return " + className + "_0.classify(i);\n");
    } else {
      text.append("    double [] sums = new double [" + m_NumClasses + "];\n");
      for (int i = 0; i < m_NumIterationsPerformed; i++) {
	text.append("    sums[(int) " + className + '_' + i 
		    + ".classify(i)] += " + m_Betas[i] + ";\n");
      }
      text.append("    double maxV = sums[0];\n" +
		  "    int maxI = 0;\n"+
		  "    for (int j = 1; j < " + m_NumClasses + "; j++) {\n"+
		  "      if (sums[j] > maxV) { maxV = sums[j]; maxI = j; }\n"+
		  "    }\n    return (double) maxI;\n");
    }
    text.append("  }\n}\n");

    for (int i = 0; i < m_Classifiers.length; i++) {
	text.append(((Sourcable)m_Classifiers[i])
		    .toSource(className + '_' + i));
    }
    return text.toString();
  }
  */

  /**
   * Returns description of the boosted classifier.
   *
   * @return description of the boosted classifier as a string
   */
  public String toString() {
    
    // only ZeroR model?
    if (m_ZeroR != null) {
      StringBuffer buf = new StringBuffer();
      buf.append(this.getClass().getName().replaceAll(".*\\.", "") + "\n");
      buf.append(this.getClass().getName().replaceAll(".*\\.", "").replaceAll(".", "=") + "\n\n");
      buf.append("Warning: No model could be built, hence ZeroR model is used:\n\n");
      buf.append(m_ZeroR.toString());
      return buf.toString();
    }
    
    StringBuffer text = new StringBuffer();
    
    if (m_NumIterationsPerformed == 0) {
      text.append("AdaBoostR2: No model built yet.\n");
    } else if (m_NumIterationsPerformed == 1) {
      text.append("AdaBoostR2: No boosting possible, one classifier used!\n");
      text.append(m_Classifiers[0].toString() + "\n");
    } else {
      text.append("AdaBoostR2: Base classifiers and their weights: \n\n");
      for (int i = 0; i < m_NumIterationsPerformed ; i++) {
	text.append(m_Classifiers[i].toString() + "\n\n");
	text.append("Weight: " + Utils.roundDouble(m_Betas[i], 2) + "\n\n");
      }
      text.append("Number of performed Iterations: " 
		  + m_NumIterationsPerformed + "\n");
    }
    
    return text.toString();
  }
  
  /**
   * Returns the revision string.
   * 
   * @return		the revision
   */
  public String getRevision() {
    return RevisionUtils.extract("$Revision: 1.40 $");
  }

  /**
   * Main method for testing this class.
   *
   * @param argv the options
   */
  public static void main(String [] argv) {
    runClassifier(new AdaBoostR2(), argv);
  }
}
