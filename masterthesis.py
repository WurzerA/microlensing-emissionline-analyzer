import numpy as np
import matplotlib

matplotlib.use("TkAgg")  # Positioned here to fix issue on macOS devices which caused the app to malfunction
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from os.path import basename
import lines_exact

# Define all globals
global print_only_once
global y_label
global number_of_spectrum
global lines_c4
global lines_c3
global lines_mg2
global lines_c4_core
global lines_c3_core
global lines_mg2_core
global p
global match
global microlen
global raw_data
global fit_list
global line_spectrum_list
global x_click_list
global count_fits
global spectrum_list_single
global which_wing
global subtracted
global button_status
global spectrum_list
global lin
global core_span


class Program:
    def __init__(self, master):

        # Variable for testing in order to print core values only once for each spectrum
        global print_only_once
        print_only_once = 0

        self.fig = plt.figure()
        self.master = master
        self.master.title("Microlensing calculations")
        self.master.protocol('WM_DELETE_WINDOW', self.close_program)
        self.master.geometry('950x650')

        self.frame = LabelFrame(master, text='')  # , bg = 'white'
        self.frame.grid(row=0, column=0, sticky=N)

        self.frame_zoomline = LabelFrame(master, text='')  # , bg = 'white'
        self.frame_zoomline.grid(row=1, column=0, sticky=N)

        self.frame_analysis = LabelFrame(master, text='Continuum Fit')  # , bg = 'white'
        self.frame_analysis.grid(row=2, column=0)

        self.frame_cores = LabelFrame(master, text='Core Alignment')  # , bg = 'white'
        self.frame_cores.grid(row=3, column=0)

        self.frame_microlensing = LabelFrame(master, text='Calculate Microlensing')  # , bg = 'white'
        self.frame_microlensing.grid(row=4, column=0)

        self.frame_save = LabelFrame(master, text='')  # , bg = 'white'
        self.frame_save.grid(row=7, column=0)

        self.frame_output = LabelFrame(master, text='Output ------- Blue wing --------------------------'
                                                    '----------------- Red wing')

        self.frame_output.grid(row=7, column=1)

        global y_label
        y_label = 'Intensity'
        global number_of_spectrum
        number_of_spectrum = 0
        global lines_c4
        global lines_c3
        global lines_mg2

        # Plot 2 core lines for each line
        # 1,2 entry: core, 3-6 : continuum
        lines_c4 = [1543, 1555, 1456, 1467, 1682, 1694]
        lines_c3 = [1902, 1915, 1807, 1818, 1989, 1999]
        lines_mg2 = [2792, 2804, 2660, 2678, 2905, 2921]

        global lines_c4_core
        global lines_c3_core
        global lines_mg2_core
        # This values are taken from lines_exact.py.
        lines_c4_core = 1549.1  # np.mean([lines_c4[0], lines_c4[1]])
        lines_c3_core = 1908.7  # np.mean([lines_c3[0], lines_c3[1]])
        lines_mg2_core = 2798.8  # np.mean([lines_mg2[0], lines_mg2[1]])

        self.data = GetData()
        global core_span
        core_span = 20

        # Plot without data
        global p
        p = Plot(self)
        p.plot(spectrum_list)
        global match
        match = MatchCores(self)
        global microlen
        microlen = Microlensing(self)
        global raw_data
        raw_data = list()
        global fit_list
        fit_list = list()
        global line_spectrum_list
        line_spectrum_list = list()
        global x_click_list
        x_click_list = list()
        global count_fits
        count_fits = list()

        # Data from specific line is saved seperately in spectrum_list_single
        # Make new list of spectra
        global spectrum_list_single
        spectrum_list_single = list()
        global which_wing
        which_wing = 'blue'
        global subtracted
        subtracted = False

        self.button_browse_file = Button(self.frame, text="Add Spectrum", command=self.enable_buttons_for_analysis)
        self.button_browse_file.grid(row=0, column=0, padx=3, pady=3)
        self.button_browse_file.config(width=13)

        # Clear plot button
        self.button_clear_plot = Button(self.frame, text='Clear Plot', state=DISABLED)
        self.button_clear_plot.grid(row=0, column=1, padx=3, pady=3)
        self.button_clear_plot.config(width=13)

        # Radiobuttons for Zoom in Lines
        self.var = IntVar()
        self.var.set(4)
        self.r1 = Radiobutton(self.frame_zoomline, text='CIV \u03bb1549.1', variable=self.var, value=1,
                              command=self.radiobutton_c4)
        self.r1.config(state=DISABLED)
        self.r1.grid(row=0, column=0, padx=3, pady=3)
        self.r2 = Radiobutton(self.frame_zoomline, text='CIII] \u03bb1908.7', variable=self.var, value=2,
                              command=self.radiobutton_c3)
        self.r2.config(state=DISABLED)
        self.r2.grid(row=1, column=0, padx=3, pady=3)
        self.r3 = Radiobutton(self.frame_zoomline, text='MgII \u03bb2798.8', variable=self.var, value=3,
                              command=self.radiobutton_mg2)
        self.r3.config(state=DISABLED)
        self.r3.grid(row=2, column=0, padx=3, pady=3)
        self.r4 = Radiobutton(self.frame_zoomline, text='all', variable=self.var, value=4, command=self.radiobutton_all)
        self.r4.grid(row=3, column=0, padx=3, pady=3)

        # Button to get coordinates from plot:
        self.button_get_coord = Button(self.frame_zoomline, text='Get Coordinates', state=DISABLED)
        self.button_get_coord.grid(row=0, column=1, sticky=W, padx=3, pady=3)
        self.button_get_coord.config(width=15)

        # Button to make linear fit
        self.button_linfit = Button(self.frame_zoomline, text='Linear Fit', state=DISABLED)
        self.button_linfit.grid(row=1, column=1, sticky=W, padx=3, pady=3)
        self.button_linfit.config(width=15)

        # Button to delete linear fits
        self.button_delfit = Button(self.frame_zoomline, text='Delete Fit(s)', state=DISABLED)
        self.button_delfit.grid(row=2, column=1, sticky=W, padx=3, pady=3)
        self.button_delfit.config(width=15)

        # Button to subtract fit from spectrum
        self.button_subtract_fit = Button(self.frame_zoomline, text='Subtract Fit', state=DISABLED)
        self.button_subtract_fit.grid(row=3, column=1, sticky=W, padx=3, pady=3)
        self.button_subtract_fit.config(width=15)

        # Radiobuttons for shift spectra
        self.varshift = IntVar()
        self.varshift.set(1)
        self.shift1 = Radiobutton(self.frame_cores, text='Spectrum 1', variable=self.varshift, value=1,
                                  command=self.radiobutton_shift1)
        self.shift1.grid(row=0, column=0)
        self.shift1.config(state=DISABLED)
        self.shift2 = Radiobutton(self.frame_cores, text='Spectrum 2', variable=self.varshift, value=2,
                                  command=self.radiobutton_shift2)
        self.shift2.grid(row=1, column=0)
        self.shift2.config(state=DISABLED)

        # Button to shift core (+)
        self.button_shift_core_plus = Button(self.frame_cores,
                                             text='Shift +1 \u212B',
                                             state=DISABLED,
                                             command=match.shift_spectrum_right)
        self.button_shift_core_plus.grid(row=0, column=1, sticky=W, padx=3, pady=3)
        self.button_shift_core_plus.config(width=10, state=DISABLED)

        # Button to shift core (-)
        self.button_shift_core_minus = Button(self.frame_cores,
                                              text='Shift -1 \u212B',
                                              state=DISABLED,
                                              command=match.shift_spectrum_left)
        self.button_shift_core_minus.grid(row=1, column=1, sticky=W, padx=3, pady=3)
        self.button_shift_core_minus.config(width=10, state=DISABLED)

        self.button_match_cores = Button(self.frame_cores, text='Match cores', state=DISABLED,
                                         command=match.match_cores)
        self.button_match_cores.grid(row=3, column=1, sticky=W, padx=3, pady=3)
        self.button_match_cores.config(width=15)

        self.entry_core_span = Entry(self.frame_cores)
        self.entry_core_span.grid(row=3, column=0)
        self.entry_core_span.config(width=2, state=DISABLED)
        self.entry_core_span.insert(0, '7')

        # Button to save plot
        self.button_save = Button(self.frame_save, text='Save as txt file', state=DISABLED,
                                  command=self.data.save_as_txt)
        self.button_save.grid(row=0, column=0, sticky=W, padx=3, pady=3)
        self.button_save.config(width=15)

        # Radiobuttons for microlensing red and blue wing span
        self.varmicro = IntVar()
        self.varmicro.set(1)
        self.micro_bluewing = Radiobutton(self.frame_microlensing, text='Blue wing', variable=self.varmicro, value=1,
                                          command=self.radiobutton_micro_bluewing)
        self.micro_bluewing.grid(row=0, column=0)
        self.micro_bluewing.config(state=DISABLED)
        self.micro_redwing = Radiobutton(self.frame_microlensing, text='Red wing', variable=self.varmicro, value=2,
                                         command=self.radiobutton_micro_redwing)
        self.micro_redwing.grid(row=0, column=1)
        self.micro_redwing.config(state=DISABLED)

        # Button for microlensing buffer and interval
        self.label_buffer = Label(self.frame_microlensing, text='Buffer')
        self.label_buffer.grid(row=2, column=0)

        self.entry_buffer = Entry(self.frame_microlensing)
        self.entry_buffer.grid(row=2, column=1)
        self.entry_buffer.config(width=3, state=DISABLED)
        self.entry_buffer.insert(0, '7')

        self.label_interval = Label(self.frame_microlensing, text='Interval')
        self.label_interval.grid(row=3, column=0)

        self.entry_interval = Entry(self.frame_microlensing)
        self.entry_interval.grid(row=3, column=1)
        self.entry_interval.config(width=3, state=DISABLED)
        self.entry_interval.insert(0, '30')

        # Button microlensing calculation
        self.button_microlensing = Button(self.frame_microlensing, text='Compute', state=DISABLED,
                                          command=microlen.get_wings_values)
        self.button_microlensing.grid(row=4, column=0, sticky=W, padx=3, pady=3)
        self.button_microlensing.config(width=15)

        # Output fiels for wings
        self.text_output_blue = Text(self.frame_output, height=6, width=40)
        self.text_output_blue.grid(row=0, column=0)
        self.text_output_blue.insert(END, '')
        self.text_output_blue.config(state=DISABLED)

        self.text_output_red = Text(self.frame_output, height=6, width=40)
        self.text_output_red.grid(row=0, column=1)
        self.text_output_red.insert(END, '')
        self.text_output_red.config(state=DISABLED)

        # Initial status: all emission lines visible
        global button_status
        button_status = 'all'

    def radiobutton_c4(self):
        linename = 'CIV'
        global button_status
        button_status = linename
        p.x_range(lines_c4, linename)
        self.r4.config(state=NORMAL)
        self.button_get_coord.config(state=NORMAL, command=p.enable_clicking)
        global print_only_once
        print_only_once = 0

    def radiobutton_c3(self):
        linename = 'CIII]'
        global button_status
        button_status = linename
        p.x_range(lines_c3, linename)
        self.r4.config(state=NORMAL)
        self.button_get_coord.config(state=NORMAL, command=p.enable_clicking)
        global print_only_once
        print_only_once = 0

    def radiobutton_mg2(self):
        linename = 'MgII'
        global button_status
        button_status = linename
        p.x_range(lines_mg2, linename)
        self.r4.config(state=NORMAL)
        self.button_get_coord.config(state=NORMAL, command=p.enable_clicking)
        global print_only_once
        print_only_once = 0

    def radiobutton_all(self):
        global button_status
        button_status = 'all'
        p.fig.clear()
        p.fig.canvas.draw()
        p.plot(raw_data)
        p.vertical_lines(raw_data, lines_c4)
        p.vertical_lines(raw_data, lines_c3)
        p.vertical_lines(raw_data, lines_mg2)
        self.button_get_coord.config(state=DISABLED)
        if len(spectrum_list) > 0:
            p.second_axis_for_lines(min(spectrum_list[0].x), max(spectrum_list[0].x))
        global print_only_once
        print_only_once = 0

    @staticmethod
    def radiobutton_shift1():
        global number_of_spectrum
        number_of_spectrum = 0

    @staticmethod
    def radiobutton_shift2():
        global number_of_spectrum
        number_of_spectrum = 1

    @staticmethod
    def radiobutton_micro_bluewing():
        global which_wing
        which_wing = 'blue'

    @staticmethod
    def radiobutton_micro_redwing():
        global which_wing
        which_wing = 'red'

    @staticmethod
    def radiobutton_micro_bothwings():
        global which_wing
        which_wing = 'both'

    def enable_buttons_for_analysis(self):
        self.data.browse_file_callback()
        if len(spectrum_list) > 0:

            if button_status == 'CIII]':
                p.x_range(lines_c3, 'CIII')
            if button_status == 'CIV':
                p.x_range(lines_c4, 'CIV')
            if button_status == 'MgII':
                p.x_range(lines_mg2, 'MgII')
            if button_status == 'all':
                p.vertical_lines(raw_data, lines_c4)
                p.vertical_lines(raw_data, lines_c3)
                p.vertical_lines(raw_data, lines_mg2)
                if len(spectrum_list) > 0:
                    p.second_axis_for_lines(min(spectrum_list[0].x), max(spectrum_list[0].x))

            self.button_clear_plot.config(state=NORMAL, command=p.clear_plot)
            self.r1.config(state=NORMAL)
            self.r2.config(state=NORMAL)
            self.r3.config(state=NORMAL)

    def close_program(self):
        self.master.quit()

    def disable_buttons(self):
        self.button_get_coord.config(state=DISABLED)
        self.button_linfit.config(state=DISABLED)
        self.button_subtract_fit.config(state=DISABLED)
        self.button_delfit.config(state=DISABLED)

        self.var.set(4)
        self.r1.config(state=DISABLED)
        self.r2.config(state=DISABLED)
        self.r3.config(state=DISABLED)

        self.button_match_cores.config(state=DISABLED)
        self.entry_core_span.delete(0, END)
        self.entry_core_span.config(state=DISABLED)
        self.button_shift_core_minus.config(state=DISABLED)
        self.button_shift_core_plus.config(state=DISABLED)
        self.varshift.set(1)
        self.shift1.config(state=DISABLED)
        self.shift2.config(state=DISABLED)

        self.varmicro.set(1)
        self.micro_redwing.config(state=DISABLED)
        self.micro_bluewing.config(state=DISABLED)
        self.entry_buffer.delete(0, END)
        self.entry_buffer.config(state=DISABLED)
        self.entry_interval.delete(0, END)
        self.entry_interval.config(state=DISABLED)
        self.button_microlensing.config(state=DISABLED)

        self.text_output_blue.delete(1.0, END)
        self.text_output_red.delete(1.0, END)
        self.text_output_blue.config(state=DISABLED)
        self.text_output_red.config(state=DISABLED)


