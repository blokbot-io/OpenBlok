# Neural networks in OpenBlok

OpenBlok utilizes two networks to perform the following tasks:

1. Identify the location of the object in the image.
2. Predict the objects feature sets.

## Location

Location input format is an image with height of 100 px, width of 150 px, and 3 channels.

Localization outputs two vectors:

1. The x, y coordinates for the center of the object of the side view.
2. The x, y coordinates for the center of the object of the top view.

## Feature prediction

Feature prediction input format is an image with height of 128 px, width of 256 px, and 3 channels.

Feature outpus two predictions"

1. The predicted class of the object.
2. The design of the object.
