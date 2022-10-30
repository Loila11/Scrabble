# Scrabble

Libraries required to run the project:
- numpy==1.21.0
- cv2=4.4.0

How to run and where to look for the output file:
- script: [main.py](./main.py)
- function: main(input_folder_name), where input_folder_name is the path to the folder containing the test images
- output: the output file consists of txt files in [results/...](./results/)

## Introduction

For solving this problem I separated the task in 3 subtasks: image preprocessing, pattern matching and score calculation.

I kept a folder with templates, containing all letters presents on the board and the empty tiles.

## Image Preprocessing

For performing different operation on the image we must first identify the board outline, then rotate and resize the image to match the letters kept as templates.

For identifying the lines I used HoughLinesP from openCV on an image that was previously transformed into grayscale, blurred and limited to the most important edges, with Canny transform.

This transformation gave a lot of outliers, which is why I consequently separated all lines in horizontal and vertical ones and kept only the lines that start and end within a certain threshold relative to the image center.

After filtering these lines and finding the board corners, I resized it in order to match the template size and repeated the aforementioned steps to re-obtain the corners.

## Pattern Matching

After obtaining the corners on the adjusted image, we can simply divide the difference between them on the Ox and on the Oy axis to 15, in order to find the placement of each square.

Between each game I initialize the game board with a matrix of 15 x 15 empty squares. For each turn I only search to see if the tiles that were previously empty have received a tile. For this, I use pattern matching between the square and the given templates. At each iteration I consider the template with the biggest match value to be the right choice. If that template is a letter, it means a new tile has been added to the board.

## Score calculation

After identifying the new tiles we must calculate the score and add them to the board. The score is calculated as described in the assignment. For the set of new tiles I check to see to which tiles they were appended, what new words they make on the side, and add each appropriate bonus. The positions, tiles and newly calculated score are added in the [results](./results/) folder, and the tiles are added to the board.

The code for this can be found in the file [score.py](./score.py).
