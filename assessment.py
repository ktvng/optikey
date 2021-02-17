import metric as ms
import layout as keyboard

class Assessment():
    def __init__(self, grid_spec, key_placement):
        self.layout = keyboard.Layout(grid_spec, key_placement)
        self.result = None


    metrics_classes = [
        ms.HandBalanceTracker,
        ms.HomeRowTracker,
        ms.KeyEaseTracker,
        ms.RepeatFingerTracker,
        ms.AlternationTracker,
    ]

    def run_on(self, filename):
        metrics = list(map(lambda x: x(), Assessment.metrics_classes))
        for metric in metrics:
            metric.init(self.layout)

        with open(filename, 'r') as file:
            for line in file:
                for char in line:
                    for metric in metrics:
                        metric.evaluate(char)


        self.result = list(map(lambda x: x.report(), metrics))


    def full_report(self):
        if self.result is None:
            return

        displayable_result = list(map(lambda x: str(x), self.result))
        print("\n".join(displayable_result))

    
    def one_line(self):
        result_vec = []
        for result in self.result:
            for key, value in result.data.items():
                result_vec.append(value)

        print(result_vec)

    def one_line_headings(self):
        headings = []
        for result in self.result:
            for key, value in result.data.items():
                headings.append(key)

        print(headings)
               
