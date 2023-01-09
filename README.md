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

Note: this actually ended up not affecting the PATH at all, so I ended up manually adding `i686-m64` to `$PATH` by making a script in `/etc/profile.d/srilm.sh` with the following text:

```pathmunge /usr/share/srilm/bin/i686-m64```

### SWIG-SRILM

Download and unzip the file from GitHub. I also moved this to `/usr/share/swig-srilm`.

Modify the Makefile variables as needed. I think Perl is not necessary because we are coding in Python here.

I set `PYTHON_INC=/usr/local/include/python3.11` and SRILM variables are straightforward.

Then, I just run `make python` and copy `_srilm.so`, `srilm.py`, `test.py`, `test.txt`, `sample.lm` into this directory and ran it as test.

### Training the LM

To train the LM, I used `convert.py` to parse all of the BNC's text into purely tokenized words, where then each sentence occupies a line for SRILM to parse.

Then, I used `ngram-count` to train the LM:

```ngram-count -order 5 -kndiscount -interpolate -text bnc-corpus.txt -l bnc.lm```

And I pruned the LM of low probability words with:

```ngram -lm bnc.lm -prune 1e-8 -write-lm bnc-pruned.lm```

We now have an ARPA LM stored as the file `bnc-pruned.lm`.

### Calculation

From this point on, we will use the calculated bigram and unigram logprobs for our entropy calculation.

Calculate probabilities with SRILM:
```ngram -lm bnc-pruned.lm -order 2 -ppl test.txt -debug 2```

Using SWIG-SRILM wrapper, Python code does it as well:
```getBigramProb(n, "this phrase")```
```getUnigramProb(n, "phrase")```
```getSentenceProb(n, "this is a sentence of length seven", 7)```