# Handles data: Reads data from file and save it in spectrum_list
class GetData:
    def __init__(self):
        global spectrum_list
        spectrum_list = list()

    def browse_file_callback(self):
        file_content, basename_file = self.read_file()
        x = file_content[:, 0]
        y = file_content[:, 1]
        spectrum_list.append(Spectrum(x, y, basename_file))
        p.plot(spectrum_list)

        # Save raw spectrum list data for calculation if several fits are necessary
        raw_data.append(Spectrum(x, y, basename_file))

    @staticmethod
    def read_file():
        filename = filedialog.askopenfilename()
        file_content = []
        basename_file = basename(filename)

        # Read text file
        with open(filename) as f:
            for line in f:
                numbers_str = line.split()  # numbers as str
                try:
                    numbers_float = [float(x) for x in numbers_str]
                    file_content.append(numbers_float)
                except ValueError:
                    print('not a number')

        return np.array(file_content), basename_file

    # Save as txt file
    @staticmethod
    def save_as_txt():
        f = filedialog.asksaveasfile(mode='w', defaultextension=".txt", filetypes=(("text file", "*.txt"),
                                                                                   ("all files", "*.*")), title='test')
        if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
            return
        for item in zip(spectrum_list[0].x, spectrum_list[0].y, spectrum_list[1].x, spectrum_list[1].y):
            f.write("%s %s %s %s \n" % (item[0], item[1], item[2], item[3]))  # "%i %5.2f\n"

        f.close()

    # Alternative: Save as CSV file
    @staticmethod
    def save_as_csv():
        f = filedialog.asksaveasfile(mode='w', defaultextension=".csv", filetypes=(("CSV file", "*.csv"),
                                                                                   ("all files", "*.*")),
                                     title='test')
        if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
            return
        f.write("x_1[A];y_1;x_2[A];y_2\n")
        for item in zip(spectrum_list[0].x, spectrum_list[0].y, spectrum_list[1].x, spectrum_list[1].y):
            f.write("%s;%s;%s;%s\n" % (item[0], item[1], item[2], item[3]))  # "%i %5.2f\n"

        f.close()


