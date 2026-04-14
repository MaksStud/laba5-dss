from scheduler.core.observer import Observer
from scheduler.implementation.election_network import ElectionNetwork

# NETWORK_CLASS should be set to the current implementation network class of the AbstractNetwork class
NETWORK_CLASS = ElectionNetwork

if __name__ == '__main__':
    # create the current object of the network implementation
    network = NETWORK_CLASS()
    observer = Observer(network)
    observer.run()
