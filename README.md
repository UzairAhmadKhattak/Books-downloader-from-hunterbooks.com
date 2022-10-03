# Books-downloader-from-hunterbooks.com  

## Introduction:
This project was created for a client and he has given me permission to make it public.  

## What this project do: 
This project is basically downloads books and their images. These books downloads from an online book store (Hunterbooks.com) in format of epub. Then these
files are converted into pdf file using online converter. When the files are successfuly converted into pdf it is downloaded. so when we have both file (epub and pdf) 
the process goes further and upload both files to a server called OnUploads(provides the way to share files). The server generates link for each file. These links
gets scrape and entrs in sql table with name of the file, category, epuburl, pdfurl and website url.

## GUI: 
PYQT5 is used to make GUI. There is one input field for start page number and one input field for end page number and two inputs fields for OnUpload credentials 
that are username and password. The last field is button that is used to start the process.
