# VoxelViz
Visualization tool for (f)MRI data-sets using Plotly Dash. Submitted to the [TransIP](https://www.transip.nl/) VPS competition.

## Intro
This tool was originally developed for the TransIP VPS competition ("come up with an original idea
for a virtual private server"), but mainly because I was looking for an excuse to mess around with
the new [Plotly Dash](https://plot.ly/dash) framework. The app turned out better than I expected and
I think I'll try to convert it into an open-source package for everyone to use. That is, I'll rewrite
it such that any neuroimaging researcher (or teacher! More about that later) with a proper dataset
can use `VoxelViz` to show/demonstrate it.

## Usage
As of now, `VoxelViz` can be used in two ways, which correspond to the two apps in this
repository (the one in the `usecase` folder and the one in the `teaching` folder).

### Showcase results
First, it can be used to interactively visualize results from (group-level) fMRI analyses. 
Or, in layman terms: show pretty brain pictures. In the `usecase` folder, the `app.py` file
runs an app that shows the results from my [fMRI study](https://academic.oup.com/scan/article/12/7/1025/3798709/Shared-states-using-MVPA-to-test-neural-overlap) (freely accessible!) about the representation
of emotion in the brain. `VoxelViz` visualizes the brain images corresponding to the different
analyses we did (left panel of the app), which can be interactively manipulated by, for example, adjusting the statistical
threshold, orientation (`X`, `Y`, `Z`), and the current "slice" (specific 2D view; changing this is 
like "scrolling" through the brain image).

Additionally, `VoxelViz` interactively visualizes the
"timeseries" from the voxel (3D cube, which represents the unit of measurement) that you hover over
in the brain image from the app's left panel. So, the right panel (timeseries plot) updates according
to where your cursor is in the app's right panel - cool huh? 

### Teaching neuroimaging
Next to the "showcase" use, I think this app could be quite helpful in a teaching context. 
It happens to be that I myself teach two "neuroimaging" (analysis of brain-data) courses at the
University of Amsterdam, and I struggly to explain "dry" (often statistical) concepts during my
lectures and computer labs. Of course, I try to make my lectures more "lively" by including a lot
of brain images, but 2D representations just don't do the trick. How cool would it be to show students
"boring" things, like the effect of a high-pass filter on fMRI analyses, interactively in a web-app?
Well, the folder `teaching` of this repository contains an app for *just* that! It shows the results
(brain images) from different preprocessing pipelines. This way, you can check out (or show students)
what happens to the brain images when you apply a high-pass filter (or not!) or when you (spatially)
smooth your data. This should be especially clear from the timeseries plot in the right panel!

## Features
I've alluded to some of the features in the previous section already, but here I'll describe them
in more detail.

### Show different datasets/results
When you start the app, you'll see a dropdown menu in the top left corner of the brain image plot.
In the `showcase` example app, this dropdown menu contains the "contrasts" (results) from different
analyses, which are referred to by keywords such as "action", "interoception", "action>interoception", etc.
(These results refer to analyes which tested how the brain activates in response to action-oriented emotional
states, interoception-oriented emotional states, and the difference between action and interoception states,
respectively.) Changing the "contrast" will update both the brain plot and the timeseries plot!

ToDo: update GIF
![alt text](https://github.com/lukassnoek/VoxelViz/raw/master/img/different_datasets.gif "Logo Title Text 1")

### Viewing/scrolling options
The brain is of course a 3D dimensional object that is, here, visualized in 2D. I've included two options
to configure which part (and in which orientation) you're viewing the brain image. Next to the "contrasts"
dropdown menu, you can choose whether you want to view the brain in a saggital orientation (from the side; "X"),
coronal orientation (from the front; "Y"), or axial orientation (from the top; "Z"). Next to the "X/Y/Z" option,
there is a slides that allows you "scroll" through the brain.

ToDo: update GIF
![alt text](https://github.com/lukassnoek/VoxelViz/raw/master/img/scrolling.gif "Logo Title Text 1")

### Adjust the (statistical) threshold
Usually, results from (f)MRI analyses are thresholded, to remove insignificant (de)activations. Therefore,
the results are by default thresholded at `abs(Z) > 2.3`. But sometimes its informative to check out the
unthresholded results, so `VoxelViz` contains a slides to adjust the threshold! Adjusting the threshold
automatically updates the brain plot (higher thresholds should show less red/blue and vice versa).

ToDo: update GIF
![alt text](https://github.com/lukassnoek/VoxelViz/raw/master/img/threshold.gif "Logo Title Text 1")

### Visualize underlying timeseries
In the right panel of the app, there is a "timeseries" plot that shows the underlying signal of
the highlighted [voxel](https://en.wikipedia.org/wiki/Voxel) (3D equivalent of pixel) in the brain plot.
In other words, if you hover over a voxel in the brain plot, the timeseries plot will automatically show
the underlying signal of that voxel. 

ToDo: make gif, explain model fit option!

## See for yourself!
`VoxelViz` will run as a standonly app on a VPS [X8 BladeVPS](https://www.transip.nl/vps/)
from TransIP, which will be accessible once I figured out how to make NGINX with SSL-encryption
work ... :grimacing:

Alternatively, you can clone this repository and run the app(s) locally! First, you'll need to
install the dependencies, which you can do through:

	$ pip install -r requirements.txt

Then, navigate to the directory (`usecase` or `teaching`) of the app you want to start, and
run:

	$ python app.py

This should start a browser with the app running on `http://localhost:8000`!

## ToDo
Couple of thing that I'd still like to implement (before the deadline of 8 August):

- Add a timeseries plot corresponding to the "hover" of the brain-plot [DONE]
- Fix styling (rows, columns) [DONE]
- Add modelfit option in timeseries plot
- Add some extra text (explanation)
