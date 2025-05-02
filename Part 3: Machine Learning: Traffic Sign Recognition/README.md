Road Sign Identification Experiment
-----------------------------------

The goal for our experiment was to train the model to identify images and classify them according to the type of traffic signs the images portray.

We used a CNN(Convolutional Neural Network) for our experiment


--------
Accuracy 
--------

After testing the model achieved an Accuracy of 0.9876(98.8%), 0.0485(0.05%) for loss.
We trained the model under 10 epochs and it exponentially increased its accuracy during the first half of the epochs(5/10) During the last half it kept a steady and gradual increase in its accuracy.
Its loss score decreased rapidly in the first half of the epochs(5/10), it remained low after and slowly decreased for the remaining epochs.

--------------
Learning Curve
--------------

We displayed the results in a line chart to visualise its learning curve. For its accuracy we got an ascending arc with validation accuracy line above the training accuracy line. This indicated that the model wasnt onver fitting nor was it underfitting and for its loss we got a descending arc.

For our first model we actually experienced a case of overfitting as the Validation accuracy line was below the training accuracy line. The Reason was because Our Dropout value was at 0.3. We fixed this by increasing our Dropout to 0.5 which also helped it to generalize better.

We also found that using 10 epochs with 0.5 gave us the best balanced results.(balance between overfitting and underfitting)

----------------
Confusion Matrix
----------------
Based on Our confusion matrix, values were distributed from the top left of Y Axis to bottom right of the x axis diagonally. We go darker shades of blue on the TP(True Positive Region)
Which means that the model was correctly classifying the images. We got values on the TN(True Negative) with ligher shades of blue which means that less volume of true wrong predictions with little to none values in the false negatives and false positives. This indicates that the model was performing very well.

---------------
Hyperparameters
---------------

We used the following:
Epochs
Optimizer
Loss Function


--------------------------------------------
The architechure of our model is as follows:
--------------------------------------------
Model: Sequenial()

Layers:
Conv2d x2
MaxPooling2d x2
Dense Layers x2
Flatten Layer x1
Dropout x1

Total Parameters: 959939
Trainable params: 319979
Non-trainable params:0
Optimizer params:639960

--------------
What it means:

This model is a sequential convolutional neural network (CNN) designed for image classification, likely with 43 output classes (suggesting a dataset like traffic sign classification). Here’s a brief breakdown:
- Feature Extraction: Two convolutional layers (Conv2D), each followed by MaxPooling to reduce spatial dimensions while preserving important features.
- Flattening: Converts the pooled feature maps into a 1D array for dense layers.
- Fully Connected Layers: A dense layer (128 neurons)
- - processes extracted features, followed by a Dropout layer to prevent overfitting.
- Output Layer: The final dense layer with 43 neurons, using softmax activation, meaning it classifies images into one of 43 possible categories.
- Total Parameters: ~960K, with ~320K trainable, balancing complexity and efficiency.
This architecture is efficient for recognizing patterns in images, leveraging convolutions for feature extraction and dense layers for classification.
-------------------------------------------------------------------------------------------------------------------------------------------------------