# Handles the plot
class Plot:
    def __init__(self, program):
        self.program = program
        self.master = program.master
        self.canvas = None
        self.fig = None
        self.m = MouseLocation(self.master, self.program)
        self.ax = None
        self.ax1 = None

    def plot(self, spectra):
        self.close_plot()
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        for s in spectra:
            if not s.is_linear_fit:
                self.ax.plot(s.x, s.y, label=s.basename)
            else:
                self.ax.plot(s.x, s.y)

        plt.subplots_adjust(left=0.1, right=0.95, top=0.8, bottom=0.1)

        canvas_frame = Frame(self.master)
        canvas_frame.grid(row=0, column=1, sticky=N + S + E + W, rowspan=6)
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
        Grid.columnconfigure(self.master, 1, weight=1)
        Grid.rowconfigure(self.master, 0, weight=1)

        toolbar_frame = Frame(self.master)
        toolbar_frame.grid(row=6, column=1)
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()

        self.ax.set_ylabel(y_label)
        self.ax.set_xlabel('Wavelength [$\AA$]')

        self.ax.legend(bbox_to_anchor=(0, 1.19), loc=3, ncol=2, borderaxespad=0)

        plt.minorticks_on()

    # Second x-axis at the top of the plot for emission line labels
    def second_axis_for_lines(self, xmin, xmax):

        if len(spectrum_list) > 0:
            self.ax1 = self.ax.twiny()
            colors = ['0.4', '0.4', '0.4', '0.4', '0.4', '0.4', 'k', '0.4', '0.4', '0.4', '0.4', '0.4', '0.4', '0.4',
                      '0.4', 'k', '0.4', '0.4', '0.4', '0.4', '0.4', '0.4', '0.4', '0.4', '0.4', 'k', '0.4']
            xlabs = ('Ly $\\alpha$', 'N V', 'Si II', 'O I/Si II', 'C II', 'Si IV/OIV]', 'C IV', 'He II', 'O III]/Al II',
                     'N IV/Al II', 'N III]', 'Fe II', 'Ne III/Si II', 'Al III', 'Si III', 'C III]', 'Fe III',
                     'Fe III', 'Fe II', 'FeII', 'Fe II/C II]', 'Fe II', 'O II', 'Fe II', 'Al II/O III', 'Mg II', 'FeII',
                     'O III')

            self.ax1.set_xticks([1215.7, 1240.7, 1262.6, 1305, 1335.3, 1398, 1549.1, 1640.4,
                                 1668, 1720, 1750.3,
                                 1788.7, 1816,
                                 1857.4,
                                 1892.0, 1908.7, 1991.8, 2076.6, 2175.6, 2222.3, 2325, 2423.8,
                                 2471.0, 2626.9, 2671,
                                 2798.8,
                                 2964.3, 3133.7])

            self.ax1.set_xticklabels(xlabs, fontsize=8, rotation=90)
            for xtick, color in zip(self.ax1.get_xticklabels(), colors):
                xtick.set_color(color)
            self.ax.set_xlim(xmin, xmax)
            self.ax1.set_xlim(xmin, xmax)

    # Convert intensity to magnitude values
    def intensity_to_magnitude_y_axis(self):
        for i in range(len(spectrum_list[0].y)):
            spectrum_list[0].y[i] = -2.5 * np.log10(spectrum_list[0].y[i])
        for i in range(len(spectrum_list[1].y)):
            spectrum_list[1].y[i] = -2.5 * np.log10(spectrum_list[1].y[i])

        global y_label
        y_label = 'Magnitude'
        self.plot_anywhere()

    def enable_clicking(self):
        self.canvas.mpl_connect('button_press_event', self.m.clicked)

    # Plot vertical lines for most important lines
    @staticmethod
    def vertical_lines(spectra, xvalues):
        if spectra[0].x[0] < xvalues[0]:
            if spectrum_list[0].x[-1] > xvalues[1]:
                xvalues = xvalues[2:6]

                global button_status
                if button_status != 'all':
                    for i in range(0, len(xvalues)):
                        plt.axvline(x=xvalues[i], color='k', linestyle='dotted')
                lines_exact.all_lines()

    @staticmethod
    def line_span(xmin, xmax, spancolor):
        plt.axvspan(xmin, xmax, alpha=0.25, color=spancolor)

    def clear_plot(self):
        global button_status
        button_status = 'all'
        global subtracted
        subtracted = False
        global print_only_once
        print_only_once = 0
        spectrum_list.clear()
        self.close_plot()

        if fit_list:
            fit_list.clear()
        if line_spectrum_list:
            line_spectrum_list.clear()
        if raw_data:
            raw_data.clear()
        if x_click_list:
            x_click_list.clear()
        if count_fits:
            count_fits.clear()

        self.program.button_microlensing.config(state=DISABLED)
        self.program.disable_buttons()

        self.program.varmicro.set(1)
        global which_wing
        which_wing = 'blue'
        microlen.reset_values()

        self.plot(spectrum_list)

    def close_plot(self):
        if self.fig is not None:
            plt.close(self.fig)
            plt.clf()
            self.fig = None

    # Handles the zoom in function for the lines. A specific x range is taken.
    def x_range(self, lines, linename):
        self.close_plot()
        self.plot([])

        # Define range for plotting.
        min_x = min(lines) - 100
        max_x = max(lines) + 100

        # Define range after subtracting fits
        if subtracted:
            min_x = min(lines)
            max_x = max(lines)

        # Make a list of y extrema and take the average value.
        maxima = list()
        minima = list()

        if spectrum_list_single:
            spectrum_list_single.clear()

        # If the spectrum is not a fit, add a label name in order to show it in the legend.
        if len(spectrum_list) == 1:
            if not spectrum_list[0].is_linear_fit:
                s_new = Spectrum([], [], spectrum_list[0].basename + ' / ' + linename)
            else:
                s_new = Spectrum([], [], '')
            spectrum_list_single.append(s_new)

            # Add x and y values to new spectra list
            for i in range(1, len(spectrum_list[0].x)):
                if min_x < spectrum_list[0].x[i] < max_x:
                    spectrum_list_single[0].x.append(spectrum_list[0].x[i])
                    spectrum_list_single[0].y.append(spectrum_list[0].y[i])

            maxima.append(max(spectrum_list_single[0].y))
            minima.append(min(spectrum_list_single[0].y))

        # If there are more than one spectra (line fit is also a spectrum):
        # Make new list of spectra
        if len(spectrum_list) > 1:
            for i in range(0, len(spectrum_list)):
                if not spectrum_list[i].is_linear_fit:
                    s_new = Spectrum([], [], spectrum_list[i].basename + ' / ' + linename)
                else:
                    s_new = Spectrum([], [], '')
                spectrum_list_single.append(s_new)

            # Add x and y values to new spectra list
            for n in range(0, len(spectrum_list)):
                for i in range(1, len(spectrum_list[n].x)):
                    if min_x < spectrum_list[n].x[i] < max_x:
                        spectrum_list_single[n].x.append(spectrum_list[n].x[i])
                        spectrum_list_single[n].y.append(spectrum_list[n].y[i])

            # Calculate maxima only for spectra, not for linear fits
            for i in range(0, len(spectrum_list_single)):
                if not spectrum_list_single[i].is_linear_fit:
                    maxima.append(max(spectrum_list_single[i].y))
                    minima.append(min(spectrum_list_single[i].y))

        max_y_val = max(maxima)
        min_y_val = min(minima)

        delta_min_max_y = max_y_val - min_y_val
        min_y = min_y_val - delta_min_max_y / 10
        max_y = max_y_val + delta_min_max_y / 10

        for s in spectrum_list_single:
            if not s.is_linear_fit:
                self.ax.plot(s.x, s.y, label=s.basename)
            else:
                self.ax.plot(s.x, s.y)
        self.ax.set_xlim(min_x, max_x)
        self.ax.set_ylim(min_y, max_y)

        self.ax.legend(bbox_to_anchor=(0, 1.19), loc=3, ncol=2, borderaxespad=0)

        p.vertical_lines(spectrum_list_single, lines)

        # Draw horizontal line at y = 0 (continuum)
        # Is just visible if plot is in right range (just for subtracted plot)
        self.ax.axhline(y=0, color='black')
        self.second_axis_for_lines(min_x, max_x)

        ########################################################################################################
        # Calculate and print mean cores
        ########################################################################################################
        for i in range(0, 2):
            y_max_index = np.where(
                spectrum_list_single[i].y == np.max(spectrum_list_single[i].y))  # find index where y maximal
            y_max_index = y_max_index[0][0]
            x_max_core1 = spectrum_list_single[i].x[y_max_index]
            x_upper = x_max_core1 + 3
            x_lower = x_max_core1 - 3
            x_range_indices = np.where((spectrum_list_single[i].x > x_lower) & (spectrum_list_single[i].x < x_upper))
            x_range_indices = x_range_indices[0][0]
            y_range = spectrum_list_single[i].y[x_range_indices]

            # Print only once the core values, one time for each spectrum, therefore 2 times at all
            global print_only_once
            if print_only_once < 2:
                print('--------------------------------------')
                print('Core values')
                print('--------------------------------------')
                print('Mean core ', i, ': ', np.round(np.mean(y_range), 2))
                print('Std core ', i, ': ', np.round(np.std(y_range), 2))
                print('--------------------------------------')
                print_only_once = print_only_once + 1

    def plot_anywhere(self):  # Plotting in any class of this program
        self.close_plot()
        self.plot(spectrum_list)
        self.fig.canvas.draw()

        if button_status == 'CIII]':
            self.x_range(lines_c3, 'CIII]')
        if button_status == 'CIV':
            self.x_range(lines_c4, 'CIV')
        if button_status == 'MgII':
            self.x_range(lines_mg2, 'MgII')


