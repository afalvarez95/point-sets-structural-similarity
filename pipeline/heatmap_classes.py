import textwrap

#Heatmap axes labelled by class (Perlin family) instead of by point cloud name, with font sizes readable in a paper.

PAPER_FONTSIZE = {"title": 22, "label": 20, "ticks": 18, "colorbar": 20}

#Names of the measurements in the plots (titles, colorbars, axes)
MEASUREMENT_LABELS = {"mci": "MCI", "wasserstein": "Sliced Wasserstein", "avg_haussdorf_distance_value": "AHD",
                      "p95_haussdorf_distance_value": "HD95", "haussdorf_distance_value": "Hausdorff"}


def measurement_label(column):
    return MEASUREMENT_LABELS.get(column, column)


def class_of(name):
    #S4-1-A -> S4, C416-Coarse-2-D -> C416-Coarse
    return "-".join(name.split("-")[:-2])


def class_groups(names):
    '''
    :returns: (class, first index, last index) of each run of consecutive names of the same class.
    '''
    groups = []
    for i, name in enumerate(names):
        if groups and groups[-1][0] == class_of(name):
            groups[-1][2] = i
        else:
            groups.append([class_of(name), i, i])
    return groups


def set_class_ticks(ax, names, axis, rotation=45, fontsize=None):
    '''
    One tick label per class, centered on its block of point clouds, and a line between classes.
    :param axis: "x" or "y".
    :param rotation: angle of the x labels (0 for horizontal labels).
    :param fontsize: size of the labels, PAPER_FONTSIZE["ticks"] by default.
    '''
    fontsize = fontsize or PAPER_FONTSIZE["ticks"]
    groups = class_groups(names)
    centers = [(first + last) / 2 for _, first, last in groups]
    labels = [label for label, _, _ in groups]
    boundaries = [first - 0.5 for _, first, _ in groups[1:]]
    if axis == "x":
        ax.set_xticks(centers)
        if rotation:
            ax.set_xticklabels(labels, rotation=rotation, ha="right", rotation_mode="anchor", fontsize=fontsize)
        else:
            ax.set_xticklabels(labels, fontsize=fontsize)
        for b in boundaries:
            ax.axvline(b, color="black", linewidth=1.2)
    else:
        ax.set_yticks(centers)
        ax.set_yticklabels(labels, fontsize=fontsize)
        for b in boundaries:
            ax.axhline(b, color="black", linewidth=1.2)
    ax.tick_params(axis=axis, length=0)


def set_paper_title(ax, title, width=35):
    #Long titles are wrapped so they keep the paper font size
    ax.set_title(textwrap.fill(title, width=width), fontsize=PAPER_FONTSIZE["title"])


#Size of the heatmaps with one row per point cloud (perturbation, removal, rigid, perturbation + removal)
PAPER_FIGSIZE = (10, 10)


def style_class_heatmap(fig, ax, im, rows, cols, title, xlabel, colorbar_label):
    '''
    Paper style of a heatmap with one row per point cloud: one label per class on the rows,
    the values of the columns (epsilon, % of removal, ...) on the x axis, paper font sizes and the colorbar.
    '''
    set_class_ticks(ax, rows, "y")
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, fontsize=PAPER_FONTSIZE["ticks"])
    ax.set_xlabel(xlabel, fontsize=PAPER_FONTSIZE["label"])
    ax.set_ylabel("Perlin cloud class", fontsize=PAPER_FONTSIZE["label"])
    set_paper_title(ax, title)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(measurement_label(colorbar_label), fontsize=PAPER_FONTSIZE["colorbar"])
    cbar.ax.tick_params(labelsize=PAPER_FONTSIZE["ticks"])
    return cbar
