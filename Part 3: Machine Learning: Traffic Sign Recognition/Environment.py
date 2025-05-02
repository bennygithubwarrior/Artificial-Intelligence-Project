!pip install tensorflow opencv-python scikit-learn #Installing Dependencies

from google.colab import drive 
drive.mount('/content/drive')   #Mounting Drive

!unzip /content/drive/MyDrive/GTSRB-Training_fixed.zip -d gtsrb #unzipping the dataset
