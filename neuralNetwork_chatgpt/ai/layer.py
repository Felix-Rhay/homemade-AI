from . import neuron as n

class Layer:
    def __init__(self, input_size, neuron_count, lr=0.1):
        self.neurons = [
            n.Neuron(input_size, lr) for _ in range(neuron_count)
        ]

    def forward(self, inputs):
        self.inputs = inputs
        return [n.forward(inputs) for n in self.neurons]

    def backward(self, errors):
        propagated_error = [0.0] * len(self.inputs)

        for neuron, error in zip(self.neurons, errors):
            neuron_error = neuron.backward(error)
            for i in range(len(propagated_error)):
                propagated_error[i] += neuron_error[i]

        return propagated_error
    
    def backward_linear(self, errors):
        propagated_error = [0.0] * len(self.inputs)

        for neuron, error in zip(self.neurons, errors):
            neuron_error = neuron.backward_linear(error)
            for i in range(len(propagated_error)):
                propagated_error[i] += neuron_error[i]

        return propagated_error


    def to_dict(self):
       return {
           "neurons": [neuron.to_dict() for neuron in self.neurons]
       } 

    def from_dict(self, data):
        for neuron, neuron_data in zip(self.neurons, data["neurons"]):
            neuron.from_dict(neuron_data)