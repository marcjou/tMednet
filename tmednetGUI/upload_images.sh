#!/bin/sh


sv="t-mednet.org 21"
user="t-mednet"
pass="lk@hRTpo1"
month=$(date --date='yesterday' +'%b')
year=$(date --date='yesterday' +'%Y')

cd /home/marcjou/Escritorio/Projects/tMednet/src/output_images

ftp -n $sv <<END_SCRIPT
quote USER $user
quote PASS $pass

cd httpdocs/images/heatwaves/${year}
put anim_MHW_days_${month}.gif
put anim_MHW_imax_${month}.gif
quit 

END_SCRIPT







