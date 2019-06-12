# plot Cemona_Plan

from utilities.plot_utilities import save_to_pdf
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D as PLine2D
from matplotlib import colors as mcolors
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages

# geplottet werden müssen: self.points, self.ex_forces, self.members, self.reactions

# member_limits and segment for plot
# Achsen Zeichnen und beschriften
# plot solved system


def get_limits_and_points_for_plot(points, offset_factor=0.25):
    x = []
    y = []

    p_id = []

    for point_id in points:
        x0 = points[point_id].coordinates[0]
        y0 = points[point_id].coordinates[1]

        x.append(x0)
        y.append(y0)

        p_id.append(point_id)

    x_lim = [min(x), max(x)]
    delta_x = x_lim[1] - x_lim[0]
    x_lim[0] -= offset_factor * delta_x
    x_lim[1] += offset_factor * delta_x

    y_lim = [min(y), max(y)]
    delta_y = y_lim[1] - y_lim[0]
    y_lim[0] -= offset_factor * delta_y
    y_lim[1] += offset_factor * delta_y

    return x_lim, y_lim, p_id, x, y


def plot_cremona_plan(Cremona_plan):
    x_lim, y_lim, p_id, x, y = get_limits_and_points_for_plot(
        Cremona_plan.points)

    fig, ax = plt.subplots()
    ax.set_title('Cremona Plan', size = 18)
    ax.set_xlim(x_lim)
    ax.set_ylim(y_lim)

    # plot points and point_id
    ax.scatter(x, y)

    for i in range(len(p_id)):
        ax.annotate("n_" + str(p_id[i]), (x[i], y[i]), size = 12)

    # plot external forces

    for f_id in Cremona_plan.ex_forces:
        x = Cremona_plan.ex_forces[f_id].x[0]
        y = Cremona_plan.ex_forces[f_id].y[0]
        delta_x = Cremona_plan.ex_forces[f_id].x[1] - x
        delta_y = Cremona_plan.ex_forces[f_id].y[1] - y
        ax.arrow(x, y, delta_x, delta_y,  color='green',
                 length_includes_head=True, head_width=10, head_length=10)
        s_x = Cremona_plan.ex_forces[f_id].midpoint[0]
        s_y = Cremona_plan.ex_forces[f_id].midpoint[1]
        ax.annotate(f_id, (s_x, s_y), size = 12)

    # plot reactions
    for f_id in Cremona_plan.reactions:
        delta_x = Cremona_plan.reactions[f_id].x
        delta_y = Cremona_plan.reactions[f_id].y
        ax.add_line(PLine2D(delta_x, delta_y,
                            alpha=1, color='b', linestyle='-'))
        s_x = Cremona_plan.reactions[f_id].midpoint[0]
        s_y = Cremona_plan.reactions[f_id].midpoint[1]
        ax.annotate(f_id, (s_x, s_y), size = 12)

    # plot members
    for f_id in Cremona_plan.members:
        delta_x = Cremona_plan.members[f_id].x
        delta_y = Cremona_plan.members[f_id].y
        ax.add_line(PLine2D(delta_x, delta_y,
                            alpha=1, color='b', linestyle='-'))
        s_x = Cremona_plan.members[f_id].midpoint[0] - 1
        s_y = Cremona_plan.members[f_id].midpoint[1] - 1
        ax.annotate(f_id, (s_x, s_y), size = 12)

    plt.rcParams.update({'font.size': 12})
