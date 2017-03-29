@echo off
rem USAGE:
rem cindy_op.bat prj ip (77, 80-sm1, 189-sm5)

SET P_PRJ=%1
SET P_IP=%2
SET P_PATH=D:\app\tasks

SET P_TB=IoT_WiFi_MappingTable
SET P_TB1=IoT_Store_Management
SET P_TB2=IoT_WiFi_StoreFunnelHourly
SET P_TB3=IoT_WiFi_StoreFunnelDaily
SET P_TB4=IoT_WiFi_DailyAggregate
SET P_TB5=IoT_WiFi_HourlyAggregate

SET P_DB=WMAX_List_%P_PRJ%
SET P_FILE1=%P_PATH%\data\%P_PRJ%_%P_TB1%.txt
SET P_FILE2=%P_PATH%\data\%P_PRJ%_%P_TB2%.txt

rem SET FILE=%1
rem SET DB=%3
rem SET TB=%4

date /T
time /T

echo "===== Start dumping table %P_IP%.%P_DB%.%P_TB2% ====="
rem STEP1 export data from mssql
bcp dbo.%P_TB1% out "%P_FILE1%" -T -S "%P_IP%" -d "%P_DB%" -w -b5000 -t,
bcp dbo.%P_TB2% out "%P_FILE2%" -T -S "%P_IP%" -d "%P_DB%" -w -b5000 -t,

rem STEP2 zip file
D:\app\7z\7za a -tzip "%P_FILE1%.zip" "%P_FILE1%"
D:\app\7z\7za a -tzip "%P_FILE2%.zip" "%P_FILE2%"

rem STEP3 scp to linux
D:\app\putty\pscp -i "key.ppk" "%P_FILE1%.zip" user@hostname:/home/user/dir/
D:\app\putty\pscp -i "key.ppk" "%P_FILE2%.zip" user@hostname:/home/user/dir/


del "%P_FILE1%.zip"
del "%P_FILE2%.zip"
del "%P_FILE1%"
del "%P_FILE2%"


echo "===== End dumping =========="
