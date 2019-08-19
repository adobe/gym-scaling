# Scaling OpenAI Gym

This gym simulates a very basic cloud provider environment with a service that processes requests from a queue. 
The environment simulates the queue, instances with a certain processing capacity and latency for instance start up. 
The reward function gives feedback about how well the boundaries are maintained, how well the queue size is kept minimal 
and how well the cloud provider's resources are utilized related to the incoming load.

![](images/sin_input_result.gif)

This project is based on [OpenAI Gym](https://gym.openai.com/) and uses [OpenAI baselines](https://github.com/openai/baselines) to train models.

## Installation guide MacOS (docker)
Install [Docker for Mac](https://docs.docker.com/docker-for-mac/install/) and [XQuartz](https://www.xquartz.org/) on your system.
<p>
Build the docker image

```
make build
```
This will take a while as it compiles mesa drivers. It is recommended to give Docker a good part of the host's resources.
<p>
Allow all incoming connections to xquartz:

```
xhost +
```

### Usage

Run the sim with a trained model:
```
export SCALING_DISPLAY=hostip:0
make run
```

Replace _hostip_ by the external ip of your system to allow the docker instance to connect to your XQuartz server.

Run training with deepq ([train_deepq.py](train_deepq.py)):
```
export SCALING_DISPLAY=hostip:0
docker run -ti  gym-scaling:latest /bin/bash -c "python3 train_deepq.py"
```


## Run simulation and training with IDE
The script can be executed within an IDE like [PyCharm](https://www.jetbrains.com/pycharm/). 
Set up an [individual virtual env](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html) for this project and use it within the IDE.
Use Python 3.x. Install [baselines](https://github.com/openai/baselines) on the virtual env.

Train a model by e.g. calling [train_deepq.py](train_deepq.py) with right click -> Run...


## Support
This is a research project and anybody is welcome to experiment with their algorithms to achieve better results. 
We will support this project by interacting with the community and reviewing pull requests. 
But be aware that we do not commit on fixing issues or adding missing features.

## Contributing

Contributions are welcomed! Read the [Contributing Guide](./.github/CONTRIBUTING.md) for more information.

## Licensing

This project is licensed under the Apache V2 License. See [LICENSE](LICENSE) for more information.
