# sparebankcup22_urskog_result_fixer
Bypasses a bug in the result compilation for [Sparebankcupen 2022](https://dfsgrasrot.no/sparebankcupen)

## How to install
1. If Python has not already been installed, download and install python: https://www.python.org/downloads/

2. [Download this repository](https://github.com/tussedrotten/sparebankcup22_urskog_result_fixer/archive/refs/heads/main.zip) 
   and unzip the contents in an appropriate directory, for example `C:\sparebankcup22_urskog_result_fixer`
   

## How to use

### Arguments
Calling `sparebankcup22_urskog_result_fixer.py` with the help flag prints:
```
C:\sparebankcup22_urskog_result_fixer>python sparebankcup22_urskog_result_fixer.py -h
usage: sparebankcup22_urskog_result_fixer.py [-h] [--ftp_user FTP_USER] [--ftp_pass FTP_PASS] input output

Bypasses a bug in the result compilation for Sparebankcupen 2022

positional arguments:
  input                Path to the input xml file.
  output               Path to the output xml file (cannot be the same as input)

optional arguments:
  -h, --help           show this help message and exit
  --ftp_user FTP_USER  Username for 'ftp.livevisning.com' - will not use FTP if None (default: None)
  --ftp_pass FTP_PASS  Password for 'ftp.livevisning.com' (default: )
```

Notice that you need to call `python.exe` with `sparebankcup22_urskog_result_fixer.py` and arguments
specifying the input and output files, and optionally username and password for the `ftp.livevisning.com` server.

### Example: Fix without uploading to the FTP server
```
C:\<PYTHON_DIR>\python.exe C:\sparebankcup22_urskog_result_fixer\sparebankcup22_urskog_result_fixer.py "C:\result\stevneoppgjør.xml" "C:\result\fixed\stevneoppgjør.xml"
```
where `<PYTHON_DIR>` is where python is installed.

### Example: Fix and upload to FTP server
```
C:\<PYTHON_DIR>\python.exe C:\sparebankcup22_urskog_result_fixer\sparebankcup22_urskog_result_fixer.py --ftp_user user@server.com --ftp_pass mypassword "C:\result\stevneoppgjør.xml" "C:\result\fixed\stevneoppgjør.xml"
```
where `<PYTHON_DIR>` is where python is installed.

### Running the fix with a batch file
For simplicity, we can write a batch file to run the fix.

The example above can for example be run from `sparebankcup22_urskog_result_fixer.bat` with the contents:
```bat
@echo off
chcp 65001
C:\<PYTHON_DIR>\python.exe ^
 C:\sparebankcup22_urskog_result_fixer\sparebankcup22_urskog_result_fixer.py ^
 --ftp_user user@server.com --ftp_pass mypassword ^
 "C:\result\stevneoppgjør.xml" ^
 "C:\result\fixed\stevneoppgjør.xml"
pause
```

### Stopping the program
Stop the program by pressing `Ctrl+c` in the terminal window.
