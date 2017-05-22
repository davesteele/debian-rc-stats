
# Debian RC Stats

These are some helper scripts to collect and report on Debian Testing
Release-Critical bugs over time.


## Scripts

### getbts

Download the backing spools from BTS, and store them in the local
*btsspool* directory. As of Aug 2017, this will result in a download
of 3M files into a 100GB directory tree.

### comments.py

Scrape the local BTS spool, creating *comments.json* and *bugs.json*.
The first contains information on every comment on the RC bugs, and 
the second information on the bugs themselves.


### srclookup.py

Read a local Packages file, and create a source package lookup
dictionary *srclookup.json*. The Packages file needs to be downloaded and
uncompressed before running the command.


### testuploads.py

Scrape the Debian Testing Changes mailing list archive, and store
*testing* upload information to *uploads.json*.


### makecsv.py

Create csv output with per-week stats for *outbugs.json*.


### buginfo.py

Analyze the local bugs.json, comments.json, srclookup.json, and uploads.json,
and output a processed bug list, *outbugs.json*.


## Files

### datestats.csv/ods

The output of makecsv.

### deb-popularity-dc17.odp

A slide presentation of some results.

