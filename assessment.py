import metric as ms
import keyboard

# class to run an assessment on a keyboard layout, that is, to supply a keyboard
# layout a stream of text and track performance metrics
#   [self.layout] is the layout to be assessed
#   [self.result] is the list of all reports generated by the metrics/trackers
class Assessment():
    # initialze the assessment on a layout which is constructed from grid_spec
    # and key_placement
    def __init__(self, grid_spec, key_placement):
        self.layout = keyboard.Layout(grid_spec, key_placement)
        self.result = None

    # list of metrics to be run in the assessment
    metrics_classes = [
        ms.HandBalanceTracker,
        ms.HomeRowTracker,
        ms.KeyEaseTracker,
        ms.RepeatFingerTracker,
        ms.AlternationTracker,
    ]

    # run the assessment on layout, and have each metric be evaluated; will
    # update [self.result] with the list of reports generated by each metric
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

    # print a full report of the results from all metrics
    def full_report(self):
        if self.result is None:
            return

        displayable_result = list(map(lambda x: str(x), self.result))
        print("\n".join(displayable_result))

    # print a one-line list containing the results from all metrics 
    def one_line(self):
        result_vec = []
        for result in self.result:
            for key, value in result.data.items():
                result_vec.append(value)

        print(result_vec)

    # print a reduce-information one-line list containing key information 
    # about each of the metrics in the one_line() report
    def one_line_headings(self):
        headings = []
        for result in self.result:
            for key, value in result.data.items():
                headings.append(key)

        print(headings)
               