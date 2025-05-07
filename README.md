# Public Version of ATPPV2

## Laura Neville, Farzin Negabhani, Frieder Wizgall

Documentation
-------------

To locally build the documentation of this repository, follow the steps below:

1. Install the sphinx through pip

```
    pip install sphinxawesome-theme
```

2. clone the public repository branch

```
    git clone -b ATPPeX_dev git@github.com:laura-neville/sn_dti.git
```

3. change directory to doc

```
    cd doc
```

4. Build the sphinx document

```
    make html
```

If the documentation compiles successfully, an index.html file under doc/build/html folder appears. Then you can open, the index.html file with any browser. 

## To-Do List

### 🟢 Completed Tasks
- [x] Set up project repository
- [x] Create initial README file
- [x] Write the ToDo List

### 🟡 In Progress
- [ ] Set up the repository 
- [ ] Push the current status of the pipeline



### 🔴 Pending Tasks
- [ ] Add documentation
- [ ] Find a more elegant solution to set up the system_config.sh
- [ ] What about combine target masks in Module 3?
- [ ] Give Settings to the user to determine the Waypoint, Target and Termination masks
- [ ] What about the probabilistic parcellation part? -> Delete it?
- [ ] Rewrite Module 11 postprocress_mpm
- [ ] Rewrite Module 12 validation
- [ ] Rewrite Module 13 indices_plot
- [ ] Remove the modules after (14, 15)
- [ ] What about other post analysis (MPM?, Shapley?)
- [ ] Add some debugging tests and asserts to make sure the data is in the correct format before performing any Modules
- [ ] Come up with a new name for the pipeline
