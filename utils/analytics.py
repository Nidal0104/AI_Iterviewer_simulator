import matplotlib.pyplot as plt

def calculate_overall(scores):
    return sum(scores) / len(scores)


def plot_scores(metrics):
    labels = list(metrics.keys())
    values = list(metrics.values())

    fig, ax = plt.subplots()
    ax.plot(labels, values)
    ax.set_ylim(0, 10)
    ax.set_title("Performance Analytics")

    return fig
