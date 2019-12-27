# arp_tn_face_recognition

This project is a tool to recognize the faces of the deputies at the Tunisian Assembly of the Representatives of the People from photos and videos.

## Possible applications

* For parlimentary reporters and anyone who needs to identify the speaking deputies
* Measuring airtime per representative

## Tasks

* [ ] Create dataset
  * [ ] Get list of deputies
  * [ ] Use a `seed` image for each deputy that will be later used to clean scraped data
  * [ ] Automate download of photos
  * [ ] Generate face embeddings for each photo
  * [ ] Perhaps use a hierarchical data file format e.g. HDF5

* [ ] Implement a *Classifier* with tuning parameters that takes a photo / video frame and returns a list of identified people with a certainty metric

* [ ] Create a way to evaluate which subset of images used in training produces best results with respect to some testing dataset
  * [ ] Generate report per person in training dataset

* [ ] Integrate the *Classifier* with sci-kit learn tools for metrics and visualisation of results.

* [ ] Abstract the interface with YouTube, Facebook, and possibly other photos / videos inputs in a neat interface

## References

* <https://face-recognition.readthedocs.io/en/latest/index.html>
* <https://github.com/ageitgey/face_recognition/blob/master/examples/facerec_from_webcam_faster.py>
* <http://vis-www.cs.umass.edu/lfw/index.html#download>
* <https://www.bogotobogo.com/python/Multithread/python_multithreading_subclassing_creating_threads.php>