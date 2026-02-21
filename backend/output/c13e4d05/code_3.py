class Renderer:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.screen = None
        self.colors = {
            'background': (0, 0, 0),
            'snake': (0, 255, 0),
            'food': (255, 0, 0),
            'text': (255, 255, 255)
        }