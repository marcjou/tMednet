import calendar
import mysql.connector
from mysql.connector import Error
from datetime import datetime

HEADER = '<div class="row">\n<div class="col-lg-4 col-sm-4" style="border: 1px solid grey;"><a style="display: block;" href="index.php?option=com_content&amp;view=article&amp;layout=aterkia:article&amp;id=279">2023</a></div>\n<div class="col-lg-4 col-sm-4" style="border: 1px solid grey;"><a style="display: block;" href="index.php?option=com_content&amp;view=article&amp;layout=aterkia:article&amp;id=278">2022</a></div>\n<div class="col-lg-4 col-sm-4" style="border: 1px solid grey;"><a style="display: block;" href="index.php?option=com_content&amp;view=article&amp;layout=aterkia:article&amp;id=206">2020</a></div>\n<div class="col-lg-4 col-sm-4" style="border: 1px solid grey;"><a style="display: block;" href="index.php?option=com_content&amp;view=article&amp;layout=aterkia:article&amp;id=175">2019</a></div>\n</div>\n<p> </p>\n<p>Marc - Welcome to T-MEDNet Marine Heatwave Tracker at 4 km in Near Real Time.</p>\n<p>Powered by @nat_bensoussan &amp; ICM-CSIC.</p>'
FOOTER = '<h2>FOR MORE INFORMATION</h2>\n<p>Extreme warming events known as Marine Heatwaves (MHW) have increased in frequency and magnitude worldwide, with harmful impacts on coastal ecosystems and human activities (e.g. Frolicher <em>et al.</em>, 2018; Oliver <em>et al.</em>, 2018; Smale <em>et al.</em>, 2019). In the Mediterranean Sea, the rapid sea surface warming trend has been associated to strong increase in Marine Heatwave days, particularily during the past two decades (<a href="http://marine.copernicus.eu/3rd-ocean-state-report-now-available/" target="_blank" rel="noopener noreferrer">OSR#3 summary</a>, Bensoussan <em>et al.</em>, 2019ab). </p>\n<p>From May to current date, large scale Marine Heatwaves have occurred in the Mediterranean Sea with anomalies &gt;5°C locally. This page is intended to share updated information with Mediterranean Marine Protected Areas managers, marine stakeholders and the general interested public.</p>\n<p> Given the need for high-resolution information over the Mediterranean basin and coastal zone, satellite derived Sea Surface Temperature (SST) has been evaluated to track Mediterranean Marine Heatwaves in Near Real Time (NRT). A multi-products approach has been set up, in which NRT Optimally Interpolated daily SST maps from CMEMS are compared to long-term statistics calculated over the 1982-2011 period at 4 Km horizontal resolution. Marine Heatwave events characterization has been conducted using the approach outlined in Hobday<em>et al.</em> (2016, 2018) to evaluate their duration, intensity and allow comparison across spatial and temporal scales (e.g. <a href="http://www.marineheatwaves.org/tracker.html" target="_blank" rel="noopener noreferrer">www.marineheatwaves.org/tracker.html</a>). All figures were generated using E.U Copernicus Marine Service Information. Powered by @nat_bensoussan.</p>\n<p> </p>\n'


TODAY = datetime.today().strftime('%d/%m/%Y')
MONTH_ABBR = calendar.month_abbr[datetime.today().month]
YEAR = datetime.today().year

MHW_MAPS = '<h2>MHW MAPS in NRT</h2>\n<p>Started in May - last update {}</p>\n<div class="row-fluid">\n<div class="span6"><img style="display: block; margin-left: auto; margin-right: auto;" src="images/heatwaves/' + str(YEAR) + '/anim_MHW_days_{}.gif" width="550" height="349" /></div>\n<div class="span6"><img style="display: block; margin-left: auto; margin-right: auto;" src="images/heatwaves/' + str(YEAR) + '/anim_MHW_imax_{}.gif" width="550" height="349" /></div><div class="span6"><img style="display: block; margin-left: auto; margin-right: auto;" src="images/heatwaves/2022/anim_SST_{}.gif" width="550" height="349" /></div>\n<div class="span6"><img style="display: block; margin-left: auto; margin-right: auto;" src="images/heatwaves/' + str(YEAR) + '/anim_SST_{}.gif" width="550" height="349" /></div>\n'.format(TODAY, MONTH_ABBR, MONTH_ABBR, MONTH_ABBR, MONTH_ABBR)
MONTHLY = '<h2>MONTHLY MAPS</h2>\n<div class="row-fluid">\n{}</div>\n<p> </p>'

OLD_DISPLAYS = '<div class="span6"><img style="display: block; margin-left: auto; margin-right: auto;" src="images/heatwaves/' + str(YEAR) + '/anim_days_{}.gif" width="550" height="349" /></div>\n<div class="span6"><img style="display: block; margin-left: auto; margin-right: auto;" src="images/heatwaves/' + str(YEAR) + '/anim_imax_{}.gif" width="550" height="349" /></div>\n'

str=''
for i in range(1, datetime.today().month):
    str=str + OLD_DISPLAYS.format(calendar.month_abbr[i], calendar.month_abbr[i])

MONTHLY = MONTHLY.format(str)


try:
    connection = mysql.connector.connect(host='86.109.170.198',
                                         database='tmednetj382',
                                         user='tmednetj382',
                                         password='$eE%q0l32')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)

except Error as e:
    print("Error while connecting to MySQL", e)
"""finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")"""

