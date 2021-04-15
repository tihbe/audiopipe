# AudioPipe

Simple script to pipe the speakers from one computer to another using Window's stereo mix and PyAudio.

# Installation

Install the packages listed in environment.yml or create the environment with conda:
```bash
conda env create -f environment.yml
```

# Usage
Start the server on the computer where you want to hear the audio:

```bash
python audiopipe.py server
```

Start the client on the computer where you want to record the audio:
```bash
python audiopipe.py client --ip IP_OF_THE_SERVER
```

For more options, check `python main.py [command] --help`.
