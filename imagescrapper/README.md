scrapper.py
Description:
This script works by reading a local HTML file. Users must manually paste the HTML skeleton (e.g., fetched from Zyte.com) into the designated file (http_response_body.html). The script then parses the HTML and downloads the images found.

scrapper2.py
Description:
This enhanced script targets the srcset attribute that lists multiple image URLs along with their resolution multipliers. It selects the candidate with the highest multiplier—thus ensuring that the highest resolution image is downloaded.

Improvisations at scrapper 2 
=> high resolution images to be needed for scrapped data, so make sure to attain its original image, rather than thumbnail image as of whole 
=>when runned, multiple times the code resturn output images in the same directory, resulting in confusion, so better to alter the code to create new directories for each run (resuting in low confusion)