# Handles the location of the mouse in order to get the coordinates for the linear fits.
class MouseLocation:
    def __init__(self, master, program):
        self.program = program
        self.master = master
        self.mousePosition = StringVar()
        self.x_coord = list()
        self.y_coord = list()

    def clicked(self, event):
        if event.inaxes:
            if len(self.x_coord) > 3:
                self.x_coord.clear()
                self.y_coord.clear()

            self.x_coord.append(event.xdata)
            self.y_coord.append(event.ydata)

            if len(self.x_coord) > 3:
                global lin
                lin = LinearFit(self.program, self.x_coord, self.y_coord)
                self.program.button_linfit.config(state=NORMAL, command=lin.make_linfit)


# Handles the linear fits.
# y coordinates not used in this type of fitting.
class LinearFit:
    def __init__(self, program, x_fit, y_fit):
        self.program = program
        self.x_fit = x_fit
        self.y_fit = []

    def make_linfit(self):
        y_values_blue = []
        y_values_red = []
        x_values_blue = []
        x_values_red = []

        count_fits.append(0)

        u = len(count_fits) - 1
        for i in range(0, len(raw_data[u].x)):
            if self.x_fit[0] < raw_data[u].x[i] < self.x_fit[1]:
                y_values_blue.append(raw_data[u].y[i])
                x_values_blue.append(raw_data[u].x[i])

        for i in range(0, len(raw_data[u].x)):
            if self.x_fit[2] < raw_data[u].x[i] < self.x_fit[3]:
                y_values_red.append(raw_data[u].y[i])
                x_values_red.append(raw_data[u].x[i])

        # x value for fit is at blue wing the left one and at red wing the right one so that the whole continuum is
        # taken. x_fit is now overwritten
        # y value is the mean of the clicked range
        self.x_fit = [self.x_fit[0], self.x_fit[3]]
        self.y_fit = [np.mean(y_values_blue), np.mean(y_values_red)]

        #########################################################################################################
        # Magnitude difference in the continuum at red and blue side: mean continuum values
        #########################################################################################################
        print()
        print('--------------------------------------')

        y_fit_blue = np.mean(y_values_blue)
        y_fit_red = np.mean(y_values_red)

        print('Continuum values: ')
        print('--------------------------------------')
        print('Mean continuum blue: ', np.round(y_fit_blue, 2))
        print('Mean continuum std: ', np.round(np.std(y_values_blue), 2))
        print()
        print('Mean continuum red: ', np.round(y_fit_red, 2))
        print('Mean continuum std: ', np.round(np.std(y_values_red), 2))
        print('--------------------------------------')
        print()
        #########################################################################################################

        # Just as many fits possible as spectra available
        if len(count_fits) <= len(raw_data):
            x_click_list.append(self.x_fit)

        else:
            x_click_list.clear()
            self.delete_fit()
            x_click_list.append(self.x_fit)
            count_fits.clear()
            count_fits.append(0)

        # Check if values are increasing for interpol
        if np.all(np.diff(self.x_fit) > 0) == FALSE:
            self.x_fit = self.x_fit[::-1]
            self.y_fit = self.y_fit[::-1]

        coeff = np.polyfit(self.x_fit, self.y_fit, 1)
        ffit = np.poly1d(coeff)

        # Make Interpolation for linear fit in order to be able to subtract these values from spectrum_list
        # Count x values for Interpolation
        x_count = 0

        line_spectrum_list.append(Spectrum([], [], raw_data[len(count_fits) - 1].basename))

        # Save values in new list for later subtraction
        # u = len(count_fits) - 1
        for i in range(0, len(raw_data[u].x)):
            if min(x_click_list[u]) < raw_data[u].x[i] < max(x_click_list[u]):
                x_count = x_count + 1
                line_spectrum_list[u].x.append(raw_data[u].x[i])
                line_spectrum_list[u].y.append(raw_data[u].y[i])

        step_interp = (max(self.x_fit) - min(self.x_fit)) / x_count
        xinterp = np.arange(min(self.x_fit), max(self.x_fit), step_interp)
        yinterp = np.interp(xinterp, self.x_fit, ffit(self.x_fit))
        spectrum_list.append(Spectrum(xinterp, yinterp, 'Continuum Fit', True))
        fit_list.append(Spectrum(xinterp, yinterp, 'Fit'))

        self.program.r4.config(state=DISABLED)

        p.plot_anywhere()

        if button_status == 'CIII]':
            self.program.r1.config(state=DISABLED)
            self.program.r3.config(state=DISABLED)
        if button_status == 'CIV':
            self.program.r2.config(state=DISABLED)
            self.program.r3.config(state=DISABLED)
        if button_status == 'MgII':
            self.program.r1.config(state=DISABLED)
            self.program.r2.config(state=DISABLED)

        self.program.button_delfit.config(state=NORMAL, command=lin.delete_fit)
        self.program.button_subtract_fit.config(state=NORMAL, command=lin.subtract_fit)
        self.program.button_linfit.config(state=DISABLED)

    def delete_fit(self):
        global subtracted
        subtracted = False

        self.program.button_linfit.config(state=DISABLED)
        self.program.button_subtract_fit.config(state=DISABLED)
        self.program.button_delfit.config(state=DISABLED)
        self.program.r1.config(state=NORMAL)
        self.program.r2.config(state=NORMAL)
        self.program.r3.config(state=NORMAL)
        self.program.r4.config(state=NORMAL)

        spectrum_list.clear()

        if fit_list:
            fit_list.clear()
        if spectrum_list_single:
            spectrum_list_single.clear()
        if line_spectrum_list:
            line_spectrum_list.clear()
        if x_click_list:
            x_click_list.clear()

        if len(raw_data) == 1:
            spectrum_list.append(raw_data[0])
        else:
            for n in range(0, len(raw_data)):
                spectrum_list.append(raw_data[n])
        if count_fits:
            count_fits.clear()

        p.plot_anywhere()

        self.program.button_match_cores.config(state=DISABLED)
        self.program.entry_core_span.config(state=DISABLED)
        self.program.entry_buffer.config(state=DISABLED)
        self.program.button_microlensing.config(state=DISABLED)
        self.program.entry_interval.config(state=DISABLED)
        self.program.shift1.config(state=DISABLED)
        self.program.shift2.config(state=DISABLED)
        self.program.micro_bluewing.config(state=DISABLED)
        self.program.micro_redwing.config(state=DISABLED)
        self.program.button_shift_core_minus.config(state=DISABLED)
        self.program.button_shift_core_plus.config(state=DISABLED)
        self.program.text_output_blue.delete(1.0, END)
        self.program.text_output_red.delete(1.0, END)
        self.program.text_output_blue.config(state=DISABLED)
        self.program.text_output_red.config(state=DISABLED)

    def subtract_fit(self):
        # Important for plotting range (x-range)
        global subtracted
        subtracted = True

        self.program.button_linfit.config(state=DISABLED)
        self.program.button_subtract_fit.config(state=DISABLED)
        subtract_list = list()
        spectrum_list.clear()

        if len(fit_list) == 1:
            subtract_list.append(Spectrum([], [], raw_data[0].basename))
            for i in range(0, len(line_spectrum_list[0].x)):
                subtract_list[0].x.append(line_spectrum_list[0].x[i])
                subtract_list[0].y.append(line_spectrum_list[0].y[i] - fit_list[0].y[i])
            spectrum_list.append(subtract_list[0])
        else:
            for n in range(0, len(fit_list)):
                subtract_list.append(Spectrum([], [], raw_data[n].basename))
                for i in range(0, len(line_spectrum_list[n].x)):
                    subtract_list[n].x.append(line_spectrum_list[n].x[i])
                    subtract_list[n].y.append(line_spectrum_list[n].y[i] - fit_list[n].y[i])
                spectrum_list.append(subtract_list[n])

        p.plot_anywhere()

        self.program.button_save.config(state=NORMAL)
        self.program.button_match_cores.config(state=NORMAL)
        self.program.entry_core_span.config(state=NORMAL)
        self.program.entry_core_span.delete(0)
        self.program.entry_core_span.insert(0, '7')
        self.program.shift1.config(state=NORMAL)
        self.program.shift2.config(state=NORMAL)

        if len(spectrum_list) == 2:
            self.program.button_match_cores.config(state=NORMAL)
            self.program.button_shift_core_plus.config(state=NORMAL)
            self.program.button_shift_core_minus.config(state=NORMAL)


