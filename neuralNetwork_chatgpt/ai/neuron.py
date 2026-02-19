import random
import math

class Neuron:
    def __init__(self, input_size, lr=0.1):
        self.weights = [random.uniform(-1,1) for _ in range(input_size)]
        self.bias = random.uniform(-1,1)
        self.lr = lr

    def sigmoid(self, z):
        return 1/(1+math.exp(-z))
    
    def forward(self, inputs):
        self.inputs = inputs
        self.z = sum(w * x for w, x in zip(self.weights, inputs)) + self.bias
        self.output = self.sigmoid(self.z)
        return self.output

    def backward(self, error):
        d_sigmoid = self.output * (1 - self.output)

        delta = error * d_sigmoid

        for i in range(len(self.weights)):
            self.weights[i] += self.lr * delta * self.inputs[i]

        self.bias += self.lr * delta

        return [delta * w for w in self.weights]

    def backward_linear(self, error):
        delta = error  # pas de dérivée d'activation

        propagated = []
        for i in range(len(self.weights)):
            propagated.append(self.weights[i] * delta)
            self.weights[i] += self.lr * delta * self.inputs[i]

        self.bias += self.lr * delta
        return propagated
    
    def to_dict(self):
        return {
            "weights": self.weights,
            "bias": self.bias
        } 

    def from_dict(self, data):
        self.weights = data["weights"]
        self.bias = data["bias"]