tempdir <- "C:/Users/TJ/AppData/Local/Temp"
dir.create(tempdir, showWarnings = FALSE)
Sys.setenv(TMPDIR = tempdir)
Sys.getenv(c("TMPDIR", "TEMP", "TMP"))
Sys.setenv(TMPDIR = "C:/Your/Custom/TempDir")

icacls "C:\Users\TJ\AppData\Local\Temp" /grant desktop-fqsttoh\tj:(OI)(CI)(F) /T