# Handles the line cores in order to match them. Calculate mean intensity maxima
# Additionally, the mean core values are printed after shifting and bevore matching the cores
class MatchCores:
    def __init__(self, program):
        self.program = program
        self.core = None

    def match_cores(self):
        if button_status == 'CIII]':
            self.core = lines_c3_core
        if button_status == 'CIV':
            self.core = lines_c4_core
        if button_status == 'MgII':
            self.core = lines_mg2_core

        core_list1 = []
        core_list2 = []

        global core_span
        core_span = float(self.program.entry_core_span.get())

        # Calculate mean maxima for both spectra for interval of +- 7 Armstrong
        for i in range(len(spectrum_list[0].x)):
            if self.core - core_span < spectrum_list[0].x[i] < self.core + core_span:
                core_list1.append(spectrum_list[0].y[i])

        mean_intensity_core1 = np.mean(core_list1)

        for i in range(len(spectrum_list[1].x)):
            if self.core - core_span < spectrum_list[1].x[i] < self.core + core_span:
                core_list2.append(spectrum_list[1].y[i])

        mean_intensity_core2 = np.mean(core_list2)

        # Which intensity is the higher one
        if mean_intensity_core1 < mean_intensity_core2:
            multiplication_factor = mean_intensity_core2 / mean_intensity_core1
            for i in range(len(spectrum_list[0].y)):
                spectrum_list[0].y[i] = spectrum_list[0].y[i] * multiplication_factor
        else:
            multiplication_factor = mean_intensity_core1 / mean_intensity_core2
            for i in range(len(spectrum_list[1].y)):
                spectrum_list[1].y[i] = spectrum_list[1].y[i] * multiplication_factor

        p.plot_anywhere()
        p.line_span(self.core - core_span, self.core + core_span, 'grey')

        self.program.micro_bluewing.config(state=NORMAL)
        self.program.micro_redwing.config(state=NORMAL)
        self.program.entry_buffer.config(state=NORMAL)
        self.program.entry_interval.config(state=NORMAL)
        self.program.button_microlensing.config(state=NORMAL)
        self.program.entry_buffer.delete(0, END)
        self.program.entry_interval.delete(0, END)
        self.program.entry_buffer.insert(0, '7')
        self.program.entry_interval.insert(0, '30')

    @staticmethod
    # Shift the spectrum one angstrom to the right
    def shift_spectrum_right():
        for i in range(len(spectrum_list[number_of_spectrum].y)):
            spectrum_list[number_of_spectrum].x[i] = spectrum_list[number_of_spectrum].x[i] + 1
        p.plot_anywhere()

    @staticmethod
    # Shift the spectrum one angstrom to the left
    def shift_spectrum_left():
        for i in range(len(spectrum_list[number_of_spectrum].y)):
            spectrum_list[number_of_spectrum].x[i] = spectrum_list[number_of_spectrum].x[i] - 1
        p.plot_anywhere()


