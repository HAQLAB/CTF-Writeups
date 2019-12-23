import Augmentor

for i in range(0, 6):
    p = Augmentor.Pipeline("old_templates/{}".format(i))
    p.random_distortion(probability=1, grid_width=4, grid_height=4, magnitude=4)
    p.sample(10)
