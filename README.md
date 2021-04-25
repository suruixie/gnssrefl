## gnssrefl

### Table of Contents

1. [News](#news)
2. [Philosophy](#philosophy)
3. [Code Description](#code)
    1. [Installation](#environment)
    2. [rinex2snr: translating RINEX files into SNR files](#module1)
    3. [quickLook: assessing a site using SNR files](#module2)
    4. [gnssir: estimating reflector heights from SNR data](#module3)
4. [File Formats](#fileformats)
5. [Bugs/Future Work](#bugs)
6. [Utilities](#helper)
7. [Publications](#publications)
8. [Acknowledgements](#acknowledgements)

### News <a name="news"></a>

[We have started putting together a set of use cases.](https://github.com/kristinemlarson/gnssrefl/blob/master/tests/first_drivethru.md)

**April 17, 2012** New plot added to quickLook. This should provide feedback to the user on which QC 
metrics to use and which azimuths are valid. New plot also added to daily_avg.

**April 3, 2021** Added new plot in quickLook that provides perspective on choosing the right
azimuths and QC metrics

**March 30, 2021** Hopefully bug fixed related to the refraction file (gpt_1wA.pickle). If it is missing from your build,
it is now downloaded for you. Apologies. 

**March 29, 2021** The L2C and L5 options now use (appropriate) time-dependent lists of satellites. 

**March 17, 2021** I have removed CDDIS from the default RINEX 2.11 archive search list. It is still useable if you use 
-archive cddis.

**March 14, 2021** Minor changes - filenames using the hybrid option are allowed to be 132 characters long.
This might address issue with people that want to have very very very long path names.
I also added the decimation feature so it works for both GPS and GNSS.

February 24, 2021 We now have three translation options for RINEX files: fortran, hybrid, and python. The last of these
is ok for 30 sec data but really too slow otherwise. Hybrid binds the python to my (fast) fortran code.
This has now been implemented for both GPS and multi-GNSS.

CDDIS is an important GNSS data archive. Because of the way that CDDIS has 
implemented security restrictions, we have had to change our download access. 
For this reason we strongly urge that you install **wget** on your machine and that 
it live in your path. You will only have very limited analysis abilities without it.

I have added more defaults so you don't have to make so many decisions. The defaults are that  
you are using GPS receiver (not GNSS) and have a fairly standard geodetic 
site (i.e. not super tall, < 5 meters). If you have previously used this package, please
note these changes to **rinex2snr**, **quickLook**, and **gnssir**.
Optional commandline inputs are still allowed.

How can you learn how to run this code correctly? You should start by reading
[Roesler and Larson, 2018](https://link.springer.com/article/10.1007/s10291-018-0744-8). 
Although this article was originally written to accompany Matlab scripts,
the principles are the same. It explains to you what a reflection
zone means and what a Nyquist frequency is for GNSS reflections. 
My reflection zone webapp will [help you pick appropriate elevation and azimuth angles.](https://gnss-reflections.org/rzones) 

If you are interested in measuring sea level, this webapp tells you [how high your site is above 
sea level.](https://gnss-reflections.org/geoid)  

### Philosophical Statement <a name="philosophy"></a>
In geodesy, you don't really need to know much about what you are doing to 
calculate a reasonably precise position from GPS data. That's just the way it is.
(Note: that is also thanks to the hard work of the geodesists that wrote the 
computer codes). For GPS/GNSS reflections, you need to know a little bit more - like what are you
trying to do? Are you trying to measure water levels? Then you need to know where the water
is! (with respect to your antenna, i.e. which azimuths are good and which are bad). 
Another application of this code is to measure snow accumulation. If you 
have a bunch of obstructions near your antenna, 
you are responsible for knowing not to use that region. If your antenna is 10 meters 
above the reflection area, and the software default only computes answers up to 6 meters,
the code will not tell you anything useful. It is up to you to know what is best for the site and 
modify the inputs accordingly. 
I encourage you to get to know your site. If it belongs to you, look at 
photographs. If you can't find photographs, use Google Earth.  You can also try using
my [google maps web app interface](https://gnss-reflections.org/geoid?station=smm3).


### Code Description<a name="code"></a>

**gnssrefl** is a new version of my GNSS interferometric reflectometry (GNSS-IR) code. 

The main difference bewteen this version and previous versions is that I am
attempting to use proper python packaging rules! However, this is a big learning curve for me,
and I know that I still have a lot to learn. I have separated out the main
parts of the code and the command line inputs so that you can use the libraries
yourself or do it all from the command line. This should also - hopefully - make
it easier for the production of Jupyter notebooks. The latter are to be developed
by UNAVCO with NASA GNSS Science Team funding.

*If you would like to try out reflectometry without installing the code*

I recommend you use the web app [I developed](https://gnss-reflections.org). It 
can show you representative results with minimal constraints. It should provide 
results in less than 10 seconds.

*If you prefer Matlab*

I had a [working matlab version on github](https://github.com/kristinemlarson/gnssIR_matlab_v3), 
but I will not be updating it. You will very likely have to make changes to accommodate the recent
change in security protocols at CDDIS.

*Goals*

The goal of this python repository is to help you compute (and evaluate) GNSS-based
reflectometry parameters using geodetic data. This method is often
called GNSS-IR, or GNSS Interferometric Reflectometry. There are three main modules:

* **rinex2snr** translates RINEX files into SNR files needed for analysis.

* **gnssir** computes reflector heights (RH) from SNR files.

* **quickLook** gives you a quick (visual) assessment of a file without dealing
with the details associated with **gnssir**. It is not meant to be used for routine analysis.
It also helps you pick an appropriate azimtuh mask and quality control settings.

There are also various utilities you might find to be useful (see the last section).
To see the names of these utilities:

* pip list 


If you are unsure about why various restrictions are being applied, it is really useful 
to read [Roesler and Larson (2018)](https://link.springer.com/article/10.1007/s10291-018-0744-8) 
or similar. I am committed in principle to set up some online
courses to teach people about GNSS reflections, but funding for these courses is 
not in hand at the moment. 

To summarize, direct (blue) and reflected (red) GNSS signals interfere and create
an interference pattern that can be observed in GNSS data as a satellite rises or sets. 
The frequency of this interference pattern is directly related to the height of the antenna phase
center above the reflecting surface, or reflector height RH (purple). Accordingly, this code strips out 
rising and setting satellite arcs and estimates RH.

<center>
<img src="https://gnss-reflections.org/static/images/overview.png" width="500" />
</center>

### Installing the Code<a name="environment"></a>

*Environment Variables*
   
You should define three environment variables:

* EXE = where various RINEX executables will live.

* ORBITS = where the GPS/GNSS orbits will be stored. They will be listed under directories by 
year and sp3 or nav depending on the orbit format.

* REFL_CODE = where the reflection code inputs (SNR files and instructions) and outputs (RH)
will be stored (see below). Both SNR files and results will be saved here in year subdirectories.

If you don't define these environment variables, the code should assume your local working directory (where you installed
the code) is where you want everything to be. The orbits, SNR files, and periodogram results are stored in 
directories in year, followed by type, i.e. snr, results, sp3, nav, and then by station name.

*Installing the Python*

If you are using the version from gitHub:

* git clone https://github.com/kristinemlarson/gnssrefl 
* cd into that directory, set up a virtual environment, a la python3 -m venv env 
* activate your virtual environment
* pip install .

If you use the PyPi version:  

* make a directory, cd into that directory, set up a virtual environment 
* activate the virtual environment
* pip install gnssrefl

To use **only** python codes, you will need to be sure that your RINEX files are not Hatanaka 
compressed.

*Non-Python Code*

**All executables must be stored in the EXE directory.**  If you do not define EXE, 
it will look for them in your local working directory.  The Fortran translators are 
much faster than using python. We now advocate using the hybrid translator option, which 
links to the Fortran internally. Using true python to translate a high-rate GPS file is 
impossibly slow.

* Required Translator for compressed (Hatanaka) RINEX files. CRX2RNX, http://terras.gsi.go.jp/ja/crx2rnx.html. 

* Optional Fortran RINEX Translator for GPS. **The executable must be called gpsSNR.e.** For the code: https://github.com/kristinemlarson/gpsonlySNR

* Optional Fortran RINEX translator for multi-GNSS. **The executable must be called gnssSNR.e** For the code: https://github.com/kristinemlarson/gnssSNR

* Optional datatool, **teqc**, is highly recommended.  There is a list of static executables at the
bottom of [this page](http://www.unavco.org/software/data-processing/teqc/teqc.html). 

* Optional datatool, **gfzrnx** is required if you plan to use the RINEX 3 option. Executables available from the GFZ,
http://dx.doi.org/10.5880/GFZ.1.1.2016.002. 


### File Formats <a name="fileformats"></a>

(under construction)

RINEX files must be version 2.11 or 3. 

For RINEX 2.11, filenames should be lowercase and following the community standard: 

4 character station name + day of year (3 characters) + '0.' + two character year  + 'o'

In many cases Hatanaka compressed formats are used by data archives. These have a 
'd' instead an 'o' at the end of the filename.

We are working to make a NMEA reader for this software package.

### rinex2snr - extracting SNR data from RINEX files <a name="module1"></a>

The international standard for sharing GNSS data is called 
the [RINEX format](https://www.ngs.noaa.gov/CORS/RINEX211.txt).
A RINEX file has extraneous information in it (which we will throw out) - and it 
does not provide some of the information needed for reflectometry (e.g. elevation and azimuth angles). 
The first task you have in GNSS-IR is to translate from RINEX into what I will 
call the SNR format. The latter will include azimuth and elevation angles. For the 
latter you will need an **orbit** file. **rinex2snr**
will go get an orbit file for you. You can override the default orbit 
choice by selections given below.

There is no reason to save ALL the RINEX data as the reflections are only useful at the lower elevation
angles. The default is to save all data with elevation lower than 30 degrees (this is called SNR format 66).
Another SNR choice is 99, which saves elevation angle data between 5 and 30.  

There are rules for naming RINEX files. **My code requires that RINEX (version 2) files be lowercase.**
The filename must be 12 characters long (ssssddd0.yyo), where ssss is station name, 
ddd is day of year, followed by a zero, yy is the two character year and o stands for observation. 
If you have installed the CRX2RNX code, you can also provide a compressed RINEX format file, which ends in a d.
I think my code allows you to gzip the RINEX files if you are providing them.

You can run **rinex2snr** at the command line. You required inputs are:

- station name
- year
- day of year

A sample call for a station called p041, restricted to GPS satellites, on day of year 132 and year 2020 would be:

<code>rinex2snr p041 2020 132</code>

If the RINEX file for p041 is in your local directory, it will translate it.  If not, 
it will check three archives (unavco, sopac, and sonel) to find it. 
This uses the hybrid translator.  If you did install a fortran translator, the command would be:

<code>rinex2snr p041 2020 132 -translator fortran</code>

For python:

<code>rinex2snr p041 2020 132 -translator python</CODE>


Here is an example from a site in Greenland (the RINEX file will be picked up from unavco):

<code>rinex2snr gls1 2011 271</code>

Allowed GNSS Data Archives:

- unavco
- sonel (global sea level observing system)
- sopac (Scripps Orbit and Permanent Array Center)
- cddis
- ngs (National Geodetic Survey)
- nrcan (Natural Resources Canada)
- bkg (German Agency for Cartography and Geodesy)
- nz (GNS New Zealand)
- ga (Geoscience Australia)
- bev (Austria Federal Office of Metrology and Surveying)

<code>rinex2snr tgho 2020 132 -archive nz</code>

What if you want to run the code for all the data for any year?  You can use doy_end:

<code>rinex2snr tgho 2019 1  -archive nz -doy_end 365</code>
 
If your station name has 9 characters (lower case please), the code assumes you are looking for a 
RINEX 3 file. However, my code will store the SNR data using the normal
4 character name. **You must install the gfzrnx executable that translates RINEX 3 to 2 to use RINEX 3 files
in my code.** *rinex2snr* currently only looks for 
RINEX 3 files at CDDIS (30 sec) and UNAVCO (15 sec).  There 
are more archive options in **download_rinex** and someday I will 
merge these. If you do have your own RINEX 3
files, I use the community standard, that is upper case except 
for the file extension (which is rnx).  I know, it is weird.

Here are some examples for RINEX 3 conversions:

<code>rinex2snr onsa00swe 2020 298</code>

<code>rinex2snr at0100usa 2020 55</code>

<code>rinex2snr mdo100usa 2020 290</code>

<code>rinex2snr mkea00usa 2020 290</code>

The snr options are mostly based on the need to remove the "direct" signal. This is 
not related to a specific site mask and that is why the most frequently used 
options (99 and 66) have a maximum elevation angle of 30 degrees. The
azimuth-specific mask is decided later when you run **gnssir**.  The SNR choices are:

- 66 is elevation angles less than 30 degrees (**this is the default**)
- 99 is elevation angles of 5-30 degrees  
- 88 is elevation angles of 5-90 degrees
- 50 is elevation angles less than 10 degrees (good for very tall sites, high-rate applications)

*orbit file options for general users:*

- gps : will use GPS broadcast orbits (**this is the default**)
- gps+glos : will use JAXA orbits which have GPS and Glonass (usually available in 48 hours)
- gnss : will use GFZ orbits, which is multi-GNSS (available in 3-4 days?)

*orbit file options for experts:*

- nav : GPS broadcast, perfectly adequate for reflectometry. 
- igs : IGS precise, GPS only
- igr : IGS rapid, GPS only
- jax : JAXA, GPS + Glonass, within a few days, very reliable
- gbm : GFZ Potsdam, multi-GNSS, not rapid
- grg: French group, GPS, Galileo and Glonass, not rapid
- wum : (disabled) Wuhan, multi-GNSS, not rapid

It would be very helpful to add broadcast orbits for Galileo, Glonass, and Beidou. Based 
on my experience with GPS, I know that this will be much much much faster if we use Fortran
code and bind with python using numpy. If you have such code, or know where it lives, please let me know.

Other questions:

- What if you do not want to install the fortran translators? That should be ok as the default
is the hybrid option, which does not require fortran.

- What if you are providing the RINEX files and you don't want the code to search for 
the files online? Use -nolook True

There is a **rate** command line input that has two values, high or low. 
However, if you invoke high, it currently only looks at the UNAVCO, GA, or 
NRCAN archives. Please beware - it takes a long time to download a 
highrate GNSS RINEX file (even when it is compressed). 
And it also takes a long time to compute orbits for it (and thus create a SNR file).
For high-rate data, you should use hybrid or fortran translators.

*SNR file format*

To columns are defined as:

1. Satellite number (remember 100 is added for Glonass, etc)
2. Elevation angle, degrees
3. Azimuth angle, degrees
4. Seconds of the day, GPS time
5. elevation angle rate of change, degrees/sec.
6.  S6 SNR on L6
7.  S1 SNR on L1
8.  S2 SNR on L2
9.  S5 SNR on L5
10. S7 SNR on L6
11. S8 SNR on L8

The unit for all SNR data is dB-Hz.

### quickLook <a name="module2"></a>

Before using the **gnssir** code, I recommend you try **quickLook**. This allows you
to quickly test various options (elevation angles, frequencies, azimuths).
The required inputs are station name, year, and doy of year. **You must have previously translated a RINEX file using rinex2snr for this to work.**

**quickLook** has stored defaults for analyzing the spectral characteristics of the SNR data. 
In general these defaults are meant to facilitate users where the antenna is less than 5 meters tall.**
If your site is taller than that, you will need to override the defaults.
Similarly, the default elevation angles are 5-25 degrees. If that mask includes a reflection region
you don't want to use, you need to override them.

For more information, use <code>quickLook -h</CODE>

Going back to our **rinex2snr** example, try running the data for station p041.

<code>quickLook p041 2020 132 </CODE>

That command will produce this periodogram summary:

<img src="tests/use_cases/p041-l1.png" width=500>

By default, these are L1 data only. Note that the x-axis does not go beyond 6 meters. This is because
you have used the defaults. Furthermore, note that results on the x-axis begin at 0.5 meters.
Since you are not able to resolve very small reflector heights with this method, this region 
is not allowed. These periodograms give you a sense of whether there is a 
planar reflector below your antenna. The fact that 
the peaks in the periodograms bunch up around 2 meters means that at 
this site the antenna phase center is ~ 2 meters above the ground. The colors 
change as you try different satellites.  If the data are plotted in
gray that means you have a failed reflection. The quadrants are Northwest, Northeast and so on. 

**quickLook** also provides a summary of various quality control metrics:

<img src="tests/use_cases/p041_l1_qc.png" width=600>

The top plot shows the sucessful RH retrievals in blue and unsuccessful RH retrievals in gray. 
Below are the peak to noise ratios. The last plot is the amplitude of the spectral peak. The dashed
lines show you what QC metrics quickLook was using. You can control/change these on the command line
(quickLook -h).

If you want to look at L2C data: 

<CODE>quickLook p041 2020 132 -fr 20</CODE>

<img src="tests/use_cases/p041-l2c.png" width=600>

In general, L2C results are always superior to L1 results. If you had set -h2 20, it would
look [like this](tests/use_cases/p041-l2c-again.png). You aren't gaining anything by doing this.

<HR>
Lets look at two days of data collected on the Greenland Ice Sheet. 
You already have one file. Now make one three years later.
<P>
<code>rinex2snr gls1 2014 271</CODE>

Now run quickLook, focusing on the QC plots:

<CODE>quickLook gls1 2011 271</CODE> 

<CODE>quickLook gls1 2014 271</CODE> 


<TABLE>
<TR>
<img src="tests/use_cases/gls1-2011.png">
</TR>
<TR>
<img src="tests/use_cases/gls2-2014.png">
</TR>
</TABLE>

<P>
<HR>
<P>
Finally, what do you do if your reflections site is taller than the default value of 6 meters?
Does the code figure this out for you automatically? **No, it does not.** We use an example 
from Greenland to demonstrate this issue. First make a SNR file using the defaults: 

<CODE>rinex2snr smm3 2018 271</CODE>

Now run **quickLook** using the defaults:

<CODE>quickLook smm3 2018 271</CODE>

<img src="tests/use_cases/smm3-default.png" width=600> 

Everything is gray (which means it didn't find a significant reflector) because you 
only calculated periodograms for reflector height values of 0.5 to 6 meters. You see some things
that might be significant at small RH, but this is just the effect of the antenna gain pattern. 
This site is ~16 meters above the ice. Accordingly, if you change the inputs to tell the program
that you want to examine reflector heights between 8 and 20 meters, i.e. 

<CODE>quickLook smm3 2018 271 -h1 8 -h2 20</CODE>

<img src="tests/use_cases/smm3-sensible.png" width=600>

You now see what you expect to see - peaks of periodograms at ~16 meters height. 
Why is the northwest quadrant so messy? I leave that as an exercise for the reader. Hint: start out by trying
to examine this site on Google Earth.

### gnssir <a name="module3"></a>

This is the main driver for the GNSS-IR code.  
You need a set of instructions for **gnssir** which are made using **make_json_input**.  
The required inputs for **make_json_input** are: 

* station name 
* latitude (degrees)  
* longitude (degrees) 
* ellipsoidal height (meters). 

The station location *does not* have to be cm-level for the reflections code. Within 
a few hundred meters is sufficient. For example: 

<CODE>make_json_input p101 41.692 -111.236 2016.1</CODE>

If you happen to have the Cartesian coordinates (in meters), you can set -xyz True and input those instead of 
lat, long, and height.

It will use defaults for other parameters if you do not provide them. Those defaults 
tell the code an azimuth and elevation angle mask (i.e. which directions you want 
to allow reflections from), and which frequencies you want to use, and various quality control (QC) metrics. 
Right now the default frequencies are GPS only, e.g. L1, L2C and L5. 
The json file of instructions will be put in $REFL_CODE/input/p101.json. You should look at 
it to get an idea of the kinds of inputs the code uses.
The default azimuths can be changed, but this needs to be done by hand. Some parameters can be set
via the command line, as in:

<CODE>make_json_input p101 41.692 -111.236 2016.1 -e1 5 -e2 10</CODE>

This changes elevation angles to 5-10 degrees. The default is to only use GPS 
frequencies, specifically L1, L2C, and L5. If you want all GNSS frequencies:

<CODE>make_json_input p101 41.692 -111.236 2016.1 -e1 5 -e2 10 -allfreq True</CODE>

To only use GPS L1:

<CODE>make_json_input p101 41.692 -111.236 2016.1 -e1 5 -e2 10 -l1 True </CODE>

To only use GPS L2C and require a spectral amplitude of 10:

<CODE>make_json_input p101 41.692 -111.236 2016.1 -e1 5 -e2 10 -l2c True -ampl 10</CODE>

To use GPS L2C, require a spectral amplitude of 10, and spectral peak to noise ratio of 3:

<CODE>make_json_input p101 41.692 -111.236 2016.1 -e1 5 -e2 10 -l2c True -ampl 10 -peak2noise 3</CODE>

As discussed in Roesler and Larson (2018), there are two QC measures used in this code. One is the peak 
value of the peak in the periodogram. In the example below the amplitude of the most significant 
peak is ~17, so if you define the required amplitude 
to be 15, this one would pass. Secondly it uses a very simple peak to noise calculation. In this case the 
average periodogram amplitude value is calculated for a RH region that you define, and that is the "noise". 
You then take the peak value (here ~17) and divide by the "noise" value.  
For the ocean, I generally recommend starting with a peak to noise ratio of 2.7, but for lakes or snow, I use 
3.2-3.5 or so. It can be tricky to set these QC values in general. 

<center>
<img src="https://github.com/kristinemlarson/gnssrefl/blob/master/tests/for_the_web.png" width="600"/>
</center>

Things that are helpful to know for the make_json_input inputs:

*Our names for the GNSS frequencies*

- 1,2,5,20 are GPS L1, L2, L5, and L2C
- 101,102 Glonass L1 and L2
- 201, 205, 206, 207, 208: Galileo frequencies
- 302, 306, 307 : Beidou frequencies

* Some json settings can be set at the command line.  run **make_json_input -h** to see these.  
Otherwise, edit the json file.  Note that there are a few inconstencies between the command line names 
and the json file (for example, h1 and h2 on the command line become
minH and maxH in the json file). I apologize for this.

- e1 and e2 are the min and max elevation angle, in degrees
- minH and maxH are the min and max allowed reflector height, in meters
- desiredP, desired reflector height precision, in meters
- PkNoise is the periodogram peak divided by the periodogram noise ratio.  
- reqAmp is the required periodogram amplitude value, in volts/volts
- polyV is the polynomial order used for removing the direct signal
- freqs are selected frequencies for analysis
- delTmax is the maximum length of allowed satellite arc, in minutes
- azval are the azimuth regions for study, in pairs (i.e. 0 90 270 360 means you want to evaluate 0 to 90 and 270 to 360).
- wantCompression, boolean, compress SNR files using xz
- screenstats, boolean, whether minimal periodogram results come to screen
- refraction, boolean, whether simple refraction model is applied.
- plt_screen: boolean, whether SNR data and periodogram are plotted to the screen 
- NReg [min and max required] : define the RH region where the "noise value" for the periodogram 
is computed. This is used to compute the peak to noise ratio used in QC.
- (*this option has been removed*) seekRinex: boolean, whether code looks for RINEX at an archive

Simple examples for my favorite GPS site [p041](https://spotlight.unavco.org/station-pages/p042/eo/scientistPhoto.jpg)

<CODE>make_json_input p041 39.949 -105.194 1728.856</CODE> (use defaults and write out a json instruction file)

<CODE>rinex2snr p041 2020 150</CODE> (pick up and translate RINEX file for day of year 150 and year 2020 from unavco )

<CODE>gnssir p041 2020 150</CODE> (calculate the reflector heights) 

<CODE>gnssir p041 2020 150 -fr 5 -plt True</CODE> (override defaults, only look at L5 SNR data, and periodogram plots come to the screen)

Where would the code store the files for this example?

- json instructions are stored in $REFL_CODE/input/p041.json
- SNR files are stored in $REFL_CODE/2020/snr/p041
- Reflector Height (RH) results are stored in $REFL_CODE/2020/results/p041

This is a snippet of what the result file would look like

<img src="https://github.com/kristinemlarson/gnssrefl/blob/master/tests/results-snippet.png" width="600">

- *Amp* is the amplitude of the most significant peak in the periodogram (i.e. the amplitude for the RH you estimated).  
- *DelT* is how long a given rising or setting satellite arc was, in minutes. 
- *emin0* and *emax0* are the min and max observed elevation angles in the arc.
- *rise/set* tells you wehther the satellite arc was rising or setting
- *Azim* is the average azimuth angle of the satellite arc
- *sat* and *freq* are as defined in this document

If you want a multi-GNSS solution, you need to make a new json file and 
use multi-GNSS orbits, and use a RINEX file that has multi-GNSS SNR observations in it. 
In 2020 p041 had a multi-GNSS receiver operating, so we can look at some of the non-GPS signals.
In this case, we will look at Galileo L1.  

<CODE>make_json_input p041 39.949 -105.194 1728.856 -allfreq True</CODE>

<CODE>rinex2snr p041 2020 151 -orb gnss</CODE>

<CODE>gnssir p041 2020 151 -fr 201 -plt True</CODE> 

What should the periodogram plots look like? Until we have Jupyter notebooks, I 
recommend you look at [the paper I wrote with Carolyn Roesler](https://link.springer.com/article/10.1007/s10291-018-0744-8) 
or the [question section of my web app.](https://gnss-reflections.org/overview). Note that a failed
arc is shown as gray in the periodogram plots. And once you know what you are doing (have picked
the azimuth and elevation angle mask), you won't be looking at plots anymore.

### Bugs/Features <a name="bugs"></a>

I have been using **teqc** to reduce the number of observables and to decimate. I have removed the former 
because it unfortunately- by default - removes Beidou observations in Rinex 2.11 files. If you request decimation 
and fortran is set to True, unfortunately this will still occur. I am working on removing my 
code's dependence on **teqc**.

No phase center offsets have been applied to reflector heights. While these values are relatively small,
we do plan to remove them in subsequent versions of the code. 

At least one agency (JAXA) writes out 9999 values for unhealthy satellites. I should remove these satellites 
at the rinex2snr level, but currently (I believe) the code simply removes the satellites because the elevation
angles are all very negative (-51). JAXA also has an incomplete number of GPS satellites in its sp3 files (removing 
the newer ones). It is unfortunate, but I cannot do anything about this.

### Utilities <a name="helper"></a>

**daily_avg** is a utility for cryosphere people interested in computing daily snow 
accumulation. It can be used for lake levels. *It is not to be used for tides!*

**download_rinex** can be useful if you want to download RINEX v2 or 3 files (using the version flag) without using 
the reflection-specific codes. Sample calls:

<CODE>download_rinex p041 2020 6 1</CODE> downloads the data from June 1, 2020

<CODE>download_rinex p041 2020 150 0</CODE> downloads the data from day of year 150 in 2020

<CODE>download_rinex p041 2020 150 0 -archive sopac</CODE> downloads the data from sopac archive on day of year 150 in 2020

**download_orbits** downloads orbit files. See -h for more information.

**ymd** translates year,month,day to day of year

**ydoy** translates year,day of year to month and day

**llh2xyz** translates latitude, longitude, and ellipsoidal ht to X, Y, Z

**xyz2llh** translates Cartesian coordinates to latitude, longitude, height

**gpsweek** translates year, month, day into GPS week, day of week (0-6) 
   
**download_unr** downloads ENV time series for GPS sites from the Nevada Reno website (IGS14), so ITRF 2014.

**download_tides** downloads up to a month of NOAA tide gauge data given station number (7 characters),
and begin/end dates, e.g. 20150601 would be June 1, 2015. The NOAA API works perfectly well for this,
but this utility writes out a file with only columns of numbers instead of 
csv. 

### Publications <a name="publications"></a>

There are A LOT of publications about GPS and GNSS interferometric reflectometry.
If you want something with a how-to flavor, try this paper, 
which is [open option](https://link.springer.com/article/10.1007/s10291-018-0744-8). Also 
look to the publications page on my [personal website](https://kristinelarson.net/publications).


### Acknowledgements <a name="acknowledgements"></a>

[Radon Rosborough](https://github.com/raxod502) helped me with my python questions. 
Joakim Strandberg provided python RINEX translators, and Johannes Boehm provided source code for the 
refraction correction. 


Kristine M. Larson

This documentation was updated on April 17, 2021.