# Handles the microlensing calculations and output
class Microlensing:
    def __init__(self, program):
        # Initial values for buffer and interval
        self.program = program
        self.linecore = 0
        self.delta_magnitude_blue = []
        self.delta_magnitude_red = []

        self.buffer_blue = 7
        self.buffer_red = 7
        self.interval_blue = 30
        self.interval_red = 30

    def reset_values(self):
        self.linecore = 0
        self.delta_magnitude_blue = []
        self.delta_magnitude_red = []
        self.buffer_blue = 7
        self.buffer_red = 7
        self.interval_blue = 30
        self.interval_red = 30

    def get_wings_values(self):
        p.plot_anywhere()

        negative_test_blue = False
        negative_test_red = False
        low_number_test_blue = False
        low_number_test_red = False

        self.program.text_output_blue.config(state=NORMAL)
        self.program.text_output_red.config(state=NORMAL)

        if which_wing == 'blue':
            self.buffer_blue = float(self.program.entry_buffer.get())
            self.interval_blue = float(self.program.entry_interval.get())
        if which_wing == 'red':
            self.buffer_red = float(self.program.entry_buffer.get())
            self.interval_red = float(self.program.entry_interval.get())

        if button_status == 'CIII]':
            self.linecore = lines_c3_core
        if button_status == 'CIV':
            self.linecore = lines_c4_core
        if button_status == 'MgII':
            self.linecore = lines_mg2_core

        spectrum_list_wings_blue = [Spectrum([], [], raw_data[0].basename + ' wings blue'),
                                    Spectrum([], [], raw_data[1].basename + ' wings blue')]
        spectrum_list_wings_red = [Spectrum([], [], raw_data[0].basename + ' wings red'),
                                   Spectrum([], [], raw_data[1].basename + ' wings red')]

        # Cut off everything until wings and after wings
        # Buffer because linecore should start at core intervall not at core exactly.
        wing_blue_lower = self.linecore - self.buffer_blue - self.interval_blue
        wing_blue_upper = self.linecore - self.buffer_blue

        wing_red_lower = self.linecore + self.buffer_red
        wing_red_upper = self.linecore + self.buffer_red + self.interval_red

        p.line_span(wing_blue_lower, wing_blue_upper,
                    'lightskyblue')
        p.line_span(wing_red_lower, wing_red_upper, 'lightcoral')

        #########################################################################################################
        # Interpolation of both spectra
        #########################################################################################################
        # Get x values from both spectra and merge it into one list
        for n in range(0, 2):
            for i in range(0, len(spectrum_list[n].x)):
                if wing_blue_lower < spectrum_list[n].x[i] < wing_blue_upper:
                    spectrum_list_wings_blue[n].x.append(spectrum_list[n].x[i])
                    spectrum_list_wings_blue[n].y.append(spectrum_list[n].y[i])
                if wing_red_lower < spectrum_list[n].x[i] < wing_red_upper:
                    spectrum_list_wings_red[n].x.append(spectrum_list[n].x[i])
                    spectrum_list_wings_red[n].y.append(spectrum_list[n].y[i])

        # Interpolate both spectra with x values from other spectrum

        x_interpolated_blue = np.sort(
            np.concatenate((spectrum_list_wings_blue[0].x, spectrum_list_wings_blue[1].x), axis=None),
            axis=None)

        yinterp_0_blue = np.interp(x_interpolated_blue, spectrum_list_wings_blue[0].x, spectrum_list_wings_blue[0].y)
        yinterp_1_blue = np.interp(x_interpolated_blue, spectrum_list_wings_blue[1].x, spectrum_list_wings_blue[1].y)

        x_interpolated_red = np.sort(
            np.concatenate((spectrum_list_wings_red[0].x, spectrum_list_wings_red[1].x), axis=None),
            axis=None)

        yinterp_0_red = np.interp(x_interpolated_red, spectrum_list_wings_red[0].x, spectrum_list_wings_red[0].y)
        yinterp_1_red = np.interp(x_interpolated_red, spectrum_list_wings_red[1].x, spectrum_list_wings_red[1].y)

        spectrum_list_wings_red[0].x = x_interpolated_red
        spectrum_list_wings_red[0].y = yinterp_0_red

        spectrum_list_wings_red[1].x = x_interpolated_red
        spectrum_list_wings_red[1].y = yinterp_1_red

        spectrum_list_wings_blue[0].x = x_interpolated_blue
        spectrum_list_wings_blue[0].y = yinterp_0_blue

        spectrum_list_wings_blue[1].x = x_interpolated_blue
        spectrum_list_wings_blue[1].y = yinterp_1_blue

        #########################################################################################################
        # Blue wing
        #########################################################################################################
        # Are enough values in lists? Minimum values required: 2 because of the calculation of the stdv
        for n in range(0, 2):
            if len(spectrum_list_wings_blue[n].y) < 2:
                self.program.text_output_blue.delete(1.0, END)
                self.program.text_output_blue.insert(END, 'Number of values too low.')
                low_number_test_blue = True

        # Change to magnitude scale if no negative values
        if not low_number_test_blue:
            for n in range(0, 2):
                for i in range(len(spectrum_list_wings_blue[n].y)):
                    if spectrum_list_wings_blue[n].y[i] < 0:
                        self.program.text_output_blue.delete(1.0, END)
                        self.program.text_output_blue.insert(END, 'Negative value in blue wing.')
                        negative_test_blue = True

            if not negative_test_blue:
                for n in range(0, 2):
                    for i in range(len(spectrum_list_wings_blue[n].y)):
                        spectrum_list_wings_blue[n].y[i] = -2.5 * np.log10(spectrum_list_wings_blue[n].y[i])
                # Calculate delta magnitude blue wing
                self.delta_magnitude_blue.clear()

                for i in range(0, len(spectrum_list_wings_blue[0].y)):
                    self.delta_magnitude_blue.append(
                        np.sqrt(((spectrum_list_wings_blue[0].y[i] + spectrum_list_wings_blue[1].y[i]) /
                                 2) /
                                (spectrum_list_wings_blue[0].y[i] + spectrum_list_wings_blue[1].y[i])) * (
                                spectrum_list_wings_blue[1].y[i] - spectrum_list_wings_blue[0].y[i]))

                self.program.text_output_blue.delete(1.0, END)
                self.program.text_output_blue.insert(END, '\u0394m = ')
                self.program.text_output_blue.insert(END, '{:12.2f}'.format(np.mean(self.delta_magnitude_blue)))
                self.program.text_output_blue.insert(END, '\n\u03C3  = ')
                self.program.text_output_blue.insert(END, '{:12.2f}'.format(np.std(self.delta_magnitude_blue)))
                self.program.text_output_blue.insert(END, '\n\u0394m / \u03C3 = ')
                self.program.text_output_blue.insert(END, '{:8.2f}'.format((np.mean(self.delta_magnitude_blue) / np.std(
                    self.delta_magnitude_blue))))

        #########################################################################################################
        # Red wing
        #########################################################################################################
        # Are enough values in lists? Minimum values required: 2 because of the calculation of the stdv
        for n in range(0, 2):
            if len(spectrum_list_wings_red[n].y) < 2:
                self.program.text_output_red.delete(1.0, END)
                self.program.text_output_red.insert(END, 'Number of values too low.')
                low_number_test_red = True

        if not low_number_test_red:
            # Change to magnitude scale if no negative values
            for n in range(0, 2):
                for i in range(len(spectrum_list_wings_red[n].y)):
                    if spectrum_list_wings_red[n].y[i] < 0:
                        self.program.text_output_red.delete(1.0, END)
                        self.program.text_output_red.insert(END, 'Negative value in red wing.')
                        negative_test_red = True

            if not negative_test_red:
                for n in range(0, 2):
                    for i in range(len(spectrum_list_wings_red[n].y)):
                        spectrum_list_wings_red[n].y[i] = -2.5 * np.log10(spectrum_list_wings_red[n].y[i])
                # Calculate delta magnitude red wing
                self.delta_magnitude_red.clear()

                for i in range(0, len(spectrum_list_wings_red[0].y)):
                    denominator = spectrum_list_wings_red[0].y[i] + spectrum_list_wings_red[1].y[i]
                    w_i = np.sqrt(((spectrum_list_wings_red[0].y[i] + spectrum_list_wings_red[
                        1].y[i]) / 2) / denominator)
                    result = w_i * (spectrum_list_wings_red[1].y[i] - spectrum_list_wings_red[0].y[i])
                    self.delta_magnitude_red.append(result)

                self.program.text_output_red.delete(1.0, END)
                self.program.text_output_red.insert(END, '\u0394m = ')
                self.program.text_output_red.insert(END, '{:12.2f}'.format(np.mean(self.delta_magnitude_red)))
                self.program.text_output_red.insert(END, '\n\u03C3  = ')
                self.program.text_output_red.insert(END, '{:12.2f}'.format(np.std(self.delta_magnitude_red)))
                self.program.text_output_red.insert(END, '\n\u0394m / \u03C3 = ')
                self.program.text_output_red.insert(END, '{:8.2f}'.format(np.mean(self.delta_magnitude_red) / np.std(
                    self.delta_magnitude_red)))


# Defines a spectrum with x and y values. There can be an arbitrary number of spectra. The microlensing calculations
# only work for 2 spectra.
class Spectrum:
    def __init__(self, x, y, name, is_linear_fit=False):
        self.x = x
        self.y = y
        self.basename = name
        self.is_linear_fit = is_linear_fit


root = Tk()
my_program = Program(root)
root.mainloop()
