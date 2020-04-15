# EvolvingObjects

### Konvertování z .svg do .png

sh batch_convert.sh svg png


### Vytvoření videa

ffmpeg -framerate 2 -i img-%2d.png output.avi
