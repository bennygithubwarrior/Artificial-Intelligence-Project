
#assigning numbers to each folder aswell as resizing the images to 30,30 and seeing whether image was receive


import cv2
import os
import numpy as np
import matplotlib.pyplot as plt

data_dir = "/content/gtsrb/GTSRB/Training"
categories = [str(i).zfill(5) for i in range(43)]
X, y = [], []
samples_shown = 0

for category in categories:
    path = os.path.join(data_dir, category)
    if not os.path.exists(path):
        continue

    for img_name in os.listdir(path):
        if not img_name.endswith(".ppm"):
            continue

        img_path = os.path.join(path, img_name)
        img = cv2.imread(img_path)

        if img is None:
            print(f"Failed to load: {img_path}")
            continue


        resized_img = cv2.resize(img, (30, 30))


        if samples_shown < 3:
            plt.figure(figsize=(8,4))
            plt.subplot(1,2,1)
            plt.xticks([])
            plt.yticks([])
            plt.title("Original Image")
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

            plt.subplot(1,2,2)
            plt.xticks([])
            plt.yticks([])
            plt.title("Resized Image (30x30)")
            plt.imshow(cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB))

            plt.show()

            samples_shown += 1


        X.append(resized_img)
        y.append(int(category))

X = np.array(X) / 255.0
y = np.array(y)

print(f"Total images loaded: {len(X)}")
print(f"Total labels loaded: {len(y)}")

#----------------------------------Ends here----------------------------------



# splitting dataset into training and testing(80/20 split)
# plotting images to see whether dataset is being loaded with resized scale



import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

plt.figure(figsize=(10,10))
for i in range(25):
    plt.subplot(5,5,i+1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.imshow(X_train[i])
    plt.xlabel(f"Label: {y_train[i]}")

plt.show()
