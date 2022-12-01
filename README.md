# Info Theory Semester 1 Project Code

## Installing SRILM and Others

### Install Python 3.11

Built from source, then had to modify `PATH` manually.

### SRILM 

`gcc`, `make`, `gzip` should all be pre-installed. `bzip2` was optional, but installed anyways.

Then, we must install `libiconv` and `GNU awk`. I downloaded each and moved them to /usr/share/libiconv and `/usr/share/gawk` respectively. Running the configuration as specified and then doing `sudo make` and `sudo make install` did the trick.

Make sure SRILM Makefile's SRILM variable is set properly. I had it at `/usr/share/srilm`. Then, running `sudo make World` worked, and then I had to set system variables.

Instructions said to set PATH to `$PATH:$SRILM/bin/$MACHINE_TYPE:$SRILM/bin`. I typed in manually:

```export PATH="$PATH:/usr/share/srilm/bin/i686-m64:/usr/share/srilm/bin"```

```export MANPATH="/usr/share/srilm/man"``` 

Check `MANPATH` first. This would override everything, but my `MANPATH` was empty.

Then to test, run `make test`. Once successful, go with `make cleanest` to clean up. 

I ran into error installing SWIG-SRILM, need to set `MAKE_PIC` to yes:

```MAKE_PIC = yes make```

### SWIG-SRILM

Download and unzip the file from GitHub. I also moved this to `/usr/share/swig-srilm`.

Modify the Makefile variables as needed. I think Perl is not necessary because we are coding in Python here.

I set `PYTHON_INC=/usr/local/include/python3.11` and SRILM variables are straightforward.

Then, I just run `make python` and copy `_srilm.so`, `srilm.py`, `test.py`, `test.txt`, `sample.lm` into this directory and ran it as test.

