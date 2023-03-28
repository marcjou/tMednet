#!/bin/sh

# WRITE THE WAY TO SELECT THE CURRENT MONTH TO UPLOAD THE FILES THAT SHOULD BE UPLOADED
sv="t-mednet.org 21"
user="t-mednet"
pass="lk@hRTpo1"

cd ../src/output_images

ftp -n $sv <<END_SCRIPT
quote USER $user
quote PASS $pass

cd httpdocs/images/heatwaves/2023
put anim_MHW_days_Jan.gif

quit 

END_SCRIPT







