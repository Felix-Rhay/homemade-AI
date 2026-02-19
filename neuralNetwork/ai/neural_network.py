import json
from . import layer as l

class Network:
    def __init__(self):
        self.layers:list[l.Layer] = []

    def add_layer(self, layer:l.Layer):
        self.layers.append(layer)

    def forward(self, inputs):
        for layer in self.layers:
            inputs = layer.forward(inputs)
        return inputs

    def backward(self, loss_gradient):
        for layer in reversed(self.layers):
            loss_gradient = layer.backward(loss_gradient)

    def backward_linear_output(self, loss_gradient):
        # 1️⃣ Dernière layer : linéaire
        loss_gradient = self.layers[-1].backward_linear(loss_gradient)

        # 2️⃣ Layers cachées : sigmoïde
        for layer in reversed(self.layers[:-1]):
            loss_gradient = layer.backward(loss_gradient)


    def save(self, filename="latest.json"):
        data = {
            "layers": [layer.to_dict() for layer in self.layers]
        }
        with open(filename, "w") as f:
            json.dump(data, f)

    def load(self, filename="latest.json"):
        with open(filename, "r") as f:
            data = json.load(f)
        for layer, layer_data in zip(self.layers, data["layers"]):
            layer.from_dict(layer_data)