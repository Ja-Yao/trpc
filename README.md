# Trans-radial Prosthesis Controller (TRPC)

****

The Trans-radial Prosthesis Controller (TRPC) is a software package designed to provide control and functionality to
individuals with upper limb amputations at the trans-radial level. It enables users to regain dexterity and perform
a wide range of tasks using a prosthetic hand.

## Table of Contents
- [Software](#software)
- [Development](#development)
- [References](#references)

****

## Software
The TRPC package is built using the LibEMG library. LibEMG is a powerful library for processing and analyzing
electromyography (EMG) signals. It provides a wide range of functions and algorithms for real-time EMG signal
processing, feature extraction, and classification.

## Development
Clone this repository to your local machine using:
```bash
git clone https://github.com/Ja-Yao/tprc.git
```

Then, create a python virtual environment inside the root project folder. Python versions 3.6 and above ship with the 
`venv` module, which should be used as shown below. 

Note that this project **requires** Python 3.8 or above.
```bash
python -m venv venv
```

Install the trpc package as an editable package:
```bash
# Run this command if you haven't started the virtual environment
source venv/bin/activate

# Install the package
pip install -e .
```

## References
- [LibEMG documentation](https://libemg.github.io/libemg/index.html)