from matplotlib import pyplot as plt

from get_log import get_log, get_logged_property_against_time, cross_plot


if __name__ == '__main__':
    log = get_log()
    t_x, x = get_logged_property_against_time(log, function_name_filter='set_x', property_extraction_function=lambda args, return_val : args)
    t_z, z = get_logged_property_against_time(log, function_name_filter='get_z', property_extraction_function=lambda args, return_val : sum(return_val))

    x2, z2 = cross_plot(t_x, x, t_z, z)

    fig, axs = plt.subplots(nrows=3)
    axs[0].plot(t_x, x)
    axs[1].plot(t_z, z)
    axs[2].scatter(x2, z2)
    plt.show()
    